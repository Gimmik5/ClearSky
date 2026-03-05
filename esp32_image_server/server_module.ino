/*
 * Server Module - V1.1 PULL Mode with SD Queue Support
 * 
 * FIXED: Uses manual URI parsing instead of UriRegex (better compatibility)
 * 
 * Existing endpoints:
 *   /          - Server info page
 *   /capture   - Capture and return live image
 *   /status    - JSON system status
 * 
 * New V1.1 endpoints:
 *   /queue                 - JSON list of queued images (oldest first)
 *   /queue/<filename>      - Serve a specific queued image
 *   /queue/delete/<filename> - Delete a queued image (after Python fetches it)
 */

#include "globals.h"

// Web server instance
WebServer server(ESP32_SERVER_PORT);

// Server statistics
unsigned long captureCount = 0;
unsigned long lastCaptureMs = 0;

// Track if Python is actively polling (for SD fallback decision)
unsigned long lastSuccessfulPoll = 0;
#define POLL_TIMEOUT_MS 60000  // Consider poller dead after 60s of no polls

// ===== SERVER INITIALIZATION =====

void initServer() {
  #if USE_PULL_MODE
    // Existing endpoints
    server.on("/", handleRoot);
    server.on("/capture", handleCapture);
    server.on("/status", handleStatus);
    
    // V1.1 SD queue endpoints - using onNotFound to handle dynamic URIs
    server.on("/queue", HTTP_GET, handleQueueList);
    
    // V1.1 SD browser endpoints
    #if ENABLE_SD_CARD
      server.on("/sd/list", HTTP_GET, handleSDList);
      server.on("/sd/browse", HTTP_GET, handleSDBrowse);
      server.on("/sd/stats", HTTP_GET, handleSDStats);
    #endif
    
    // V1.1 Control endpoints
    server.on("/control/pause", HTTP_POST, handleControlPause);
    server.on("/control/pause", HTTP_GET, handleControlPause);  // Allow GET too
    server.on("/control/resume", HTTP_POST, handleControlResume);
    server.on("/control/resume", HTTP_GET, handleControlResume);
    server.on("/control/capture", HTTP_POST, handleControlCapture);
    server.on("/control/capture", HTTP_GET, handleControlCapture);
    server.on("/control/status", HTTP_GET, handleControlStatus);
    
    // Dynamic URIs handled in onNotFound
    server.onNotFound(handleNotFound);
    
    server.begin();
    
    #if ENABLE_SERIAL_OUTPUT
      Serial.println("\n[SERVER] Web Server Started (V1.1)");
      printServerInfo();
    #endif
  #endif
}

void handleServerClients() {
  #if USE_PULL_MODE
    server.handleClient();
  #endif
}

void printServerInfo() {
  #if ENABLE_SERIAL_OUTPUT && USE_PULL_MODE
    Serial.println("  Endpoints:");
    Serial.printf("    http://%s/          - Server info\n", WiFi.localIP().toString().c_str());
    Serial.printf("    http://%s/capture   - Live capture\n", WiFi.localIP().toString().c_str());
    Serial.printf("    http://%s/status    - System status\n", WiFi.localIP().toString().c_str());
    #if ENABLE_SD_CARD
      Serial.printf("    http://%s/queue     - SD queue list\n", WiFi.localIP().toString().c_str());
    #endif
  #endif
}

// ===== EXISTING HTTP HANDLERS =====

void handleRoot() {
  String html = "<!DOCTYPE html><html><head>";
  html += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
  html += "<style>";
  html += "body{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}";
  html += ".card{background:white;border-radius:8px;padding:20px;margin-bottom:20px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}";
  html += "h1{color:#333;margin-bottom:10px}";
  html += ".status{padding:15px;border-radius:5px;margin:15px 0}";
  html += ".status.running{background:#d4edda;border:1px solid #c3e6cb;color:#155724}";
  html += ".status.paused{background:#fff3cd;border:1px solid #ffeaa7;color:#856404}";
  html += ".btn{padding:10px 20px;border:none;border-radius:5px;cursor:pointer;font-size:1em;margin:5px}";
  html += ".btn-success{background:#28a745;color:white}";
  html += ".btn-warning{background:#ffc107;color:black}";
  html += ".btn-primary{background:#007bff;color:white}";
  html += ".btn:hover{opacity:0.8}";
  html += "</style></head><body>";
  
  html += "<div class=\"card\">";
  html += "<h1>ESP32-CAM Image Server V1.1</h1>";
  
  // Status indicator
  if (systemPaused) {
    html += "<div class=\"status paused\">⏸️ PAUSED</div>";
  } else {
    html += "<div class=\"status running\">▶️ RUNNING</div>";
  }
  
  html += "<p><strong>IP:</strong> " + WiFi.localIP().toString() + "</p>";
  html += "<p><strong>Captures:</strong> " + String(captureCount) + "</p>";
  
  #if ENABLE_SD_CARD
    if (sdCardAvailable) {
      html += "<p><strong>SD Queue:</strong> " + String(sdQueueCount) + " images</p>";
      html += "<p><strong>SD Usage:</strong> " + String(getSDUsagePercent()) + "%</p>";
    } else {
      html += "<p><strong>SD Card:</strong> Not available</p>";
    }
  #endif
  
  html += "</div>";
  
  // Control panel
  html += "<div class=\"card\">";
  html += "<h2>Control Panel</h2>";
  
  if (systemPaused) {
    html += "<button class=\"btn btn-success\" onclick=\"fetch('/control/resume').then(()=>location.reload())\">▶️ Resume</button>";
  } else {
    html += "<button class=\"btn btn-warning\" onclick=\"fetch('/control/pause').then(()=>location.reload())\">⏸️ Pause</button>";
  }
  
  html += "<button class=\"btn btn-primary\" onclick=\"fetch('/control/capture')\">📷 Capture Now</button>";
  html += "</div>";
  
  // Endpoints
  html += "<div class=\"card\">";
  html += "<h3>Endpoints:</h3>";
  html += "<ul>";
  html += "<li><a href='/capture'>/capture</a> - Live capture (JPEG)</li>";
  html += "<li><a href='/status'>/status</a> - JSON status</li>";
  html += "<li><a href='/control/status'>/control/status</a> - Control status (JSON)</li>";
  
  #if ENABLE_SD_CARD
    html += "<li><a href='/queue'>/queue</a> - SD queue list (JSON)</li>";
    html += "<li><a href='/sd/browse'>/sd/browse</a> - SD card browser</li>";
  #endif
  
  html += "</ul>";
  html += "</div>";
  
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleCapture() {
  /*
   * Live image capture.
   * 
   * V1.1 change: If Python hasn't polled in POLL_TIMEOUT_MS,
   * assume poller is down and save to SD as backup.
   */
  unsigned long startTime = millis();
  
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    debugPrint("[CAPTURE] Request received");
  #endif
  
  blinkCapture();
  
  camera_fb_t* fb = captureImageWithRetry();
  
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    blinkError();
    return;
  }
  
  // Record successful poll
  lastSuccessfulPoll = millis();
  resetPollerActivity();  // Reset auto-capture mode
  
  captureCount++;
  lastCaptureMs = millis() - startTime;
  
  // Send image as JPEG
  server.setContentLength(fb->len);
  server.send(200, "image/jpeg", "");
  WiFiClient client = server.client();
  client.write(fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
  blinkSuccess();
  
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    debugPrintf("[SUCCESS] Sent %u bytes in %lums", fb->len, lastCaptureMs);
  #endif
}

void handleStatus() {
  // Record successful poll
  lastSuccessfulPoll = millis();
  resetPollerActivity();  // Reset auto-capture mode
  
  String json = "{";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"uptime\":" + String(millis() / 1000) + ",";
  json += "\"captures\":" + String(captureCount) + ",";
  json += "\"lastCaptureMs\":" + String(lastCaptureMs) + ",";
  json += "\"freeHeap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"wifi_rssi\":" + String(WiFi.RSSI());
  
  #if ENABLE_SD_CARD
    json += ",\"sd_available\":" + String(sdCardAvailable ? "true" : "false");
    if (sdCardAvailable) {
      json += ",\"sd_queue_count\":" + String(sdQueueCount);
      json += ",\"sd_usage_percent\":" + String(getSDUsagePercent());
    }
  #endif
  
  json += "}";
  
  server.send(200, "application/json", json);
}

void handleNotFound() {
  /*
   * FIXED: Handle dynamic URIs manually instead of using UriRegex
   * Checks for /queue/<filename>, /queue/delete/<filename>,
   * /sd/file/<path>, and /sd/delete/<path> patterns
   */
  String uri = server.uri();
  
  #if ENABLE_SD_CARD
    // Handle /queue/delete/<filename>
    if (uri.startsWith("/queue/delete/")) {
      handleQueueDelete();
      return;
    }
    // Handle /queue/<filename>
    else if (uri.startsWith("/queue/") && uri.length() > 7) {
      handleQueueServe();
      return;
    }
    // Handle /sd/file/<path>
    else if (uri.startsWith("/sd/file/")) {
      handleSDFile();
      return;
    }
    // Handle /sd/delete/<path>
    else if (uri.startsWith("/sd/delete/")) {
      handleSDDelete();
      return;
    }
  #endif
  
  // Actually not found
  server.send(404, "text/plain", "Not Found");
}

// ===== V1.1 SD QUEUE HANDLERS =====

void handleQueueList() {
  /*
   * GET /queue
   * Returns JSON array of queued image filenames (oldest first).
   * 
   * Response: ["20260212_143022.jpg", "20260212_143122.jpg", ...]
   */
  #if !ENABLE_SD_CARD
    server.send(503, "application/json", "{\"error\":\"SD card disabled\"}");
    return;
  #endif
  
  if (!sdCardAvailable) {
    server.send(503, "application/json", "{\"error\":\"SD card not available\"}");
    return;
  }
  
  std::vector<String> files;
  getQueuedImageList(files);
  
  String json = "[";
  for (size_t i = 0; i < files.size(); i++) {
    if (i > 0) json += ",";
    json += "\"" + files[i] + "\"";
  }
  json += "]";
  
  debugPrintf("[QUEUE] List requested - %d images", files.size());
  server.send(200, "application/json", json);
}

void handleQueueServe() {
  /*
   * GET /queue/<filename>
   * Serve a specific queued image.
   * 
   * Example: GET /queue/20260212_143022.jpg
   */
  #if !ENABLE_SD_CARD
    server.send(503, "text/plain", "SD card disabled");
    return;
  #endif
  
  if (!sdCardAvailable) {
    server.send(503, "text/plain", "SD card not available");
    return;
  }
  
  // Extract filename from URI (remove /queue/ prefix)
  String uri = server.uri();
  String filename = uri.substring(7);  // Skip "/queue/"
  
  // Security check: ensure filename doesn't contain path separators
  if (filename.indexOf('/') >= 0 || filename.indexOf('\\') >= 0) {
    server.send(400, "text/plain", "Invalid filename");
    return;
  }
  
  size_t imageSize = 0;
  uint8_t* imageData = readImageFromSD(filename, imageSize);
  
  if (!imageData || imageSize == 0) {
    server.send(404, "text/plain", "Image not found on SD card");
    return;
  }
  
  // Send image
  server.setContentLength(imageSize);
  server.send(200, "image/jpeg", "");
  WiFiClient client = server.client();
  client.write(imageData, imageSize);
  
  free(imageData);
  
  debugPrintf("[QUEUE] Served: %s (%u bytes)", filename.c_str(), imageSize);
}

void handleQueueDelete() {
  /*
   * GET /queue/delete/<filename>
   * Delete a queued image after Python successfully fetches it.
   * 
   * Example: GET /queue/delete/20260212_143022.jpg
   * Response: {"deleted": true} or {"deleted": false}
   */
  #if !ENABLE_SD_CARD
    server.send(503, "application/json", "{\"error\":\"SD card disabled\"}");
    return;
  #endif
  
  if (!sdCardAvailable) {
    server.send(503, "application/json", "{\"error\":\"SD card not available\"}");
    return;
  }
  
  // Extract filename from URI (remove /queue/delete/ prefix)
  String uri = server.uri();
  String filename = uri.substring(14);  // Skip "/queue/delete/"
  
  // Security check: ensure filename doesn't contain path separators
  if (filename.indexOf('/') >= 0 || filename.indexOf('\\') >= 0) {
    server.send(400, "application/json", "{\"error\":\"Invalid filename\"}");
    return;
  }
  
  bool deleted = deleteImageFromSD(filename);
  
  String json = "{\"deleted\":" + String(deleted ? "true" : "false") + "}";
  server.send(200, "application/json", json);
}

// ===== HELPER: Check if poller appears dead =====

bool isPollerActive() {
  /*
   * Returns true if Python has polled in the last POLL_TIMEOUT_MS.
   * Used to decide whether to save to SD as backup.
   */
  return (millis() - lastSuccessfulPoll) < POLL_TIMEOUT_MS;
}

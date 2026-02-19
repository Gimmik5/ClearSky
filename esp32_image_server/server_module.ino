/*
 * Server Module (Pull Mode)
 * ESP32 acts as HTTP server, Python fetches images on demand
 */

#include "globals.h"

// Web server instance
WebServer server(ESP32_SERVER_PORT);

// Server statistics
unsigned long captureCount = 0;
unsigned long lastCaptureMs = 0;

// ===== SERVER INITIALIZATION =====

void initServer() {
  #if USE_PULL_MODE
    server.on("/", handleRoot);
    server.on("/capture", handleCapture);
    server.on("/status", handleStatus);
    server.onNotFound(handleNotFound);
    
    server.begin();
    
    #if ENABLE_SERIAL_OUTPUT
      Serial.println("\n[SERVER] Web Server Started");
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
    Serial.printf("    http://%s/capture   - Capture image\n", WiFi.localIP().toString().c_str());
    Serial.printf("    http://%s/status    - System status\n", WiFi.localIP().toString().c_str());
  #endif
}

// ===== HTTP HANDLERS =====

void handleRoot() {
  String html = "<html><body>";
  html += "<h1>ESP32-CAM Image Server</h1>";
  html += "<p>Status: Running</p>";
  html += "<p>IP: " + WiFi.localIP().toString() + "</p>";
  html += "<p>Captures: " + String(captureCount) + "</p>";
  html += "<hr>";
  html += "<h3>Endpoints:</h3>";
  html += "<ul>";
  html += "<li><a href='/capture'>/capture</a> - Capture new image (JPEG)</li>";
  html += "<li><a href='/status'>/status</a> - JSON status</li>";
  html += "</ul>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleCapture() {
  unsigned long startTime = millis();
  
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    Serial.println("[CAPTURE] Request received");
  #endif
  
  blinkCapture();
  
  camera_fb_t* fb = captureImageWithRetry();
  
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    blinkError();
    return;
  }
  
  captureCount++;
  lastCaptureMs = millis() - startTime;
  
  // Send image as JPEG binary data
  server.setContentLength(fb->len);
  server.send(200, "image/jpeg", "");
  WiFiClient client = server.client();
  client.write(fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
  blinkSuccess();
  
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    Serial.printf("[SUCCESS] Sent image (%d bytes) in %lums\n", fb->len, lastCaptureMs);
  #endif
}

void handleStatus() {
  String json = "{";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"uptime\":" + String(millis() / 1000) + ",";
  json += "\"captures\":" + String(captureCount) + ",";
  json += "\"lastCaptureMs\":" + String(lastCaptureMs) + ",";
  json += "\"freeHeap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"rssi\":" + String(WiFi.RSSI());
  json += "}";
  
  server.send(200, "application/json", json);
}

void handleNotFound() {
  server.send(404, "text/plain", "Not Found");
}

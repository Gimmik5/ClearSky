/*
 * Web Server Module
 * 
 * This module provides:
 * - Live image viewing through a web browser
 * - Pause/Resume control via web interface
 * - Current status display
 * 
 * Access at: http://[ESP32_IP_ADDRESS]
 * NO #include statements needed here - the main file handles that.
 */

// ===== WEB SERVER SETUP =====
void setupWebServer() {
  // Start the web server on port 80
  server.on("/", HTTP_GET, handleRoot);
  server.on("/capture", HTTP_GET, handleCapture);
  server.on("/pause", HTTP_GET, handlePause);
  server.on("/resume", HTTP_GET, handleResume);
  server.on("/status", HTTP_GET, handleStatus);
  
  server.begin();
  Serial.println("Web server started!");
  Serial.print("Access at: http://");
  Serial.println(WiFi.localIP());
}

// ===== ROOT PAGE - MAIN INTERFACE =====
void handleRoot() {
  String html = "<!DOCTYPE html><html><head>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<style>";
  html += "body { font-family: Arial; margin: 20px; background: #f0f0f0; }";
  html += ".container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }";
  html += "h1 { color: #333; }";
  html += "img { max-width: 100%; border: 2px solid #333; border-radius: 5px; }";
  html += "button { padding: 10px 20px; margin: 5px; font-size: 16px; cursor: pointer; border-radius: 5px; border: none; }";
  html += ".pause { background: #ff9800; color: white; }";
  html += ".resume { background: #4CAF50; color: white; }";
  html += ".capture { background: #2196F3; color: white; }";
  html += ".status { padding: 10px; background: #e3f2fd; border-radius: 5px; margin: 10px 0; }";
  html += "</style>";
  html += "</head><body>";
  html += "<div class='container'>";
  html += "<h1>📷 ESP32-CAM Sky Predictor</h1>";
  
  // Status display
  html += "<div class='status'>";
  html += "<strong>Status:</strong> ";
  html += systemPaused ? "⏸️ PAUSED" : "▶️ RUNNING";
  html += "</div>";
  
  // Control buttons
  html += "<div>";
  if (systemPaused) {
    html += "<button class='resume' onclick='location.href=\"/resume\"'>▶️ Resume</button>";
  } else {
    html += "<button class='pause' onclick='location.href=\"/pause\"'>⏸️ Pause</button>";
  }
  html += "<button class='capture' onclick='location.href=\"/capture\"'>📸 Capture Now</button>";
  html += "</div>";
  
  // Image display with auto-refresh
  html += "<h2>Latest Image:</h2>";
  html += "<img id='liveImage' src='/capture' />";
  html += "<p><small>Image refreshes every ";
  html += String(captureIntervalMs / 1000);
  html += " seconds when running</small></p>";
  
  // Auto-refresh script
  html += "<script>";
  html += "setInterval(function() {";
  html += "  if (!" + String(systemPaused ? "true" : "false") + ") {";
  html += "    document.getElementById('liveImage').src = '/capture?t=' + new Date().getTime();";
  html += "  }";
  html += "}, " + String(captureIntervalMs) + ");";
  html += "</script>";
  
  html += "</div></body></html>";
  
  server.send(200, "text/html", html);
}

// ===== CAPTURE AND SEND IMAGE =====
void handleCapture() {
  // Capture a new image
  camera_fb_t * fb = esp_camera_fb_get();
  
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }
  
  // Send the JPEG image
  server.sendHeader("Content-Disposition", "inline; filename=capture.jpg");
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
  
  // Release the frame buffer
  esp_camera_fb_return(fb);
}

// ===== PAUSE FUNCTIONALITY =====
void handlePause() {
  systemPaused = true;
  Serial.println("⏸️ System PAUSED via web interface");
  
  String html = "<!DOCTYPE html><html><head>";
  html += "<meta http-equiv='refresh' content='2;url=/'>";
  html += "</head><body>";
  html += "<h2>⏸️ System Paused</h2>";
  html += "<p>Redirecting...</p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

// ===== RESUME FUNCTIONALITY =====
void handleResume() {
  systemPaused = false;
  Serial.println("▶️ System RESUMED via web interface");
  
  String html = "<!DOCTYPE html><html><head>";
  html += "<meta http-equiv='refresh' content='2;url=/'>";
  html += "</head><body>";
  html += "<h2>▶️ System Resumed</h2>";
  html += "<p>Redirecting...</p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

// ===== STATUS API ENDPOINT =====
void handleStatus() {
  String json = "{";
  json += "\"paused\":" + String(systemPaused ? "true" : "false") + ",";
  json += "\"interval\":" + String(captureIntervalMs) + ",";
  json += "\"uptime\":" + String(millis());
  json += "}";
  
  server.send(200, "application/json", json);
}

/*
 * ===== WEB SERVER FEATURES =====
 * 
 * Main Page (http://[ESP32_IP]):
 * - Shows current system status (running/paused)
 * - Displays latest captured image
 * - Auto-refreshes image when system is running
 * - Pause/Resume buttons
 * - Manual capture button
 * 
 * Endpoints:
 * - /         : Main interface
 * - /capture  : Get current camera image (JPEG)
 * - /pause    : Pause the system
 * - /resume   : Resume the system
 * - /status   : Get JSON status
 * 
 * Usage:
 * 1. Connect ESP32 to WiFi (configure in main file)
 * 2. Note the IP address in Serial Monitor
 * 3. Open http://[IP_ADDRESS] in your browser
 * 4. Control and view images from any device on the network
 * 
 * Mobile-friendly:
 * - Responsive design works on phones and tablets
 * - Touch-friendly buttons
 * - Images scale to screen size
 */
/*
 * Control Module (V1.1)
 * 
 * Web-based system control endpoints
 * 
 * Endpoints:
 *   POST /control/pause     - Pause automatic captures
 *   POST /control/resume    - Resume automatic captures  
 *   POST /control/capture   - Manual capture now
 *   GET  /control/status    - Get system status (JSON)
 */

#include "globals.h"

void handleControlPause() {
  systemPaused = true;
  
  String json = "{\"success\":true,\"paused\":true,\"message\":\"System paused\"}";
  server.send(200, "application/json", json);
  
  debugPrint("[CONTROL] System paused via web");
}

void handleControlResume() {
  systemPaused = false;
  
  String json = "{\"success\":true,\"paused\":false,\"message\":\"System resumed\"}";
  server.send(200, "application/json", json);
  
  debugPrint("[CONTROL] System resumed via web");
}

void handleControlCapture() {
  /*
   * Manual capture trigger
   * Useful when system is paused
   */
  debugPrint("[CONTROL] Manual capture requested");
  
  camera_fb_t* fb = captureImageWithRetry();
  
  if (!fb) {
    String json = "{\"success\":false,\"message\":\"Camera capture failed\"}";
    server.send(500, "application/json", json);
    blinkError();
    return;
  }
  
  // If SD available and system paused, save to SD
  #if ENABLE_SD_CARD
    if (systemPaused && sdCardAvailable) {
      String timestamp = getTimestamp();
      String path = saveImageToSD(fb, timestamp);
      
      esp_camera_fb_return(fb);
      
      if (!path.isEmpty()) {
        String json = "{\"success\":true,\"message\":\"Saved to SD\",\"filename\":\"" + timestamp + ".jpg\"}";
        server.send(200, "application/json", json);
        blinkSuccess();
      } else {
        String json = "{\"success\":false,\"message\":\"SD save failed\"}";
        server.send(500, "application/json", json);
        blinkError();
      }
      return;
    }
  #endif
  
  // Return image directly
  server.setContentLength(fb->len);
  server.send(200, "image/jpeg", "");
  WiFiClient client = server.client();
  client.write(fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
  blinkSuccess();
}

void handleControlStatus() {
  /*
   * System status for control panel
   */
  String json = "{";
  json += "\"paused\":" + String(systemPaused ? "true" : "false") + ",";
  json += "\"uptime\":" + String(millis() / 1000) + ",";
  json += "\"free_heap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"wifi_rssi\":" + String(WiFi.RSSI()) + ",";
  json += "\"captures\":" + String(captureCount);
  
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

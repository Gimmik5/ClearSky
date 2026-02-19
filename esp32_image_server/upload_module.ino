/*
 * Upload Module
 * Handles image capture workflow and HTTP upload to server
 */

#include "globals.h"

// ===== CAPTURE AND SEND WORKFLOW =====

void captureAndSend() {
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    Serial.println("----------------------------------------");
    Serial.println("[CAPTURE] Capturing image...");
  #endif
  
  blinkCapture();
  
  camera_fb_t* fb = captureImageWithRetry();
  if (!fb) {
    return;
  }
  
  if (!checkWiFiConnection()) {
    reconnectWiFi();
  }
  
  if (checkWiFiConnection()) {
    bool success = uploadImage(fb);
    if (success) {
      blinkSuccess();
    } else {
      blinkError();
    }
  } else {
    debugPrint("[ERROR] No WiFi connection");
  }
  
  esp_camera_fb_return(fb);
  
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    Serial.printf("Next capture in %d seconds\n", captureInterval / 1000);
    Serial.println("----------------------------------------\n");
  #endif
}

// ===== IMAGE UPLOAD =====

bool uploadImage(camera_fb_t* fb) {
  HTTPClient http;
  http.setTimeout(HTTP_TIMEOUT_MS);
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "image/jpeg");
  
  bool success = sendHTTPRequest(&http, fb);
  
  http.end();
  return success;
}

bool sendHTTPRequest(HTTPClient* http, camera_fb_t* fb) {
  int httpCode = http->POST(fb->buf, fb->len);
  
  if (httpCode == 200) {
    uploadFailCount = 0;
    String response = http->getString();
    handleUploadSuccess(response);
    return true;
  } else {
    uploadFailCount++;
    handleUploadFailure(httpCode);
    
    // Retry logic
    if (uploadFailCount < MAX_UPLOAD_RETRIES) {
      delay(RETRY_DELAY_MS);
      debugPrint("Retrying upload...");
      
      http->end();
      http->begin(SERVER_URL);
      http->addHeader("Content-Type", "image/jpeg");
      httpCode = http->POST(fb->buf, fb->len);
      
      if (httpCode == 200) {
        uploadFailCount = 0;
        debugPrint("[SUCCESS] Retry successful");
        return true;
      }
    }
    return false;
  }
}

// ===== UPLOAD RESPONSE HANDLERS =====

void handleUploadSuccess(String response) {
  debugPrint("[SUCCESS] Sent to server");
  
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    if (response.length() > 0) {
      Serial.println("\nServer analysis:");
      Serial.println(response);
    }
  #endif
}

void handleUploadFailure(int httpCode) {
  debugPrintf("[ERROR] Upload failed: HTTP %d", httpCode);
  debugPrintf("  Fail count: %d", uploadFailCount);
}

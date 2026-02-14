/*
 * Upload Module - With SD Card Integration
 * 
 * Drop-in replacement for upload_module.ino once SD card is integrated.
 * Saves image to SD card before upload, logs result, runs cleanup.
 * 
 * Changes from upload_module.ino:
 *   - captureAndSend() saves to SD before uploading
 *   - captureAndSend() logs result to CSV after upload
 *   - captureAndSend() runs auto-cleanup after logging
 *   - uploadImage() and sendHTTPRequest() unchanged
 *   - handleUploadSuccess() and handleUploadFailure() unchanged
 */

#include "globals.h"

// ===== CAPTURE AND SEND WORKFLOW =====

void captureAndSend() {
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    Serial.println("----------------------------------------");
    Serial.println("📷 Capturing image...");
  #endif

  blinkCapture();

  camera_fb_t* fb = captureImageWithRetry();
  if (!fb) {
    return;
  }

  // Save to SD card before attempting upload
  #if SD_CARD_ENABLE
    if (sdIsAvailable()) {
      String filename = generateImageFilename();
      saveImageToSD(fb, filename.c_str());
    }
  #endif

  // Upload to server
  bool uploadSuccess = false;
  if (!checkWiFiConnection()) {
    reconnectWiFi();
  }

  if (checkWiFiConnection()) {
    uploadSuccess = uploadImage(fb);
    if (uploadSuccess) {
      blinkSuccess();
    } else {
      blinkError();
    }
  } else {
    debugPrint("x No WiFi - image saved to SD only");
  }

  // Log capture result to CSV
  #if SD_CARD_ENABLE
    char timestamp[32];
    snprintf(timestamp, sizeof(timestamp), "%lu", millis());
    logCaptureToSD(timestamp, fb->len, uploadSuccess);

    // Run auto-cleanup if storage limits reached
    cleanupOldImages();
  #endif

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
        debugPrint("✔ Retry successful");
        return true;
      }
    }
    return false;
  }
}

// ===== UPLOAD RESPONSE HANDLERS =====

void handleUploadSuccess(String response) {
  debugPrint("✔ Sent to server");

  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    if (response.length() > 0) {
      Serial.println("\nServer analysis:");
      Serial.println(response);
    }
  #endif
}

void handleUploadFailure(int httpCode) {
  debugPrintf("x Upload failed: HTTP %d", httpCode);
  debugPrintf("  Fail count: %d", uploadFailCount);
}

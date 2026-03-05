/*
 * Auto-Capture Module (V1.1)
 * 
 * Monitors poller activity and automatically captures to SD when inactive.
 * 
 * Logic:
 *   - Track last successful poll via /capture or /status requests
 *   - If no poll for POLL_TIMEOUT_MS (60s), assume poller is down
 *   - Auto-capture to SD every FALLBACK_INTERVAL_MS (default: 10s)
 *   - Resume normal operation when poller returns
 */

#include "globals.h"

// Auto-capture state
unsigned long lastAutoCaptureTime = 0;

// Intervals (from ESP32_Config.h or defaults)
#ifndef FALLBACK_CAPTURE_INTERVAL_MS
  #define FALLBACK_CAPTURE_INTERVAL_MS 10000  // 10 seconds
#endif

#ifndef POLL_TIMEOUT_MS
  #define POLL_TIMEOUT_MS 60000  // 60 seconds
#endif

void checkAutoCapture() {
  /*
   * Called from main loop().
   * 
   * If poller hasn't been active for POLL_TIMEOUT_MS,
   * automatically capture to SD every FALLBACK_INTERVAL_MS.
   */
  
  #if !ENABLE_SD_CARD
    return;  // SD disabled, skip auto-capture
  #endif
  
  if (!sdCardAvailable) {
    return;  // SD not working, skip
  }
  
  // Check if poller is active (has polled within timeout window)
  unsigned long now = millis();
  bool pollerActive = (now - lastSuccessfulPoll) < POLL_TIMEOUT_MS;
  
  if (pollerActive) {
    // Poller is active, no need for auto-capture
    return;
  }
  
  // Poller appears dead - check if it's time to auto-capture
  if ((now - lastAutoCaptureTime) >= FALLBACK_CAPTURE_INTERVAL_MS) {
    
    #if ENABLE_SERIAL_OUTPUT
      if (lastAutoCaptureTime == 0) {
        // First time detecting dead poller
        debugPrint("[AUTO] Poller inactive - switching to SD auto-capture mode");
      }
    #endif
    
    performAutoCapture();
    lastAutoCaptureTime = now;
  }
}

void performAutoCapture() {
  /*
   * Capture image and save to SD card.
   * Called automatically when poller is inactive.
   */
  
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    debugPrint("[AUTO] Capturing to SD...");
  #endif
  
  blinkCapture();
  
  camera_fb_t* fb = captureImageWithRetry();
  
  if (!fb) {
    debugPrint("[AUTO] Capture failed");
    blinkError();
    return;
  }
  
  // Get timestamp
  String timestamp = getTimestamp();
  
  // Save to SD
  String path = saveImageToSD(fb, timestamp);
  
  esp_camera_fb_return(fb);
  
  if (!path.isEmpty()) {
    blinkSuccess();
    #if ENABLE_SERIAL_OUTPUT
      debugPrintf("[AUTO] Saved to SD: %s.jpg", timestamp.c_str());
    #endif
  } else {
    blinkError();
    debugPrint("[AUTO] SD save failed");
  }
}

void resetPollerActivity() {
  /*
   * Called when poller becomes active again.
   * Resets auto-capture tracking.
   */
  if (lastAutoCaptureTime > 0) {
    debugPrint("[AUTO] Poller active - resuming normal operation");
    lastAutoCaptureTime = 0;
  }
}

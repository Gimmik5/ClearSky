/*
 * ESP32-CAM Image Server/Sender
 * Main sketch file - supports both Push and Pull modes
 * 
 * CONFIGURATION:
 * - Edit ESP32_Config.h to configure all settings
 * - Set USE_PULL_MODE true for server mode (Python fetches)
 * - Set USE_PULL_MODE false for sender mode (ESP32 pushes)
 * 
 * PULL MODE: ESP32 acts as HTTP server, Python requests images
 * PUSH MODE: ESP32 captures and uploads images to Python server
 */

#include "esp_camera.h"
#include "WiFi.h"
#include "HTTPClient.h"
#include "WebServer.h"
#include "ESP32_Config.h"
#include "globals.h"

#if ENABLE_WATCHDOG
  #include "esp_task_wdt.h"
#endif

// ===== SETUP =====
void setup() {
  initSystem();
  initLED();
  initWatchdog();
  
  // Initialize camera
  if (!initCamera()) {
    debugPrint("âœ— Camera init failed - halting");
    while(1) {
      blinkError();
      delay(1000);
    }
  }
  
  // Initialize WiFi
  if (!initWiFi()) {
    debugPrint("âœ— WiFi init failed - halting");
    while(1) {
      blinkError();
      delay(1000);
    }
  }
  
  // Initialize appropriate mode
  #if USE_PULL_MODE
    initServer();
    debugPrint("Mode: PULL (Server)");
  #else
    debugPrint("Mode: PUSH (Sender)");
  #endif
  
  printStartupInfo();
  
  lastCaptureTime = millis();
  delay(1000);
  
  // Initial capture for Push Mode
  #if !USE_PULL_MODE
    captureAndSend();
  #endif
}

// ===== MAIN LOOP =====
void loop() {
  #if ENABLE_WATCHDOG
    esp_task_wdt_reset();
  #endif
  
  // Handle serial commands
  checkSerialCommands();
  
  #if USE_PULL_MODE
    // PULL MODE: Handle HTTP server requests
    handleServerClients();
    
  #else
    // PUSH MODE: Capture and send at intervals
    if (!systemPaused && (millis() - lastCaptureTime >= captureInterval)) {
      captureAndSend();
      lastCaptureTime = millis();
    }
    
    #if ENABLE_DEEP_SLEEP
      if (!systemPaused && captureInterval >= 60000) {
        debugPrintf("Entering deep sleep for %d seconds", DEEP_SLEEP_SECONDS);
        #if ENABLE_SERIAL_OUTPUT
          Serial.flush();
        #endif
        esp_sleep_enable_timer_wakeup(DEEP_SLEEP_SECONDS * 1000000ULL);
        esp_deep_sleep_start();
      }
    #endif
  #endif
  
  delay(100);
}

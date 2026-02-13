/*
 * ESP32-CAM Simple Image Sender - V1 Modular Multi-File
 * Main file - contains only setup() and loop()
 * 
 * All settings are in ESP32_Config.h
 * Functionality is split across multiple module files
 */

#include "esp_camera.h"
#include "WiFi.h"
#include "HTTPClient.h"
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
  
  if (!initCamera()) {
    debugPrint("✗ Camera init failed - halting");
    while(1) delay(1000);
  }
  
  if (!initWiFi()) {
    debugPrint("✗ WiFi init failed - halting");
    while(1) delay(1000);
  }
  
  printStartupInfo();
  
  lastCaptureTime = millis();
  delay(1000);
  captureAndSend();  // Initial capture
}

// ===== MAIN LOOP =====
void loop() {
  #if ENABLE_WATCHDOG
    esp_task_wdt_reset();
  #endif
  
  checkSerialCommands();
  
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
  
  delay(100);
}

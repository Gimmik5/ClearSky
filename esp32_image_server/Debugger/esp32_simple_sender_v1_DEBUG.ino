/*
 * ESP32-CAM Simple Image Sender - V1 Modular Multi-File
 * DEBUG VERSION - Extra logging to identify crash location
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
  Serial.begin(115200);
  delay(1000);  // Give serial time to initialize
  
  Serial.println("\n\n========================================");
  Serial.println("ESP32-CAM BOOT - DEBUG MODE");
  Serial.println("========================================");
  Serial.flush();
  
  Serial.println("Step 1: System init...");
  Serial.flush();
  initSystem();
  
  Serial.println("Step 2: LED init...");
  Serial.flush();
  initLED();
  
  // SKIP WATCHDOG FOR NOW - It might be causing resets
  // Serial.println("Step 3: Watchdog init...");
  // Serial.flush();
  // initWatchdog();
  Serial.println("Step 3: Watchdog DISABLED for debugging");
  
  Serial.println("Step 4: Camera init...");
  Serial.flush();
  if (!initCamera()) {
    Serial.println("✗ Camera init failed - HALTING");
    Serial.println("Check camera connections!");
    Serial.flush();
    while(1) {
      delay(5000);
      Serial.println("Still waiting... camera failed to init");
    }
  }
  Serial.println("✓ Camera initialized successfully");
  Serial.flush();
  
  Serial.println("Step 5: WiFi init...");
  Serial.flush();
  if (!initWiFi()) {
    Serial.println("✗ WiFi init failed - CONTINUING ANYWAY");
    Serial.println("You can still use serial commands");
    Serial.flush();
  } else {
    Serial.println("✓ WiFi connected successfully");
    Serial.flush();
  }
  
  printStartupInfo();
  
  lastCaptureTime = millis();
  
  Serial.println("\n========================================");
  Serial.println("SETUP COMPLETE - Entering main loop");
  Serial.println("========================================\n");
  Serial.flush();
  
  // Skip initial capture for now
  // delay(1000);
  // captureAndSend();
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

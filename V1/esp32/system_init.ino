/*
 * System Initialization Module
 * Handles system startup, LED setup, and watchdog initialization
 */

#include "globals.h"

#if ENABLE_WATCHDOG
  #include "esp_task_wdt.h"
  #define WDT_TIMEOUT WATCHDOG_TIMEOUT_SECONDS*1000
#endif

// ===== GLOBAL VARIABLE DEFINITIONS =====
bool systemPaused = false;
unsigned long lastCaptureTime = 0;
int captureInterval = DEFAULT_CAPTURE_INTERVAL_MS;
int uploadFailCount = 0;

// ===== SYSTEM INITIALIZATION =====

void initSystem() {
  #if ENABLE_SERIAL_OUTPUT
    Serial.begin(SERIAL_BAUD_RATE);
    Serial.println("\n\n========================================");
    Serial.println("ESP32-CAM Image Sender V1 Modular");
    Serial.println("========================================");
  #endif
}

void initLED() {
  #if LED_ENABLE
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    debugPrint("✓ LED initialized");
  #endif
}

void initWatchdog() {
  #if ENABLE_WATCHDOG
    esp_task_wdt_config_t twdt_config = {
        .timeout_ms = WDT_TIMEOUT
    };
    esp_task_wdt_init(&twdt_config);
    esp_task_wdt_add(NULL);
    debugPrintf("✓ Watchdog enabled (%d seconds)", WDT_TIMEOUT);
  #endif
}

void printStartupInfo() {
  #if ENABLE_SERIAL_OUTPUT
    Serial.println("\n========================================");
    Serial.println("Ready to send images");
    Serial.println("========================================");
    Serial.println("\nCommands:");
    Serial.println("  pause / p      - Stop captures");
    Serial.println("  resume / r     - Resume captures");
    Serial.println("  capture / c    - Capture now");
    Serial.println("  interval N     - Set interval (ms)");
    Serial.println("  status / s     - Show status");
    Serial.println("========================================\n");
  #endif
}

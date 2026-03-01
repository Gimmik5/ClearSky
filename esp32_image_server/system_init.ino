/*
 * System Initialization Module - V1.1 PULL Mode
 * Handles system startup, LED, watchdog, SD card, and NTP
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

// V1.1 SD card state
bool sdCardAvailable = false;
int  sdQueueCount = 0;

// ===== SYSTEM INITIALIZATION =====

void initSystem() {
  /*
   * V1.1 Enhanced initialization:
   * 1. Serial + banner
   * 2. LED
   * 3. Watchdog
   * 4. Camera
   * 5. WiFi
   * 6. NTP (needs WiFi)
   * 7. SD card (independent of WiFi)
   * 8. Web server
   */
  
  #if ENABLE_SERIAL_OUTPUT
    Serial.begin(SERIAL_BAUD_RATE);
    delay(100);
    Serial.println("\n\n========================================");
    Serial.println("ESP32-CAM Image Server V1.1");
    Serial.println("SD Card Offline Storage Edition");
    Serial.println("========================================");
  #endif
  
  initLED();
  
  #if ENABLE_WATCHDOG
    initWatchdog();
  #endif
  
  // Camera init (handled in main .ino setup)
  
  // WiFi init (handled in main .ino setup)
  
  // NTP sync (after WiFi connects)
  if (WiFi.status() == WL_CONNECTED) {
    initNTP();
  } else {
    debugPrint("[Time] WiFi not connected - NTP sync skipped");
  }
  
  // SD card init
  #if ENABLE_SD_CARD
    if (!initSDCard()) {
      debugPrint("[Init] SD card unavailable - offline storage disabled");
    } else {
      int queued = countQueuedImages();
      if (queued > 0) {
        debugPrintf("[Init] %d image(s) waiting in offline queue", queued);
      }
    }
  #endif
  
  // Web server init (handled in main .ino setup)
}

void initLED() {
  #if LED_ENABLE
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    debugPrint("[OK] LED initialized");
  #endif
}

void initWatchdog() {
  #if ENABLE_WATCHDOG
    esp_task_wdt_config_t twdt_config = {
        .timeout_ms = WDT_TIMEOUT
    };
    esp_task_wdt_init(&twdt_config);
    esp_task_wdt_add(NULL);
    debugPrintf("[OK] Watchdog enabled (%d seconds)", WATCHDOG_TIMEOUT_SECONDS);
  #endif
}

void printStartupInfo() {
  #if ENABLE_SERIAL_OUTPUT
    Serial.println("\n========================================");
    Serial.println("Ready - Pull Mode with SD Queue");
    Serial.println("========================================");
    
    #if ENABLE_SD_CARD
      if (sdCardAvailable) {
        Serial.printf("SD Card: %d%% used, %d queued\n", 
                      getSDUsagePercent(), sdQueueCount);
      }
    #endif
    
    Serial.println("\nCommands:");
    Serial.println("  pause / p      - Stop captures");
    Serial.println("  resume / r     - Resume captures");
    Serial.println("  capture / c    - Capture now");
    Serial.println("  interval N     - Set interval (ms)");
    Serial.println("  status / s     - Show status");
    Serial.println("  sdstatus       - Show SD card status");
    Serial.println("========================================\n");
  #endif
}

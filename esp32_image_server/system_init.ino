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
  Serial.println("[DEBUG] About to init LED"); //debug addition
  initLED();
  

  Serial.println("[DEBUG] About to init watchdog"); //debug addition
  #if ENABLE_WATCHDOG
    initWatchdog();
  #endif
  
  // Camera init (handled in main .ino setup)
    Serial.println("[DEBUG] About to init camera");
  if (!initCamera()) {
    debugPrint("✗ Camera init failed - halting");
    while(1) {
      blinkError();
      delay(1000);
    }
  }
  Serial.println("[DEBUG] Camera init succeeded");

  // WiFi init (handled in main .ino setup)
  Serial.println("[DEBUG] About to init WiFi");
  if (!initWiFi()) {
    debugPrint("✗ WiFi init failed - halting");
    while(1) {
      blinkError();
      delay(1000);
    }
  }
  Serial.println("[DEBUG] WiFi init succeeded");


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
      sdCardAvailable = false;
    } else {
      sdCardAvailable = true;
      
      // Show SD stats
      uint64_t totalMB = SD_MMC.totalBytes() / (1024 * 1024);
      uint64_t usedMB  = SD_MMC.usedBytes()  / (1024 * 1024);
      debugPrintf("[SD] Ready  Total: %lluMB  Used: %lluMB", totalMB, usedMB);
      debugPrint("[Init] SD card ready - offline storage enabled");
      
      // Optional: Count queue only if usage is low
      // (prevents out-of-memory with thousands of files)
      if (getSDUsagePercent() < 20) {
        int queued = countQueuedImages();
        if (queued > 0) {
          debugPrintf("[Init] %d image(s) in offline queue", queued);
        }
      } else {
        debugPrint("[Init] Large queue detected - count skipped (check /sd/browse)");
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
        Serial.printf("SD Card: %d%% used\n", getSDUsagePercent());
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

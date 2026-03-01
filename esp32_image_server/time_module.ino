/*
 * Time Module (V1.1)
 * 
 * NTP synchronization for accurate wall-clock timestamps.
 * Used to name offline images so Python can reconstruct the timeline.
 * 
 * Syncs once after WiFi connects. ESP32 RTC keeps reasonable time
 * between boots (drifts, but good enough for sky monitoring intervals).
 * 
 * Falls back to millis() if NTP never succeeds.
 */

#include "globals.h"
#include <time.h>

// NTP servers (primary + fallbacks)
static const char* NTP_SERVER_1 = "pool.ntp.org";
static const char* NTP_SERVER_2 = "time.google.com";
static const char* NTP_SERVER_3 = "time.cloudflare.com";

// Timezone configuration
// Change these to match your location:
//   UTC+0  = 0
//   UTC+1  = 3600
//   UTC-5  = -18000
static const long GMT_OFFSET_SEC      = 0;
static const int  DAYLIGHT_OFFSET_SEC = 0;  // Set to 3600 during DST

static bool ntpSynced = false;

void initNTP() {
  /*
   * Configure SNTP and wait up to 10 seconds for valid time.
   * Call once after WiFi connects.
   */
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC,
             NTP_SERVER_1, NTP_SERVER_2, NTP_SERVER_3);

  debugPrint("[Time] Syncing NTP...");
  struct tm timeinfo;
  int attempts = 0;

  while (!getLocalTime(&timeinfo, 1000) && attempts < 10) {
    Serial.print(".");
    attempts++;
  }

  if (getLocalTime(&timeinfo, 0)) {
    ntpSynced = true;
    char buf[32];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &timeinfo);
    debugPrintf(" OK  [%s UTC]", buf);
  } else {
    ntpSynced = false;
    debugPrint(" FAILED (using millis fallback)");
  }
}

bool isNTPSynced() {
  return ntpSynced;
}

String getTimestamp() {
  /*
   * Returns timestamp string: YYYYMMDD_HHMMSS
   * Falls back to NORTS_<millis> if RTC year < 2024.
   */
  struct tm timeinfo;
  if (getLocalTime(&timeinfo, 0) && (timeinfo.tm_year + 1900) >= 2024) {
    char buf[20];
    strftime(buf, sizeof(buf), "%Y%m%d_%H%M%S", &timeinfo);
    return String(buf);
  }

  // Fallback: millis() zero-padded to 13 digits
  char buf[20];
  snprintf(buf, sizeof(buf), "NORTS_%013lu", millis());
  return String(buf);
}

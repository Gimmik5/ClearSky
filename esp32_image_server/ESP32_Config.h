/*
 * ESP32-CAM Configuration File
 * 
 * All ESP32 settings are configured here.
 * Edit this file instead of the main sketch.
 */

#ifndef ESP32_CONFIG_H
#define ESP32_CONFIG_H

// ===== WIFI SETTINGS =====
const char* WIFI_SSID     = "YourActualNetworkName";
const char* WIFI_PASSWORD = "your_actual_wifi_password";

// WiFi connection settings
#define WIFI_TIMEOUT_SECONDS 40        // How long to wait for connection
#define WIFI_RETRY_DELAY_MS  500       // Delay between connection attempts

// ===== OPERATION MODE =====
// Set to true for Pull Mode (Python fetches from ESP32 server)
// Set to false for Push Mode (ESP32 uploads to Python server)
#define USE_PULL_MODE true

// ===== SERVER SETTINGS (Pull Mode) =====
// Port the ESP32 web server listens on
// Python will fetch images from http://<ESP32_IP>:<ESP32_SERVER_PORT>/capture
#define ESP32_SERVER_PORT 80

// ===== UPLOAD SETTINGS (Push Mode - only used if USE_PULL_MODE is false) =====
#define SERVER_URL "http://192.168.1.100:5000/upload"  // Change to your Python server address
#define HTTP_TIMEOUT_MS 10000                           // HTTP request timeout (10 seconds)

// ===== CAPTURE TIMING =====
#define DEFAULT_CAPTURE_INTERVAL_MS 30000   // Default: capture every 30 seconds
#define MIN_CAPTURE_INTERVAL_MS 20000        // Minimum: 5 seconds between captures

// ===== CAMERA SETTINGS =====

// Camera pin configuration for AI Thinker ESP32-CAM
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Image quality settings
// Frame size options:
//   FRAMESIZE_QVGA   (320x240)  - Fast, low quality, low bandwidth
//   FRAMESIZE_VGA    (640x480)  - Balanced (recommended)
//   FRAMESIZE_SVGA   (800x600)  - High quality, more bandwidth
//   FRAMESIZE_XGA    (1024x768) - Very high quality, slow
#define CAMERA_FRAME_SIZE   FRAMESIZE_QVGA

// JPEG quality: 0-63 (lower = better quality, larger file size)
#define CAMERA_JPEG_QUALITY 20

// Camera sensor auto-adjustments
#define CAMERA_AUTO_EXPOSURE    true   // Auto exposure control
#define CAMERA_AUTO_GAIN        true   // Auto gain control
#define CAMERA_AUTO_WHITE_BALANCE true // Auto white balance

// Manual adjustments (used if auto disabled)
#define CAMERA_BRIGHTNESS 0            // -2 to 2
#define CAMERA_CONTRAST   0            // -2 to 2
#define CAMERA_SATURATION 0            // -2 to 2

// ===== SERIAL SETTINGS =====
#define SERIAL_BAUD_RATE     115200    // Serial communication speed
#define ENABLE_SERIAL_OUTPUT true      // Enable serial prints
#define SHOW_DETAILED_OUTPUT true      // Show detailed status messages

// ===== LED SETTINGS =====
#define LED_PIN            33          // Built-in LED pin
#define LED_ENABLE         false       // Enable LED status indicator
#define LED_BLINK_ON_CAPTURE true      // Blink when capturing

// ===== RETRY SETTINGS =====
#define MAX_CAPTURE_RETRIES 3          // Max attempts if capture fails
#define MAX_UPLOAD_RETRIES  2          // Max upload attempts (Push Mode)
#define RETRY_DELAY_MS      1000       // Delay between retries (ms)

// ===== POWER MANAGEMENT =====
#define ENABLE_DEEP_SLEEP false        // Deep sleep between captures
#define DEEP_SLEEP_SECONDS  60         // Sleep duration if enabled

// ===== WATCHDOG =====
#define ENABLE_WATCHDOG          false // Enable watchdog timer
#define WATCHDOG_TIMEOUT_SECONDS 60    // Watchdog timeout

// ===== BUFFER SETTINGS =====
#define CAMERA_FB_COUNT 1              // Frame buffer count (1 or 2)

// ===== PRESETS =====
// Uncomment ONE preset for common scenarios

// PRESET: Fast Development
// #define USE_PRESET_DEV
#ifdef USE_PRESET_DEV
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_QVGA
  #undef SHOW_DETAILED_OUTPUT
  #define SHOW_DETAILED_OUTPUT true
#endif

// PRESET: Production (reliable)
// #define USE_PRESET_PRODUCTION
#ifdef USE_PRESET_PRODUCTION
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_VGA
  #undef ENABLE_WATCHDOG
  #define ENABLE_WATCHDOG true
#endif

// PRESET: High Quality
// #define USE_PRESET_HIGH_QUALITY
#ifdef USE_PRESET_HIGH_QUALITY
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_SVGA
  #undef CAMERA_JPEG_QUALITY
  #define CAMERA_JPEG_QUALITY 5
#endif
// ===== SD CARD SETTINGS =====

// Enable/disable SD card offline storage
#define ENABLE_SD_CARD true

// Directory on SD card where offline images are queued
#define SD_QUEUE_DIR "/offline"

// Storage management thresholds (percentage of total capacity)
#define SD_WARN_PERCENT   80   // Trigger cleanup at this usage level
#define SD_TARGET_PERCENT 50   // Clean until usage drops to this level

// Maximum single image size accepted for SD write (bytes)
// Default matches Python MAX_IMAGE_SIZE_MB (5 MB)
#define SD_MAX_IMAGE_BYTES (5 * 1024 * 1024)

// Delay between queue endpoint requests during sync (ms)
// Prevents server overload when Python fetches many queued images
#define SD_SYNC_DELAY_MS 500

// When poller is inactive, how often to auto-capture to SD (ms)
// Default: 10 seconds (matches typical Python polling interval)
#define FALLBACK_CAPTURE_INTERVAL_MS 300000

// How long to wait before considering poller "dead" (ms)
// Default: 60 seconds (6x the normal polling interval)
#define POLL_TIMEOUT_MS 360000


#endif // ESP32_CONFIG_H

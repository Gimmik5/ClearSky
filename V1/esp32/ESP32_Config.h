/*
 * ESP32-CAM Configuration File
 * 
 * All ESP32 settings are configured here.
 * Edit this file instead of the main sketch.
 */

#ifndef ESP32_CONFIG_H
#define ESP32_CONFIG_H

// ===== WIFI SETTINGS =====
const char* WIFI_SSID = "BT-N5CM5C";
const char* WIFI_PASSWORD = "LmHk7LnJ6cHfNL";

// WiFi connection settings
#define WIFI_TIMEOUT_SECONDS 40        // How long to wait for connection
#define WIFI_RETRY_DELAY_MS 500        // Delay between connection attempts

// ===== SERVER SETTINGS =====
// Your PC's IP address (find with ipconfig/ifconfig)
const char* SERVER_URL = "http://192.168.1.146:5000/upload";

// HTTP settings
#define HTTP_TIMEOUT_MS 10000          // Timeout for HTTP requests

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
//   FRAMESIZE_QVGA   (320x240)   - Fast, low quality, low bandwidth
//   FRAMESIZE_VGA    (640x480)   - Balanced (recommended)
//   FRAMESIZE_SVGA   (800x600)   - High quality, more bandwidth
//   FRAMESIZE_XGA    (1024x768)  - Very high quality, slow upload
#define CAMERA_FRAME_SIZE FRAMESIZE_SVGA

// JPEG quality: 0-63 (lower = better quality, larger file size)
#define CAMERA_JPEG_QUALITY 10

// Camera sensor auto-adjustments
#define CAMERA_AUTO_EXPOSURE true      // Auto exposure control
#define CAMERA_AUTO_GAIN true          // Auto gain control
#define CAMERA_AUTO_WHITE_BALANCE true // Auto white balance

// Manual adjustments (if auto disabled)
#define CAMERA_BRIGHTNESS 0            // -2 to 2 (0 = default)
#define CAMERA_CONTRAST 0              // -2 to 2 (0 = default)
#define CAMERA_SATURATION 0            // -2 to 2 (0 = default)

// ===== TIMING SETTINGS =====

// Default capture interval (milliseconds)
#define DEFAULT_CAPTURE_INTERVAL_MS 10000  // 10 seconds

// Common presets (uncomment one to use):
// #define DEFAULT_CAPTURE_INTERVAL_MS 5000     // 5 seconds
// #define DEFAULT_CAPTURE_INTERVAL_MS 30000    // 30 seconds
// #define DEFAULT_CAPTURE_INTERVAL_MS 60000    // 1 minute
// #define DEFAULT_CAPTURE_INTERVAL_MS 300000   // 5 minutes

// Minimum interval (safety limit)
#define MIN_CAPTURE_INTERVAL_MS 1000   // 1 second minimum

// ===== SERIAL SETTINGS =====
#define SERIAL_BAUD_RATE 115200        // Serial communication speed
#define ENABLE_SERIAL_OUTPUT true      // Enable serial prints
#define SHOW_DETAILED_OUTPUT true      // Show detailed status messages

// ===== LED SETTINGS =====
#define LED_PIN 33                     // Built-in LED pin (if available)
#define LED_ENABLE false               // Enable LED status indicator
#define LED_BLINK_ON_CAPTURE true      // Blink LED when capturing

// ===== RETRY SETTINGS =====
#define MAX_CAPTURE_RETRIES 3          // Max attempts if capture fails
#define MAX_UPLOAD_RETRIES 2           // Max attempts if upload fails
#define RETRY_DELAY_MS 1000            // Delay between retries

// ===== POWER MANAGEMENT =====
#define ENABLE_DEEP_SLEEP false        // Use deep sleep between captures
#define DEEP_SLEEP_SECONDS 60          // Sleep duration if enabled

// ===== WATCHDOG =====
#define ENABLE_WATCHDOG false           // Enable watchdog timer
#define WATCHDOG_TIMEOUT_SECONDS 60    // Watchdog timeout

// ===== BUFFER SETTINGS =====
#define CAMERA_FB_COUNT 1              // Frame buffer count (1 or 2)

// ===== PRESETS =====
// Uncomment ONE preset to quickly configure for common scenarios

// PRESET: Fast Development (quick iterations)
// #define USE_PRESET_DEV
#ifdef USE_PRESET_DEV
  #undef DEFAULT_CAPTURE_INTERVAL_MS
  #define DEFAULT_CAPTURE_INTERVAL_MS 5000
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_QVGA
  #undef SHOW_DETAILED_OUTPUT
  #define SHOW_DETAILED_OUTPUT true
#endif

// PRESET: Production (balanced, reliable)
// #define USE_PRESET_PRODUCTION
#ifdef USE_PRESET_PRODUCTION
  #undef DEFAULT_CAPTURE_INTERVAL_MS
  #define DEFAULT_CAPTURE_INTERVAL_MS 30000
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_VGA
  #undef ENABLE_WATCHDOG
  #define ENABLE_WATCHDOG true
#endif

// PRESET: Low Power (battery operation)
// #define USE_PRESET_LOW_POWER
#ifdef USE_PRESET_LOW_POWER
  #undef DEFAULT_CAPTURE_INTERVAL_MS
  #define DEFAULT_CAPTURE_INTERVAL_MS 300000  // 5 minutes
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_QVGA
  #undef ENABLE_DEEP_SLEEP
  #define ENABLE_DEEP_SLEEP true
  #undef LED_ENABLE
  #define LED_ENABLE false
#endif

// PRESET: High Quality (best images)
// #define USE_PRESET_HIGH_QUALITY
#ifdef USE_PRESET_HIGH_QUALITY
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_SVGA
  #undef CAMERA_JPEG_QUALITY
  #define CAMERA_JPEG_QUALITY 5
  #undef DEFAULT_CAPTURE_INTERVAL_MS
  #define DEFAULT_CAPTURE_INTERVAL_MS 60000  // 1 minute (slow upload)
#endif

#endif // ESP32_CONFIG_H

/*
 * ===== CONFIGURATION GUIDE =====
 * 
 * QUICK START:
 * 1. Set WIFI_SSID and WIFI_PASSWORD
 * 2. Set SERVER_URL to your PC's IP (find with ipconfig/ifconfig)
 * 3. Choose CAMERA_FRAME_SIZE based on your WiFi speed
 * 4. Set DEFAULT_CAPTURE_INTERVAL_MS
 * 
 * FRAME SIZE RECOMMENDATIONS:
 * - QVGA (320x240): Fast WiFi upload, lower quality
 * - VGA (640x480): Balanced, recommended for most use
 * - SVGA (800x600): Better quality, slower upload
 * - XGA (1024x768): Best quality, very slow
 * 
 * INTERVAL RECOMMENDATIONS:
 * - Development/testing: 5-10 seconds
 * - Normal monitoring: 30-60 seconds
 * - Battery powered: 5-15 minutes
 * - Time-lapse: 1-5 minutes
 * 
 * JPEG QUALITY:
 * - 5-8: Excellent quality, large files
 * - 10-12: Good quality, medium files (recommended)
 * - 15-20: Acceptable quality, small files
 * - Higher numbers = lower quality
 * 
 * TROUBLESHOOTING:
 * 
 * WiFi won't connect:
 * - Check SSID and password
 * - Make sure router is 2.4GHz (ESP32 doesn't support 5GHz)
 * - Increase WIFI_TIMEOUT_SECONDS
 * - Check signal strength
 * 
 * Upload fails:
 * - Verify SERVER_URL is correct
 * - Make sure PC server is running
 * - Check PC firewall (allow port 5000)
 * - Try reducing CAMERA_FRAME_SIZE
 * - Increase HTTP_TIMEOUT_MS
 * 
 * Camera init fails:
 * - Check all pin connections
 * - Verify camera ribbon cable is inserted correctly
 * - Try different CAMERA_FRAME_SIZE
 * - Power cycle the ESP32
 * 
 * Images are too dark/bright:
 * - Enable CAMERA_AUTO_EXPOSURE
 * - Adjust CAMERA_BRIGHTNESS manually
 * - Check camera orientation (should face sky)
 * 
 * ESP32 crashes/resets:
 * - Reduce CAMERA_FRAME_SIZE
 * - Enable ENABLE_WATCHDOG
 * - Check power supply (needs stable 5V)
 * - Reduce CAMERA_FB_COUNT to 1
 */
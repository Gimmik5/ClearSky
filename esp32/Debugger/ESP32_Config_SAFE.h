/*
 * ESP32-CAM Configuration File - SAFE DEBUGGING VERSION
 * 
 * This version has safe, conservative settings for debugging
 * Use this if you're experiencing continuous resets
 */

#ifndef ESP32_CONFIG_H
#define ESP32_CONFIG_H

// ===== WIFI SETTINGS =====
const char* WIFI_SSID = "YourWiFiName";        // CHANGE THIS
const char* WIFI_PASSWORD = "YourWiFiPassword"; // CHANGE THIS

// WiFi connection settings
#define WIFI_TIMEOUT_SECONDS 90        // Increased timeout
#define WIFI_RETRY_DELAY_MS 500

// ===== SERVER SETTINGS =====
const char* SERVER_URL = "http://192.168.1.100:5000/upload"; // CHANGE THIS to your PC's IP

// HTTP settings
#define HTTP_TIMEOUT_MS 10000

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

// Image quality settings - CONSERVATIVE FOR DEBUGGING
#define CAMERA_FRAME_SIZE FRAMESIZE_QVGA  // Small and fast (320x240)
#define CAMERA_JPEG_QUALITY 12             // Medium quality

// Camera sensor auto-adjustments
#define CAMERA_AUTO_EXPOSURE true
#define CAMERA_AUTO_GAIN true
#define CAMERA_AUTO_WHITE_BALANCE true

// Manual adjustments
#define CAMERA_BRIGHTNESS 0
#define CAMERA_CONTRAST 0
#define CAMERA_SATURATION 0

// ===== TIMING SETTINGS =====
#define DEFAULT_CAPTURE_INTERVAL_MS 30000  // 30 seconds - slow for debugging
#define MIN_CAPTURE_INTERVAL_MS 1000

// ===== SERIAL SETTINGS =====
#define SERIAL_BAUD_RATE 115200
#define ENABLE_SERIAL_OUTPUT true
#define SHOW_DETAILED_OUTPUT true          // Extra debugging info

// ===== LED SETTINGS =====
#define LED_PIN 4                          // ESP32-CAM flash LED (some boards don't have this)
#define LED_ENABLE false                   // DISABLED - may not exist or cause issues
#define LED_BLINK_ON_CAPTURE false

// ===== RETRY SETTINGS =====
#define MAX_CAPTURE_RETRIES 3
#define MAX_UPLOAD_RETRIES 2
#define RETRY_DELAY_MS 1000

// ===== POWER MANAGEMENT =====
#define ENABLE_DEEP_SLEEP false            // DISABLED for debugging

// ===== WATCHDOG =====
#define ENABLE_WATCHDOG false              // DISABLED for debugging - enable after it works
#define WATCHDOG_TIMEOUT_SECONDS 120       // Increased timeout when enabled

// ===== BUFFER SETTINGS =====
#define CAMERA_FB_COUNT 1                  // Single buffer only

#endif // ESP32_CONFIG_H

/*
 * ===== DEBUGGING CONFIGURATION NOTES =====
 * 
 * This configuration is designed to be as stable as possible:
 * 
 * 1. WATCHDOG DISABLED
 *    - Won't reset during initialization
 *    - Enable after everything works
 * 
 * 2. SMALL FRAME SIZE (QVGA)
 *    - Faster processing
 *    - Less memory usage
 *    - Reduces crash risk
 * 
 * 3. LONG TIMEOUTS
 *    - 90 seconds for WiFi
 *    - 10 seconds for HTTP
 * 
 * 4. LED DISABLED
 *    - Some ESP32-CAM boards don't have LED on pin 4
 *    - Avoids potential pin conflicts
 * 
 * 5. SINGLE FRAME BUFFER
 *    - Minimal memory usage
 *    - Most stable configuration
 * 
 * 6. SLOW CAPTURE INTERVAL
 *    - 30 seconds between images
 *    - Easy to debug
 * 
 * AFTER IT WORKS:
 * - Re-enable watchdog
 * - Increase frame size if needed
 * - Reduce capture interval
 * - Enable LED if your board has one
 */

/*
 * Configuration File
 * 
 * All user-configurable settings are in this file.
 * Change settings here instead of modifying the main sketch.
 * 
 * This is a .h (header) file, not a .ino file.
 * Save this as "Config.h" in the same folder as your sketch.
 */

#ifndef CONFIG_H
#define CONFIG_H

// =========================================
// FEATURE ENABLE/DISABLE
// =========================================

// Enable/disable major features
#define ENABLE_WEB_SERVER true          // Web interface for viewing images
#define ENABLE_SERIAL_COMMANDS true      // Keyboard control via Serial Monitor

// Enable/disable analysis methods
#define USE_BRIGHTNESS_ANALYSIS true     // Simple brightness analysis (fast)
#define USE_COLOR_ANALYSIS true          // Detailed RGB color analysis (slower)
#define USE_SKY_FEATURES false           // Advanced sky feature detection (slowest)

// =========================================
// WIFI SETTINGS (only used if ENABLE_WEB_SERVER is true)
// =========================================

const char* WIFI_SSID = "BT-N5CM5C";
const char* WIFI_PASSWORD = "LmHk7LnJ6cHfNL";

// WiFi connection settings
#define WIFI_TIMEOUT_SECONDS 20          // How long to wait for WiFi connection
#define WEB_SERVER_PORT 80               // Port for web server (80 = standard HTTP)

// =========================================
// CAMERA SETTINGS
// =========================================

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
//   FRAMESIZE_QVGA   (320x240)   - Fast, low quality, low memory
//   FRAMESIZE_VGA    (640x480)   - Balanced (recommended)
//   FRAMESIZE_SVGA   (800x600)   - High quality, more memory
//   FRAMESIZE_XGA    (1024x768)  - Very high quality, most memory
#define CAMERA_FRAME_SIZE FRAMESIZE_VGA

// JPEG quality: 0-63 (lower = better quality, larger file size)
#define CAMERA_JPEG_QUALITY 12

// Camera sensor adjustments (0 = auto/default)
#define CAMERA_BRIGHTNESS 0              // -2 to 2
#define CAMERA_CONTRAST 0                // -2 to 2
#define CAMERA_SATURATION 0              // -2 to 2
#define CAMERA_AUTO_EXPOSURE true        // Auto exposure control
#define CAMERA_AUTO_GAIN true            // Auto gain control
#define CAMERA_AUTO_WHITE_BALANCE true   // Auto white balance

// =========================================
// TIMING SETTINGS
// =========================================

// Default capture interval (milliseconds)
// Can be changed at runtime via Serial commands
#define DEFAULT_CAPTURE_INTERVAL_MS 10000  // 10 seconds

// Common presets (uncomment one to use):
// #define DEFAULT_CAPTURE_INTERVAL_MS 5000    // 5 seconds
// #define DEFAULT_CAPTURE_INTERVAL_MS 30000   // 30 seconds
// #define DEFAULT_CAPTURE_INTERVAL_MS 60000   // 1 minute
// #define DEFAULT_CAPTURE_INTERVAL_MS 300000  // 5 minutes

// =========================================
// SERIAL OUTPUT SETTINGS
// =========================================

#define SERIAL_BAUD_RATE 115200          // Serial communication speed

// Output verbosity controls
#define SHOW_IMAGE_INFO true             // Show image size, dimensions
#define SHOW_DETAILED_OUTPUT true        // Show detailed analysis results
#define SHOW_STARTUP_BANNER true         // Show welcome banner on startup

// =========================================
// ANALYSIS THRESHOLDS & PARAMETERS
// =========================================

// Brightness Analysis Thresholds (0-255 scale)
#define BRIGHTNESS_VERY_BRIGHT 180       // Clear/sunny threshold
#define BRIGHTNESS_BRIGHT 140            // Partly cloudy threshold
#define BRIGHTNESS_MODERATE 100          // Cloudy threshold
#define BRIGHTNESS_DIM 60                // Overcast threshold

// Color Analysis Parameters
#define COLOR_SAMPLE_RATE 50             // Sample every Nth pixel (lower = slower but more accurate)
#define BLUE_DOMINANCE_RED_DIFF 20       // Blue must be this much higher than red
#define BLUE_DOMINANCE_GREEN_DIFF 10     // Blue must be this much higher than green
#define GRAY_VARIANCE_THRESHOLD 30       // Color variance for gray detection

// Sky Features Parameters
#define SKY_FEATURES_SAMPLE_RATE 100     // Sample every Nth pixel
#define BLUE_SKY_MIN_VALUE 150           // Minimum blue value for "blue sky"
#define BLUE_SKY_RED_DIFF 30             // Blue > red by this much
#define BLUE_SKY_GREEN_DIFF 20           // Blue > green by this much
#define WHITE_BRIGHTNESS_MIN 200         // Minimum brightness for "white"
#define WHITE_VARIANCE_MAX 40            // Max color variance for "white"

// =========================================
// MEMORY & PERFORMANCE
// =========================================

// Loop delay (milliseconds) - prevents excessive CPU usage
#define MAIN_LOOP_DELAY_MS 100

// Minimum interval between captures (safety limit)
#define MIN_CAPTURE_INTERVAL_MS 1000     // 1 second minimum

// =========================================
// ADVANCED SETTINGS
// =========================================

// Camera frame buffer count (1 or 2)
// 2 buffers allow continuous capture but use more RAM
#define CAMERA_FB_COUNT 1

// Enable camera test pattern (for debugging)
#define CAMERA_TEST_PATTERN false

// =========================================
// PRESET CONFIGURATIONS
// =========================================

// Uncomment ONE of these to use a preset configuration:

// PRESET: Fast & Efficient (battery powered, low data)
// #define USE_PRESET_FAST
#ifdef USE_PRESET_FAST
  #undef USE_BRIGHTNESS_ANALYSIS
  #define USE_BRIGHTNESS_ANALYSIS true
  #undef USE_COLOR_ANALYSIS
  #define USE_COLOR_ANALYSIS false
  #undef USE_SKY_FEATURES
  #define USE_SKY_FEATURES false
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_QVGA
  #undef DEFAULT_CAPTURE_INTERVAL_MS
  #define DEFAULT_CAPTURE_INTERVAL_MS 60000
#endif

// PRESET: Detailed Analysis (maximum accuracy)
// #define USE_PRESET_DETAILED
#ifdef USE_PRESET_DETAILED
  #undef USE_BRIGHTNESS_ANALYSIS
  #define USE_BRIGHTNESS_ANALYSIS true
  #undef USE_COLOR_ANALYSIS
  #define USE_COLOR_ANALYSIS true
  #undef USE_SKY_FEATURES
  #define USE_SKY_FEATURES true
  #undef CAMERA_FRAME_SIZE
  #define CAMERA_FRAME_SIZE FRAMESIZE_VGA
  #undef DEFAULT_CAPTURE_INTERVAL_MS
  #define DEFAULT_CAPTURE_INTERVAL_MS 30000
#endif

// PRESET: Testing & Development
// #define USE_PRESET_TESTING
#ifdef USE_PRESET_TESTING
  #undef ENABLE_SERIAL_COMMANDS
  #define ENABLE_SERIAL_COMMANDS true
  #undef ENABLE_WEB_SERVER
  #define ENABLE_WEB_SERVER false
  #undef DEFAULT_CAPTURE_INTERVAL_MS
  #define DEFAULT_CAPTURE_INTERVAL_MS 5000
  #undef SHOW_IMAGE_INFO
  #define SHOW_IMAGE_INFO true
  #undef SHOW_DETAILED_OUTPUT
  #define SHOW_DETAILED_OUTPUT true
#endif

#endif // CONFIG_H

/*
 * ===== CONFIGURATION GUIDE =====
 * 
 * QUICK START:
 * 1. Set ENABLE_WEB_SERVER to true or false
 * 2. If using web server, enter your WiFi credentials
 * 3. Choose which analyses to enable
 * 4. Set DEFAULT_CAPTURE_INTERVAL_MS
 * 
 * PRESETS:
 * Uncomment one preset at the bottom to quickly configure for common use cases:
 * - USE_PRESET_FAST: Battery efficient, basic analysis
 * - USE_PRESET_DETAILED: Full analysis, best accuracy
 * - USE_PRESET_TESTING: Quick captures for development
 * 
 * CAMERA QUALITY:
 * Frame Size vs Memory:
 * - QVGA (320x240): ~100KB RAM, very fast
 * - VGA (640x480): ~600KB RAM, balanced
 * - SVGA (800x600): ~1MB RAM, high quality
 * - XGA (1024x768): ~1.5MB RAM, maximum quality
 * 
 * ANALYSIS SPEED:
 * Approximate processing times:
 * - Brightness: ~50ms
 * - Color: ~200-500ms (varies with frame size)
 * - Sky Features: ~300-800ms (most detailed)
 * 
 * TIMING RECOMMENDATIONS:
 * - Testing: 5-10 seconds
 * - Normal use: 30-60 seconds
 * - Battery powered: 5-15 minutes
 * - Time-lapse: 1-5 minutes
 * 
 * THRESHOLDS:
 * Adjust brightness thresholds based on your location:
 * - Sunny climate: increase thresholds by 10-20
 * - Cloudy climate: decrease thresholds by 10-20
 * - Indoor testing: decrease significantly
 * 
 * TROUBLESHOOTING:
 * If ESP32 crashes or resets:
 * - Reduce CAMERA_FRAME_SIZE
 * - Disable some analyses
 * - Increase capture interval
 * 
 * If colors seem wrong:
 * - Enable all auto settings (exposure, gain, white balance)
 * - Adjust saturation
 * - Check camera orientation (should face sky)
 * 
 * If images are too dark/bright:
 * - Adjust CAMERA_BRIGHTNESS (-2 to +2)
 * - Enable CAMERA_AUTO_EXPOSURE
 * - Check time of day (may need different settings for dawn/dusk)
 */
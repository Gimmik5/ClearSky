/*
 * ESP32-CAM Clear Sky Predictor - Main Control File
 * 
 * This is your main sketch file that controls everything.
 * All settings are configured in Config.h
 * 
 * IMPORTANT: This file must be named the same as your folder!
 * Example: If folder is "Sky_Predictor", this file must be "Sky_Predictor.ino"
 */
#include "esp_camera.h"
#include "img_converters.h"
#include "Config.h"  // All settings are in Config.h

// Only include WiFi if web server is enabled
#if ENABLE_WEB_SERVER
  #include <WiFi.h>
  #include <WebServer.h>
  WebServer server(WEB_SERVER_PORT);
#endif

// ===== GLOBAL VARIABLES =====
camera_fb_t * fb = NULL;                 // Frame buffer to store captured image
bool systemPaused = false;               // Pause/resume state
bool manualCaptureRequested = false;     // Flag for manual capture
unsigned long lastCaptureTime = 0;       // Track last capture time
int captureIntervalMs = DEFAULT_CAPTURE_INTERVAL_MS;  // Current interval (can be changed at runtime)

// ===== FUNCTION DECLARATIONS =====
// These tell the compiler that these functions exist in other files
bool initCamera();
void analyzeBrightness(camera_fb_t * frame);
void analyzeColor(camera_fb_t * frame);
void analyzeSkyColor(int red, int green, int blue);
void detectSkyFeatures(camera_fb_t * frame);

#if ENABLE_SERIAL_COMMANDS
  void checkSerialCommands();
  void printStatus();
  void printHelp();
  void printConfig();
#endif

#if ENABLE_WEB_SERVER
  void setupWebServer();
  void handleRoot();
  void handleCapture();
  void handlePause();
  void handleResume();
  void handleStatus();
#endif

// ===== SETUP FUNCTION (Runs once when ESP32 starts) =====
void setup() {
  // Start serial communication
  Serial.begin(SERIAL_BAUD_RATE);
// ADD THIS: Wait 3 seconds for the Serial Monitor to catch up
  for(int i = 3; i > 0; i--) {
    Serial.printf("Starting in %d...\n", i);
    delay(1000);
  }
  #if SHOW_STARTUP_BANNER
    Serial.println("\n\n========================================");
    Serial.println("ESP32-CAM Clear Sky Predictor");
    Serial.println("========================================");
    
    // Display configuration
    Serial.println("\nConfiguration:");
    Serial.printf("  Brightness Analysis: %s\n", USE_BRIGHTNESS_ANALYSIS ? "ON" : "OFF");
    Serial.printf("  Color Analysis: %s\n", USE_COLOR_ANALYSIS ? "ON" : "OFF");
    Serial.printf("  Sky Features: %s\n", USE_SKY_FEATURES ? "ON" : "OFF");
    Serial.printf("  Capture Interval: %d seconds\n", captureIntervalMs / 1000);
    
    #if ENABLE_WEB_SERVER
      Serial.printf("  Web Server: ENABLED\n");
    #endif
    
    #if ENABLE_SERIAL_COMMANDS
      Serial.printf("  Serial Commands: ENABLED (type 'help')\n");
    #endif
  #endif
  
  // Small delay to let things stabilize
  delay(1000);
  
  // Initialize the camera
  if (initCamera()) {
    Serial.println("\n✓ Camera initialized successfully!");
  } else {
    Serial.println("\n✗ Camera initialization FAILED!");
    Serial.println("Check your connections and restart.");
    while(1);  // Stop here if camera fails
  }
  
  // Setup WiFi and web server if enabled
  #if ENABLE_WEB_SERVER
    Serial.println("\nConnecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < WIFI_TIMEOUT_SECONDS * 2) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n✓ WiFi connected!");
      Serial.print("IP Address: ");
      Serial.println(WiFi.localIP());
      setupWebServer();
    } else {
      Serial.println("\n✗ WiFi connection failed");
      Serial.println("Web server will not be available");
    }
  #endif
  
  Serial.println("\n========================================");
  Serial.println("Ready to analyze sky!");
  #if ENABLE_SERIAL_COMMANDS
    Serial.println("Type 'help' for available commands");
  #endif
  Serial.println("========================================\n");
  
  lastCaptureTime = millis();
}

// ===== MAIN LOOP (Runs repeatedly) =====
void loop() {
  // Handle web server requests if enabled
  #if ENABLE_WEB_SERVER
    server.handleClient();
  #endif
  
  // Check for serial commands if enabled
  #if ENABLE_SERIAL_COMMANDS
    checkSerialCommands();
  #endif
  
  // Check if it's time to capture or if manual capture requested
  unsigned long currentTime = millis();
  bool shouldCapture = false;
  
  if (manualCaptureRequested) {
    shouldCapture = true;
    manualCaptureRequested = false;
  } else if (!systemPaused && (currentTime - lastCaptureTime >= captureIntervalMs)) {
    shouldCapture = true;
    lastCaptureTime = currentTime;
  }
  
  // Perform capture and analysis if needed
  if (shouldCapture) {
    // Capture an image
    Serial.println("📷 Capturing image...");
    fb = esp_camera_fb_get();
    
    if (!fb) {
      Serial.println("✗ Image capture failed!");
      delay(1000);
      return;
    }
    
    Serial.println("✓ Image captured!");
    
    // Show image info if enabled
    if (SHOW_IMAGE_INFO) {
      Serial.printf("   Size: %d bytes\n", fb->len);
      Serial.printf("   Width: %d pixels\n", fb->width);
      Serial.printf("   Height: %d pixels\n", fb->height);
    }
    
    // Run selected analyses
    if (USE_BRIGHTNESS_ANALYSIS) {
      analyzeBrightness(fb);
    }
    
    if (USE_COLOR_ANALYSIS) {
      analyzeColor(fb);
    }
    
    if (USE_SKY_FEATURES) {
      detectSkyFeatures(fb);
    }
    
    // Release the frame buffer (important to free memory!)
    esp_camera_fb_return(fb);
    
    if (!systemPaused) {
      Serial.printf("\nNext capture in %d seconds...\n", captureIntervalMs / 1000);
    }
    Serial.println("========================================\n");
  }
  
  // Small delay to prevent excessive CPU usage
  delay(MAIN_LOOP_DELAY_MS);
}

/*
 * ===== FILE STRUCTURE =====
 * 
 * Your sketch folder should contain these files:
 * 
 * REQUIRED:
 * 1. Sky_Predictor.ino           (this file - main control)
 * 2. Config.h                    (all settings - EDIT THIS)
 * 3. Camera_Init.ino             (camera initialization)
 * 4. Brightness_Analysis.ino     (brightness functions)
 * 5. Color_Analysis.ino          (color functions)
 * 
 * OPTIONAL (enable in Config.h):
 * 6. Web_Server.ino              (web interface)
 * 7. Serial_Commands.ino         (keyboard control)
 * 
 * ===== GETTING STARTED =====
 * 
 * 1. Open Config.h
 * 2. Set your preferences:
 *    - Enable/disable features
 *    - Set WiFi credentials (if using web server)
 *    - Choose analysis methods
 *    - Set capture interval
 * 3. Upload this sketch
 * 4. Open Serial Monitor (115200 baud)
 * 
 * ===== QUICK CONFIGURATION =====
 * 
 * All settings are in Config.h. You can:
 * - Use presets (uncomment USE_PRESET_FAST, etc.)
 * - Customize individual settings
 * - Adjust thresholds for your location
 * 
 * No need to edit this file unless adding new features!
 */
/*
 * Serial Commands Module
 * 
 * This module provides keyboard control via Serial Monitor.
 * Type commands in the Serial Monitor to control the system.
 * 
 * NO #include statements needed here - the main file handles that.
 */

// ===== PROCESS SERIAL COMMANDS =====
void checkSerialCommands() {
  // Check if data is available
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace
    command.toLowerCase();  // Convert to lowercase
    
    // Process the command
    if (command == "pause" || command == "p") {
      systemPaused = true;
      Serial.println("\n⏸️  SYSTEM PAUSED");
      Serial.println("Type 'resume' or 'r' to continue\n");
    }
    else if (command == "resume" || command == "r") {
      systemPaused = false;
      Serial.println("\n▶️  SYSTEM RESUMED\n");
    }
    else if (command == "status" || command == "s") {
      printStatus();
    }
    else if (command == "capture" || command == "c") {
      Serial.println("\n📸 Manual capture requested\n");
      // This flag will be checked in the main loop
      manualCaptureRequested = true;
    }
    else if (command == "help" || command == "h" || command == "?") {
      printHelp();
    }
    else if (command == "config") {
      printConfig();
    }
    else if (command.startsWith("interval ")) {
      // Change capture interval: "interval 5000" for 5 seconds
      int newInterval = command.substring(9).toInt();
      if (newInterval >= MIN_CAPTURE_INTERVAL_MS) {
        captureIntervalMs = newInterval;
        Serial.printf("\n✓ Capture interval set to %d ms (%d seconds)\n\n", 
                      captureIntervalMs, captureIntervalMs / 1000);
      } else {
        Serial.printf("\n✗ Invalid interval. Minimum is %dms (%d second)\n\n",
                      MIN_CAPTURE_INTERVAL_MS, MIN_CAPTURE_INTERVAL_MS / 1000);
      }
    }
    else if (command.length() > 0) {
      Serial.println("\n❓ Unknown command. Type 'help' for available commands.\n");
    }
  }
}

// ===== PRINT STATUS =====
void printStatus() {
  Serial.println("\n========================================");
  Serial.println("SYSTEM STATUS");
  Serial.println("========================================");
  Serial.printf("State: %s\n", systemPaused ? "⏸️  PAUSED" : "▶️  RUNNING");
  Serial.printf("Uptime: %lu seconds\n", millis() / 1000);
  Serial.printf("Capture Interval: %d ms (%d seconds)\n", 
                captureIntervalMs, captureIntervalMs / 1000);
  Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());
  
  #ifdef ENABLE_WEB_SERVER
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("WiFi: Connected to %s\n", WIFI_SSID);
    Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("WiFi: Disconnected");
  }
  #endif
  
  Serial.println("========================================\n");
}

// ===== PRINT HELP =====
void printHelp() {
  Serial.println("\n========================================");
  Serial.println("AVAILABLE COMMANDS");
  Serial.println("========================================");
  Serial.println("pause (p)       - Pause image capture");
  Serial.println("resume (r)      - Resume image capture");
  Serial.println("capture (c)     - Capture image immediately");
  Serial.println("status (s)      - Show system status");
  Serial.println("config          - Show configuration");
  Serial.println("interval [ms]   - Change capture interval");
  Serial.println("                  Example: interval 5000");
  Serial.println("help (h, ?)     - Show this help message");
  Serial.println("========================================");
  Serial.println("\nTip: Commands are case-insensitive");
  Serial.println("========================================\n");
}

// ===== PRINT CONFIGURATION =====
void printConfig() {
  Serial.println("\n========================================");
  Serial.println("CURRENT CONFIGURATION");
  Serial.println("========================================");
  Serial.printf("Brightness Analysis: %s\n", USE_BRIGHTNESS_ANALYSIS ? "ON" : "OFF");
  Serial.printf("Color Analysis: %s\n", USE_COLOR_ANALYSIS ? "ON" : "OFF");
  Serial.printf("Sky Features: %s\n", USE_SKY_FEATURES ? "ON" : "OFF");
  Serial.printf("Frame Size: ");
  
  switch(CAMERA_FRAME_SIZE) {
    case FRAMESIZE_QVGA: Serial.println("QVGA (320x240)"); break;
    case FRAMESIZE_VGA: Serial.println("VGA (640x480)"); break;
    case FRAMESIZE_SVGA: Serial.println("SVGA (800x600)"); break;
    case FRAMESIZE_XGA: Serial.println("XGA (1024x768)"); break;
    default: Serial.println("Unknown"); break;
  }
  
  Serial.printf("JPEG Quality: %d (lower = better)\n", CAMERA_JPEG_QUALITY);
  Serial.printf("Capture Interval: %d ms\n", captureIntervalMs);
  Serial.println("========================================\n");
}

/*
 * ===== SERIAL COMMANDS USAGE =====
 * 
 * Open Serial Monitor (Tools → Serial Monitor)
 * Set baud rate to 115200
 * Make sure "Newline" or "Both NL & CR" is selected in dropdown
 * 
 * Available Commands:
 * 
 * pause / p
 *   - Stops automatic image capture
 *   - System will wait for resume command
 * 
 * resume / r
 *   - Resumes automatic image capture
 * 
 * capture / c
 *   - Takes an immediate photo
 *   - Works even when paused
 * 
 * status / s
 *   - Shows system information
 *   - Uptime, memory, WiFi status
 * 
 * config
 *   - Displays current settings
 *   - Shows which analyses are enabled
 * 
 * interval [milliseconds]
 *   - Changes capture interval
 *   - Example: "interval 30000" for 30 seconds
 *   - Minimum: 1000ms (1 second)
 * 
 * help / h / ?
 *   - Shows command list
 * 
 * Commands are case-insensitive and work with shortcuts.
 */
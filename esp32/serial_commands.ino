/*
 * Serial Commands Module
 * Handles serial input and command processing
 */

#include "globals.h"

// ===== COMMAND PARSER =====

void checkSerialCommands() {
  if (!Serial.available()) return;
  
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  cmd.toLowerCase();
  
  if (cmd == "pause" || cmd == "p") {
    handlePauseCommand();
  }
  else if (cmd == "resume" || cmd == "r") {
    handleResumeCommand();
  }
  else if (cmd == "capture" || cmd == "c") {
    handleCaptureCommand();
  }
  else if (cmd.startsWith("interval ")) {
    handleIntervalCommand(cmd);
  }
  else if (cmd == "status" || cmd == "s") {
    handleStatusCommand();
  }
  else if (cmd.length() > 0) {
    printCommandHelp();
  }
}

// ===== COMMAND HANDLERS =====

void handlePauseCommand() {
  systemPaused = true;
  debugPrint("\n⏸️  PAUSED - Type 'resume' to continue\n");
}

void handleResumeCommand() {
  systemPaused = false;
  debugPrint("\n▶️  RESUMED\n");
}

void handleCaptureCommand() {
  debugPrint("\n📸 Manual capture\n");
  captureAndSend();
}

void handleIntervalCommand(String cmd) {
  int newInterval = cmd.substring(9).toInt();
  
  if (newInterval >= MIN_CAPTURE_INTERVAL_MS) {
    captureInterval = newInterval;
    debugPrintf("\n✓ Interval set to %d ms (%d seconds)\n", 
                captureInterval, captureInterval / 1000);
  } else {
    debugPrintf("\n✗ Invalid interval (min %dms)\n", MIN_CAPTURE_INTERVAL_MS);
  }
}

void handleStatusCommand() {
  printStatus();
}

// ===== STATUS AND HELP =====

void printCommandHelp() {
  #if ENABLE_SERIAL_OUTPUT
    Serial.println("\n❓ Unknown command");
    Serial.println("Available: pause, resume, capture, interval N, status\n");
  #endif
}

void printStatus() {
  #if ENABLE_SERIAL_OUTPUT
    Serial.println("\n========================================");
    Serial.println("STATUS");
    Serial.println("========================================");
    Serial.printf("State: %s\n", systemPaused ? "⏸️  PAUSED" : "▶️  RUNNING");
    Serial.printf("Uptime: %lu seconds\n", millis() / 1000);
    Serial.printf("Interval: %d ms (%d seconds)\n", captureInterval, captureInterval / 1000);
    Serial.printf("Free heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("WiFi: %s (RSSI: %d dBm)\n", 
                  WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected",
                  WiFi.RSSI());
    Serial.printf("Server: %s\n", SERVER_URL);
    Serial.printf("Upload failures: %d\n", uploadFailCount);
    Serial.println("========================================\n");
  #endif
}

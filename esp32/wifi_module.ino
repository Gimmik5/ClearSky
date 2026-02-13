/*
 * WiFi Module
 * Handles WiFi connection, reconnection, and status monitoring
 */

#include "globals.h"

// ===== WIFI INITIALIZATION =====

bool initWiFi() {
  debugPrintf("Connecting to WiFi: %s", WIFI_SSID);
  
  if (!connectToWiFi()) {
    debugPrint("✗ WiFi connection failed");
    return false;
  }
  
  debugPrint("✓ WiFi connected");
  printWiFiInfo();
  
  return true;
}

// ===== WIFI CONNECTION =====

bool connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  int maxAttempts = WIFI_TIMEOUT_SECONDS * 2;
  
  while (WiFi.status() != WL_CONNECTED && attempts < maxAttempts) {
    delay(WIFI_RETRY_DELAY_MS);
    #if ENABLE_SERIAL_OUTPUT
      Serial.print(".");
    #endif
    attempts++;
  }
  
  #if ENABLE_SERIAL_OUTPUT
    Serial.println();
  #endif
  
  return WiFi.status() == WL_CONNECTED;
}

bool checkWiFiConnection() {
  return WiFi.status() == WL_CONNECTED;
}

void reconnectWiFi() {
  debugPrint("✗ WiFi disconnected, reconnecting...");
  initWiFi();
}

// ===== WIFI STATUS =====

void printWiFiInfo() {
  #if ENABLE_SERIAL_OUTPUT
    Serial.print("  ESP32 IP: ");
    Serial.println(WiFi.localIP());
    Serial.printf("  Sending to: %s\n", SERVER_URL);
    Serial.print("  Signal: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  #endif
}

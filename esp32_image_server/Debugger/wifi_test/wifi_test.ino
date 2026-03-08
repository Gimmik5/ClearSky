/*
 * WiFi Connection Test
 * Upload this to verify WiFi credentials and hardware
 */

#include "WiFi.h"

// ===== EDIT THESE =====
const char* WIFI_SSID = "YourActualNetworkName";      // Change this
const char* WIFI_PASSWORD = "your_actual_wifi_password";      // Change this
// ======================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n========================================");
  Serial.println("ESP32 WiFi Test");
  Serial.println("========================================");
  
  Serial.printf("Attempting to connect to: %s\n", WIFI_SSID);
  Serial.println("Connecting");
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {  // 20 second timeout
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi Connected Successfully!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
  } else {
    Serial.println("\n✗ WiFi Connection FAILED");
    Serial.print("Status Code: ");
    Serial.println(WiFi.status());
    
    Serial.println("\nPossible reasons:");
    Serial.println("1. Wrong SSID or password");
    Serial.println("2. WiFi network is 5GHz (ESP32 only supports 2.4GHz)");
    Serial.println("3. Network has special characters in password");
    Serial.println("4. MAC filtering enabled on router");
    Serial.println("5. WiFi antenna not connected properly");
  }
  
  Serial.println("========================================");
}

void loop() {
  // Check connection status every 5 seconds
  delay(5000);
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[%lu] Still connected - IP: %s, RSSI: %d dBm\n", 
                  millis()/1000, 
                  WiFi.localIP().toString().c_str(), 
                  WiFi.RSSI());
  } else {
    Serial.printf("[%lu] Disconnected - Status: %d\n", 
                  millis()/1000, 
                  WiFi.status());
  }
}

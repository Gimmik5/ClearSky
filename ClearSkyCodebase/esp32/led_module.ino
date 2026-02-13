/*
 * LED Module
 * Handles LED blinking for status indication
 */

#include "globals.h"

// ===== LED CONTROL =====

void blinkLED(int times) {
  #if LED_ENABLE
    for (int i = 0; i < times; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(100);
      digitalWrite(LED_PIN, LOW);
      if (i < times - 1) {
        delay(100);
      }
    }
  #endif
}

// ===== STATUS INDICATORS =====

void blinkSuccess() {
  #if LED_ENABLE && LED_BLINK_ON_CAPTURE
    blinkLED(2);  // 2 blinks = successful upload
  #endif
}

void blinkError() {
  #if LED_ENABLE
    blinkLED(5);  // 5 blinks = error
  #endif
}

void blinkCapture() {
  #if LED_ENABLE && LED_BLINK_ON_CAPTURE
    blinkLED(1);  // 1 blink = capturing
  #endif
}

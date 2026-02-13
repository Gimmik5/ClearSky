/*
 * Utilities Module
 * Helper functions for debugging and logging
 */

#include "globals.h"

// ===== DEBUG OUTPUT =====

void debugPrint(const char* message) {
  #if ENABLE_SERIAL_OUTPUT
    Serial.println(message);
  #endif
}

void debugPrintf(const char* format, ...) {
  #if ENABLE_SERIAL_OUTPUT
    char buffer[256];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    Serial.println(buffer);
  #endif
}

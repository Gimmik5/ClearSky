/*
 * Brightness Analysis Module
 * 
 * This file contains the brightness analysis function.
 * It is automatically included when you open the main sketch.
 * 
 * NO #include statements needed here - the main file handles that.
 */

// ===== IMAGE BRIGHTNESS ANALYSIS FUNCTION =====
void analyzeBrightness(camera_fb_t * frame) {
  Serial.println("\n🔍 Analyzing brightness...");
  
  // Variables to calculate average brightness
  long totalBrightness = 0;
  int pixelCount = 0;
  int sampleRate = 100;  // Sample every 100th byte for speed
  
  // Loop through image data (sampling for efficiency)
  for (int i = 0; i < frame->len; i += sampleRate) {
    totalBrightness += frame->buf[i];
    pixelCount++;
  }
  
  // Calculate average brightness (0-255 scale)
  int avgBrightness = totalBrightness / pixelCount;
  
  // Display results
  Serial.printf("   Average Brightness: %d / 255\n", avgBrightness);
  Serial.print("   Sky Condition: ");
  
  // Simple classification based on brightness thresholds from Config.h
  if (avgBrightness > BRIGHTNESS_VERY_BRIGHT) {
    Serial.println("☀️  VERY BRIGHT - Likely clear/sunny");
  } else if (avgBrightness > BRIGHTNESS_BRIGHT) {
    Serial.println("🌤️  BRIGHT - Partly cloudy or hazy");
  } else if (avgBrightness > BRIGHTNESS_MODERATE) {
    Serial.println("⛅ MODERATE - Cloudy");
  } else if (avgBrightness > BRIGHTNESS_DIM) {
    Serial.println("☁️  DIM - Overcast");
  } else {
    Serial.println("🌙 DARK - Night or very dark clouds");
  }
  
  // Calculate a simple "clear sky score" (0-100%)
  int clearSkyScore = map(avgBrightness, 0, 255, 0, 100);
  clearSkyScore = constrain(clearSkyScore, 0, 100);  // Keep it 0-100
  Serial.printf("   Clear Sky Score: %d%%\n", clearSkyScore);
}

/*
 * ===== BRIGHTNESS ANALYSIS EXPLANATION =====
 * 
 * This function samples the JPEG data bytes and averages them
 * to get a rough brightness estimate. It's fast but doesn't
 * look at actual colors.
 * 
 * Sampling: We check every 100th byte instead of every byte
 * to speed things up. This still gives accurate results.
 * 
 * Thresholds are configured in Config.h:
 * - BRIGHTNESS_VERY_BRIGHT (default 180): Clear sunny day
 * - BRIGHTNESS_BRIGHT (default 140): Partly cloudy
 * - BRIGHTNESS_MODERATE (default 100): Cloudy
 * - BRIGHTNESS_DIM (default 60): Overcast
 * 
 * You can adjust these thresholds in Config.h based on your
 * location and typical weather patterns.
 */
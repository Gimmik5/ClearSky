/*
 * Color Analysis Module
 * 
 * This file contains color analysis functions for detecting
 * blue skies, clouds, and weather conditions.
 * 
 * NO #include statements needed here - the main file handles that.
 */

// ===== COLOR ANALYSIS FUNCTION =====
void analyzeColor(camera_fb_t * frame) {
  Serial.println("\n🎨 Analyzing color...");
  
  // STEP 1: Calculate how much memory we need for RGB565
  // RGB565 uses 2 bytes per pixel
  size_t rgb565_len = frame->width * frame->height * 2;
  
  // Allocate memory for RGB565 data
  uint8_t * rgb565_buf = (uint8_t*)malloc(rgb565_len);
  
  if (rgb565_buf == NULL) {
    Serial.println("✗ Failed to allocate memory for RGB conversion!");
    return;
  }
  
  // STEP 2: Convert JPEG to RGB565 format
  bool converted = jpg2rgb565(frame->buf, frame->len, rgb565_buf, JPG_SCALE_NONE);
  
  if (!converted) {
    Serial.println("✗ Failed to convert image to RGB!");
    free(rgb565_buf);
    return;
  }
  
  Serial.println("✓ Image converted to RGB565 format");
  
  // STEP 3: Sample pixels and analyze their colors
  long totalRed = 0;
  long totalGreen = 0;
  long totalBlue = 0;
  int pixelCount = 0;
  
  int totalPixels = frame->width * frame->height;
  int sampleRate = COLOR_SAMPLE_RATE;  // From Config.h
  
  // Loop through pixels
  for (int i = 0; i < totalPixels; i += sampleRate) {
    int byteIndex = i * 2;
    
    // Extract RGB565 pixel
    uint16_t pixel = (rgb565_buf[byteIndex + 1] << 8) | rgb565_buf[byteIndex];
    
    // Convert RGB565 to R, G, B values (0-255 scale)
    int red = ((pixel >> 11) & 0x1F) * 255 / 31;
    int green = ((pixel >> 5) & 0x3F) * 255 / 63;
    int blue = (pixel & 0x1F) * 255 / 31;
    
    totalRed += red;
    totalGreen += green;
    totalBlue += blue;
    pixelCount++;
  }
  
  // STEP 4: Calculate average RGB values
  int avgRed = totalRed / pixelCount;
  int avgGreen = totalGreen / pixelCount;
  int avgBlue = totalBlue / pixelCount;
  
  // STEP 5: Display results
  Serial.printf("   Average Red:   %d / 255\n", avgRed);
  Serial.printf("   Average Green: %d / 255\n", avgGreen);
  Serial.printf("   Average Blue:  %d / 255\n", avgBlue);
  
  // STEP 6: Analyze sky conditions
  analyzeSkyColor(avgRed, avgGreen, avgBlue);
  
  // Free memory
  free(rgb565_buf);
}

// ===== SKY COLOR INTERPRETATION FUNCTION =====
void analyzeSkyColor(int red, int green, int blue) {
  Serial.println("\n🔍 Sky Analysis:");
  
  int brightness = (red + green + blue) / 3;
  
  // Blue dominance indicates clear sky (thresholds from Config.h)
  bool blueDominant = (blue > red + BLUE_DOMINANCE_RED_DIFF) && 
                      (blue > green + BLUE_DOMINANCE_GREEN_DIFF);
  
  // Gray sky has similar R, G, B values
  int colorVariance = abs(red - green) + abs(green - blue) + abs(blue - red);
  bool isGray = colorVariance < GRAY_VARIANCE_THRESHOLD;
  
  Serial.printf("   Overall Brightness: %d / 255\n", brightness);
  Serial.printf("   Color Variance: %d (lower = more gray)\n", colorVariance);
  
  // Sky condition logic
  if (blueDominant && brightness > 100) {
    Serial.println("   Condition: ☀️ CLEAR BLUE SKY - Excellent!");
    Serial.printf("   Blue Sky Score: %d%%\n", map(blue, 0, 255, 0, 100));
  } 
  else if (isGray && brightness > 150) {
    Serial.println("   Condition: 🌫️ BRIGHT OVERCAST - High thin clouds");
  }
  else if (isGray && brightness > 100) {
    Serial.println("   Condition: ☁️ CLOUDY - Thick cloud cover");
  }
  else if (isGray && brightness > 50) {
    Serial.println("   Condition: ⛈️ DARK CLOUDS - Storm possible");
  }
  else if (brightness < 50) {
    Serial.println("   Condition: 🌙 NIGHT TIME or very dark");
  }
  else {
    Serial.println("   Condition: 🌤️ MIXED - Partial clouds");
  }
  
  // Calculate clear sky score
  float blueRatio = (float)blue / (red + green + blue + 1);
  int clearSkyScore = (int)(blueRatio * brightness / 255.0 * 100);
  Serial.printf("   Clear Sky Score: %d%%\n", constrain(clearSkyScore, 0, 100));
}

// ===== ADVANCED: DETECT SPECIFIC SKY FEATURES =====
void detectSkyFeatures(camera_fb_t * frame) {
  Serial.println("\n🌤️ Detecting sky features...");
  
  // Allocate memory
  size_t rgb565_len = frame->width * frame->height * 2;
  uint8_t * rgb565_buf = (uint8_t*)malloc(rgb565_len);
  
  if (rgb565_buf == NULL) {
    Serial.println("✗ Failed to allocate memory!");
    return;
  }
  
  // Convert to RGB
  bool converted = jpg2rgb565(frame->buf, frame->len, rgb565_buf, JPG_SCALE_NONE);
  
  if (!converted) {
    Serial.println("✗ Conversion failed!");
    free(rgb565_buf);
    return;
  }
  
  int totalPixels = frame->width * frame->height;
  int bluePixels = 0;
  int grayPixels = 0;
  int whitePixels = 0;
  int sampleRate = SKY_FEATURES_SAMPLE_RATE;  // From Config.h
  
  // Count different types of pixels
  for (int i = 0; i < totalPixels; i += sampleRate) {
    int byteIndex = i * 2;
    uint16_t pixel = (rgb565_buf[byteIndex + 1] << 8) | rgb565_buf[byteIndex];
    
    int red = ((pixel >> 11) & 0x1F) * 255 / 31;
    int green = ((pixel >> 5) & 0x3F) * 255 / 63;
    int blue = (pixel & 0x1F) * 255 / 31;
    
    int brightness = (red + green + blue) / 3;
    int colorVar = abs(red - green) + abs(green - blue) + abs(blue - red);
    
    // Classify pixel using thresholds from Config.h
    if (blue > BLUE_SKY_MIN_VALUE && 
        blue > red + BLUE_SKY_RED_DIFF && 
        blue > green + BLUE_SKY_GREEN_DIFF) {
      bluePixels++;  // Blue sky
    }
    else if (brightness > WHITE_BRIGHTNESS_MIN && colorVar < WHITE_VARIANCE_MAX) {
      whitePixels++;  // Bright white (clouds or sun)
    }
    else if (colorVar < GRAY_VARIANCE_THRESHOLD) {
      grayPixels++;  // Gray (clouds)
    }
  }
  
  int sampledPixels = totalPixels / sampleRate;
  float bluePercent = (float)bluePixels / sampledPixels * 100;
  float grayPercent = (float)grayPixels / sampledPixels * 100;
  float whitePercent = (float)whitePixels / sampledPixels * 100;
  
  Serial.printf("   Blue Sky Coverage: %.1f%%\n", bluePercent);
  Serial.printf("   Gray Cloud Coverage: %.1f%%\n", grayPercent);
  Serial.printf("   Bright/White Coverage: %.1f%%\n", whitePercent);
  
  // Overall assessment
  if (bluePercent > 60) {
    Serial.println("   Assessment: ☀️ Mostly clear - great conditions!");
  } else if (grayPercent > 60) {
    Serial.println("   Assessment: ☁️ Mostly cloudy");
  } else if (whitePercent > 40) {
    Serial.println("   Assessment: 🌥️ Partly cloudy with bright spots");
  } else {
    Serial.println("   Assessment: 🌤️ Mixed conditions");
  }
  
  free(rgb565_buf);
}

/*
 * ===== COLOR ANALYSIS EXPLANATION =====
 * 
 * These functions convert JPEG to RGB565 and analyze actual colors.
 * All thresholds and parameters are configurable in Config.h
 * 
 * analyzeColor():
 * - Gets average R, G, B values from the image
 * - Uses COLOR_SAMPLE_RATE to control speed vs accuracy
 * - Calls analyzeSkyColor() to interpret the results
 * 
 * analyzeSkyColor():
 * - Determines if sky is blue-dominant (clear)
 * - Uses BLUE_DOMINANCE_RED_DIFF and BLUE_DOMINANCE_GREEN_DIFF
 * - Detects gray conditions (clouds)
 * - Calculates color variance (how uniform the color is)
 * 
 * detectSkyFeatures():
 * - Most detailed analysis
 * - Counts blue, gray, and white pixels separately
 * - Uses SKY_FEATURES_SAMPLE_RATE for pixel sampling
 * - Gives percentage coverage for each type
 * - Slowest but most accurate
 * 
 * Memory requirements:
 * - VGA (640x480): ~600KB for RGB conversion
 * - If you get crashes, reduce CAMERA_FRAME_SIZE in Config.h
 * 
 * Adjusting for your location:
 * - Edit thresholds in Config.h
 * - Test and compare results
 * - Fine-tune based on typical weather in your area
 */
/*
 * Camera Module
 * Handles camera initialization, configuration, and image capture
 */

#include "globals.h"

// ===== CAMERA INITIALIZATION =====

bool initCamera() {
  camera_config_t config;
  
  if (!configureCameraSettings(&config)) {
    return false;
  }
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    debugPrintf("✗ Camera init failed: 0x%x", err);
    return false;
  }
  
  if (!configureCameraSensor()) {
    debugPrint("✗ Camera sensor config failed");
    return false;
  }
  
  debugPrint("✓ Camera initialized");
  printCameraInfo();
  
  return true;
}

// ===== CAMERA CONFIGURATION =====

bool configureCameraSettings(camera_config_t* config) {
  config->ledc_channel = LEDC_CHANNEL_0;
  config->ledc_timer = LEDC_TIMER_0;
  config->pin_d0 = Y2_GPIO_NUM;
  config->pin_d1 = Y3_GPIO_NUM;
  config->pin_d2 = Y4_GPIO_NUM;
  config->pin_d3 = Y5_GPIO_NUM;
  config->pin_d4 = Y6_GPIO_NUM;
  config->pin_d5 = Y7_GPIO_NUM;
  config->pin_d6 = Y8_GPIO_NUM;
  config->pin_d7 = Y9_GPIO_NUM;
  config->pin_xclk = XCLK_GPIO_NUM;
  config->pin_pclk = PCLK_GPIO_NUM;
  config->pin_vsync = VSYNC_GPIO_NUM;
  config->pin_href = HREF_GPIO_NUM;
  config->pin_sscb_sda = SIOD_GPIO_NUM;
  config->pin_sscb_scl = SIOC_GPIO_NUM;
  config->pin_pwdn = PWDN_GPIO_NUM;
  config->pin_reset = RESET_GPIO_NUM;
  config->xclk_freq_hz = 20000000;
  config->pixel_format = PIXFORMAT_JPEG;
  config->frame_size = CAMERA_FRAME_SIZE;
  config->jpeg_quality = CAMERA_JPEG_QUALITY;
  config->fb_count = CAMERA_FB_COUNT;
  
  return true;
}

bool configureCameraSensor() {
  sensor_t* s = esp_camera_sensor_get();
  if (s == NULL) {
    return false;
  }
  
  s->set_brightness(s, CAMERA_BRIGHTNESS);
  s->set_contrast(s, CAMERA_CONTRAST);
  s->set_saturation(s, CAMERA_SATURATION);
  s->set_exposure_ctrl(s, CAMERA_AUTO_EXPOSURE ? 1 : 0);
  s->set_gain_ctrl(s, CAMERA_AUTO_GAIN ? 1 : 0);
  s->set_whitebal(s, CAMERA_AUTO_WHITE_BALANCE ? 1 : 0);
  
  return true;
}

void printCameraInfo() {
  #if ENABLE_SERIAL_OUTPUT && SHOW_DETAILED_OUTPUT
    Serial.print("  Frame size: ");
    switch(CAMERA_FRAME_SIZE) {
      case FRAMESIZE_QVGA: Serial.println("QVGA (320x240)"); break;
      case FRAMESIZE_VGA: Serial.println("VGA (640x480)"); break;
      case FRAMESIZE_SVGA: Serial.println("SVGA (800x600)"); break;
      case FRAMESIZE_XGA: Serial.println("XGA (1024x768)"); break;
      default: Serial.println("Unknown"); break;
    }
    Serial.printf("  JPEG quality: %d\n", CAMERA_JPEG_QUALITY);
  #endif
}

// ===== IMAGE CAPTURE =====

camera_fb_t* captureImage() {
  return esp_camera_fb_get();
}

camera_fb_t* captureImageWithRetry() {
  camera_fb_t* fb = NULL;
  int retries = 0;
  
  while (retries < MAX_CAPTURE_RETRIES) {
    fb = captureImage();
    if (fb) {
      debugPrintf("✓ Captured %d bytes", fb->len);
      return fb;
    }
    
    retries++;
    debugPrintf("Capture retry %d/%d", retries, MAX_CAPTURE_RETRIES);
    delay(RETRY_DELAY_MS);
  }
  
  debugPrint("✗ Capture failed after retries!");
  return NULL;
}

/*
 * Camera Initialization Module
 * 
 * This file contains all camera-related initialization and configuration.
 * NO #include statements needed here - the main file handles that.
 */

// ===== CAMERA INITIALIZATION FUNCTION =====
bool initCamera() {
  // Configure camera settings
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;  // 20MHz clock
  config.pixel_format = PIXFORMAT_JPEG;  // We want JPEG images
  
  // Use configured settings from Config.h
  config.frame_size = CAMERA_FRAME_SIZE;
  config.jpeg_quality = CAMERA_JPEG_QUALITY;
  config.fb_count = CAMERA_FB_COUNT;
  
  #if CAMERA_TEST_PATTERN
    config.grab_mode = CAMERA_GRAB_LATEST;
  #endif
  
  // Initialize the camera with our configuration
  esp_err_t err = esp_camera_init(&config);
  
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return false;
  }
  
  // Get camera sensor for additional adjustments
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    // Apply settings from Config.h
    s->set_brightness(s, CAMERA_BRIGHTNESS);
    s->set_contrast(s, CAMERA_CONTRAST);
    s->set_saturation(s, CAMERA_SATURATION);
    s->set_exposure_ctrl(s, CAMERA_AUTO_EXPOSURE ? 1 : 0);
    s->set_gain_ctrl(s, CAMERA_AUTO_GAIN ? 1 : 0);
    s->set_whitebal(s, CAMERA_AUTO_WHITE_BALANCE ? 1 : 0);
    
    #if CAMERA_TEST_PATTERN
      s->set_colorbar(s, 1);  // Enable test pattern
    #endif
  }
  
  return true;
}

/*
 * ===== CAMERA SENSOR ADJUSTMENTS =====
 * 
 * The sensor_t structure allows you to fine-tune image capture.
 * These settings can dramatically affect sky analysis accuracy.
 * 
 * Key settings for sky detection:
 * - exposure_ctrl: Auto exposure helps with changing light conditions
 * - gain_ctrl: Auto gain adjusts for brightness
 * - whitebal: Auto white balance helps with color accuracy
 * - brightness: Manual adjustment if images are too dark/bright
 * - saturation: Increase to make blue skies more vivid
 * 
 * Experiment with these values and compare the analysis results!
 */
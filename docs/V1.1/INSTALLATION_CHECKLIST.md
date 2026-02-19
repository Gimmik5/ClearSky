# ESP32-CAM Installation Checklist

## ✅ Pre-Upload Checklist

### 1. File Setup
- [ ] Created folder named: `esp32_image_server`
- [ ] Copied ALL 11 files to this folder:
  - [ ] esp32_image_server.ino (main sketch)
  - [ ] ESP32_Config.h
  - [ ] globals.h
  - [ ] server_module.ino
  - [ ] camera_module.ino
  - [ ] wifi_module.ino
  - [ ] upload_module.ino
  - [ ] serial_commands.ino
  - [ ] system_init.ino
  - [ ] led_module.ino
  - [ ] utils.ino

### 2. Configuration
- [ ] Opened ESP32_Config.h
- [ ] Set WIFI_SSID to your network name
- [ ] Set WIFI_PASSWORD to your password
- [ ] Chose mode:
  - [ ] USE_PULL_MODE = true (Server mode)
  - [ ] OR USE_PULL_MODE = false (Sender mode)
- [ ] If Push Mode: Set SERVER_URL to your Python server

### 3. Arduino IDE Setup
- [ ] Arduino IDE installed (version 2.x recommended)
- [ ] ESP32 board support installed
- [ ] Tools → Board → ESP32 Arduino → AI Thinker ESP32-CAM
- [ ] Tools → Port → Selected correct USB port
- [ ] Baud rate set to 115200 in Serial Monitor

### 4. Hardware Connections
- [ ] ESP32-CAM connected to USB-TTL adapter:
  - [ ] GND → GND
  - [ ] 5V → 5V
  - [ ] U0R → TX
  - [ ] U0T → RX
- [ ] GPIO 0 → GND (for upload mode)
- [ ] Camera module connected to ESP32-CAM

## ✅ Upload Checklist

### During Upload
- [ ] GPIO 0 connected to GND
- [ ] Pressed RESET button on ESP32-CAM
- [ ] Clicked Upload button in Arduino IDE
- [ ] Waited for "Connecting..." message
- [ ] Upload completed successfully ("Done uploading")
- [ ] Disconnected GPIO 0 from GND
- [ ] Pressed RESET button again

### After Upload
- [ ] Opened Serial Monitor (115200 baud)
- [ ] Saw startup message
- [ ] WiFi connected successfully
- [ ] IP address displayed
- [ ] Camera initialized
- [ ] Mode displayed (PULL or PUSH)

## ✅ Testing Checklist

### Pull Mode Testing
- [ ] Noted ESP32 IP address from Serial Monitor
- [ ] Opened browser to: http://<ESP32_IP>/
- [ ] Saw server info page
- [ ] Tested: http://<ESP32_IP>/capture
- [ ] Image displayed/downloaded successfully
- [ ] Tested: http://<ESP32_IP>/status
- [ ] JSON data displayed

### Push Mode Testing
- [ ] Python server running on configured port
- [ ] ESP32 sending images automatically
- [ ] Check Serial Monitor for upload status
- [ ] Python server receiving images

### Serial Commands Testing
- [ ] Typed `status` → System info displayed
- [ ] Typed `pause` → System paused
- [ ] Typed `resume` → System resumed
- [ ] Typed `capture` → Manual capture triggered
- [ ] Typed `interval 60000` → Interval changed to 60s

## ✅ Troubleshooting Checklist

### If Compilation Fails:
- [ ] All 11 files in same folder?
- [ ] Folder name matches main .ino file?
- [ ] ESP32 board support installed?
- [ ] Correct board selected?
- [ ] All files saved?

### If Upload Fails:
- [ ] GPIO 0 connected to GND?
- [ ] Correct USB port selected?
- [ ] Reset button pressed before upload?
- [ ] USB cable supports data (not just power)?
- [ ] Try different USB port?

### If WiFi Fails:
- [ ] Correct SSID and password?
- [ ] Using 2.4GHz network (not 5GHz)?
- [ ] Network within range?
- [ ] Serial Monitor shows connection attempts?
- [ ] Router allows new devices?

### If Camera Fails:
- [ ] Camera cable properly connected?
- [ ] Camera module not damaged?
- [ ] Serial Monitor shows camera errors?
- [ ] Try reseating camera cable?

## ✅ Success Indicators

### Pull Mode Success:
✓ Serial shows: "Mode: PULL (Server)"
✓ Web server started message
✓ Can access http://<IP>/capture
✓ Images download successfully

### Push Mode Success:
✓ Serial shows: "Mode: PUSH (Sender)"
✓ Upload success messages
✓ Python server receives images
✓ No upload errors in Serial Monitor

## 📋 Expected Serial Output (Pull Mode)

```
========================================
ESP32-CAM Image Server/Sender V1
========================================
Connecting to WiFi: YourNetwork
.........
[OK] WiFi connected
  ESP32 IP: 192.168.1.123
  Mode: PULL (Server)
  Signal: -45 dBm

[OK] Camera initialized
  Frame size: VGA (640x480)
  JPEG quality: 10

[SERVER] Web Server Started
  Endpoints:
    http://192.168.1.123/          - Server info
    http://192.168.1.123/capture   - Capture image
    http://192.168.1.123/status    - System status

========================================
Ready - Server Mode
========================================
```

## 📋 Expected Serial Output (Push Mode)

```
========================================
ESP32-CAM Image Server/Sender V1
========================================
Connecting to WiFi: YourNetwork
.........
[OK] WiFi connected
  ESP32 IP: 192.168.1.123
  Sending to: http://192.168.1.100:5000/upload
  Mode: PUSH (Sender)
  Signal: -45 dBm

[OK] Camera initialized
  Frame size: VGA (640x480)
  JPEG quality: 10

========================================
Ready - Sender Mode
========================================

Commands:
  pause / p      - Stop captures
  resume / r     - Resume captures
  capture / c    - Capture now
  interval N     - Set interval (ms)
  status / s     - Show status
========================================

----------------------------------------
[CAPTURE] Capturing image...
[OK] Captured 45678 bytes
[SUCCESS] Sent to server
Next capture in 30 seconds
----------------------------------------
```

## 🎉 Final Checklist

- [ ] Code compiles without errors
- [ ] Code uploads successfully
- [ ] ESP32 boots and connects to WiFi
- [ ] Camera initializes properly
- [ ] Mode is correct (Pull or Push)
- [ ] Testing successful
- [ ] Ready for deployment!

---

**If all boxes are checked, your ESP32-CAM is ready to use! 🚀**

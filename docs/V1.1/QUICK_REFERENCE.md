# ESP32-CAM Quick Reference Card

## ðŸš€ Quick Setup (3 Steps)

### 1. Edit ESP32_Config.h
```cpp
// WiFi Settings
const char* WIFI_SSID = "YourWiFiName";
const char* WIFI_PASSWORD = "YourPassword";

// Choose Mode
#define USE_PULL_MODE true  // true=Server, false=Sender
```

### 2. Upload Files
Place all files in folder named: `esp32_image_server/`

### 3. Upload to ESP32
Open `esp32_image_server.ino` in Arduino IDE and click Upload

---

## ðŸ"Œ Pin Connections for Upload

```
ESP32-CAM     USB-TTL Adapter
---------     ---------------
GND    <----> GND
5V     <----> 5V
U0R    <----> TX
U0T    <----> RX
GPIO 0 <----> GND (during upload only!)
```

**Upload Steps:**
1. Connect GPIO 0 to GND
2. Press RESET on ESP32-CAM  
3. Click Upload in Arduino IDE
4. Wait for "Done uploading"
5. Disconnect GPIO 0 from GND
6. Press RESET again

---

## ðŸ'» Serial Monitor Commands

**Baud Rate:** 115200

| Command | Action |
|---------|--------|
| `status` | Show system info |
| `pause` | Stop capturing |
| `resume` | Resume capturing |
| `capture` | Take photo now |
| `interval 30000` | Set 30s interval |
| `help` | Show all commands |

---

## ðŸŒ Mode Selection

### PULL MODE (Recommended)
```cpp
#define USE_PULL_MODE true
```
- ESP32 acts as server
- Python fetches images: `GET http://<ESP32_IP>/capture`
- More reliable
- Lower power

### PUSH MODE
```cpp
#define USE_PULL_MODE false
#define SERVER_URL "http://192.168.1.100:5000/upload"
```
- ESP32 uploads automatically
- Captures every N seconds
- Traditional approach

---

## ðŸ" Testing Your Setup

### 1. Check Serial Monitor
```
âœ" WiFi connected!
  IP: 192.168.1.123
  Signal: -45 dBm

Mode: PULL (Server)

ðŸŒ Web Server Started
  Endpoints:
    http://192.168.1.123/          - Server info
    http://192.168.1.123/capture   - Capture image
    http://192.168.1.123/status    - System status
```

### 2. Test from Browser (Pull Mode)
```
http://192.168.1.123/capture
```
Should display/download a JPEG image

### 3. Test Status Endpoint
```
http://192.168.1.123/status
```
Should show JSON with system info

---

## âš™ï¸ Common Settings

### Image Quality
```cpp
#define CAMERA_FRAME_SIZE FRAMESIZE_VGA  // 640x480
#define CAMERA_JPEG_QUALITY 10            // 0-63, lower=better
```

### Capture Timing (Push Mode)
```cpp
#define DEFAULT_CAPTURE_INTERVAL_MS 30000  // 30 seconds
```

### LED Indicator
```cpp
#define LED_ENABLE false              // Turn LED on/off
#define LED_BLINK_ON_CAPTURE true     // Blink when capturing
```

### Debug Output
```cpp
#define ENABLE_SERIAL_OUTPUT true     // Enable Serial prints
#define SHOW_DETAILED_OUTPUT true     // Verbose output
```

---

## ðŸ›  Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| **Won't compile** | Install ESP32 board support in Arduino IDE |
| **Won't upload** | Connect GPIO 0 to GND, press RESET, try upload |
| **No WiFi** | Check credentials, ensure 2.4GHz network |
| **No camera** | Re-seat camera cable, check for damage |
| **Can't access server** | Check IP from Serial Monitor, verify same network |
| **Upload fails** | Verify SERVER_URL matches Python server IP |

---

## ðŸ"‹ Required Files Checklist

- [ ] esp32_image_server.ino (MAIN - updated)
- [ ] ESP32_Config.h (UPDATED with fixes)
- [ ] globals.h (UPDATED with HTTPClient)
- [ ] server_module.ino (NEW for Pull Mode)
- [ ] camera_module.ino
- [ ] wifi_module.ino  
- [ ] upload_module.ino
- [ ] serial_commands.ino
- [ ] led_module.ino
- [ ] system_init.ino
- [ ] utils.ino

All files must be in the same folder!

---

## 🎯 Python Integration Examples

### Pull Mode (Python fetches)
```python
import requests

esp32_ip = "192.168.1.123"
response = requests.get(f"http://{esp32_ip}/capture")

if response.status_code == 200:
    with open("image.jpg", "wb") as f:
        f.write(response.content)
```

### Push Mode (ESP32 uploads)
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    image_data = request.data
    with open("image.jpg", "wb") as f:
        f.write(image_data)
    return "OK", 200

app.run(host='0.0.0.0', port=5000)
```

---

## 📞 Support

- Serial Monitor: 115200 baud for debug info
- LED Patterns:
  - Single blink: Capturing
  - 2 quick blinks: Success
  - 3 quick blinks: Error
  
- Check FIX_GUIDE.md for detailed troubleshooting

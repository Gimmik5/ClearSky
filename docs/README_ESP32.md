# ESP32-CAM V1 Modular Multi-File Structure

This version splits the ESP32 code into multiple files for better organization and maintainability.

## File Structure

```
esp32_v1_modular/
├── esp32_simple_sender_v1.ino  # Main file (setup & loop only)
├── globals.h                    # Global variables & function declarations
├── ESP32_Config.h              # Configuration settings
├── system_init.ino             # System initialization
├── camera_module.ino           # Camera functions
├── wifi_module.ino             # WiFi functions
├── upload_module.ino           # Image upload & HTTP
├── serial_commands.ino         # Command handling
├── led_module.ino              # LED control
└── utils.ino                   # Utility functions
```

## Module Breakdown

### **esp32_simple_sender_v1.ino** (Main)
- `setup()` - System initialization
- `loop()` - Main program loop

### **globals.h** (Header)
- Global variable declarations
- All function prototypes
- Shared includes

### **ESP32_Config.h** (Configuration)
- WiFi credentials
- Server URL
- Camera settings
- Timing & behavior settings

### **system_init.ino** (Initialization)
- `initSystem()` - Serial setup
- `initLED()` - LED initialization
- `initWatchdog()` - Watchdog timer setup
- `printStartupInfo()` - Display startup menu
- **Global variable definitions**

### **camera_module.ino** (Camera)
- `initCamera()` - Camera initialization
- `configureCameraSettings()` - Hardware config
- `configureCameraSensor()` - Sensor settings
- `printCameraInfo()` - Display info
- `captureImage()` - Single capture
- `captureImageWithRetry()` - Capture with retry

### **wifi_module.ino** (WiFi)
- `initWiFi()` - WiFi initialization
- `connectToWiFi()` - Connection logic
- `checkWiFiConnection()` - Check status
- `reconnectWiFi()` - Reconnection
- `printWiFiInfo()` - Display info

### **upload_module.ino** (Upload)
- `captureAndSend()` - Main workflow
- `uploadImage()` - HTTP upload setup
- `sendHTTPRequest()` - POST request
- `handleUploadSuccess()` - Success handler
- `handleUploadFailure()` - Error handler

### **serial_commands.ino** (Commands)
- `checkSerialCommands()` - Command parser
- `handlePauseCommand()` - Pause capture
- `handleResumeCommand()` - Resume capture
- `handleCaptureCommand()` - Manual capture
- `handleIntervalCommand()` - Change interval
- `handleStatusCommand()` - Show status
- `printCommandHelp()` - Help text
- `printStatus()` - Status display

### **led_module.ino** (LED)
- `blinkLED()` - Generic blink
- `blinkSuccess()` - Success indicator
- `blinkError()` - Error indicator
- `blinkCapture()` - Capture indicator

### **utils.ino** (Utilities)
- `debugPrint()` - Simple debug output
- `debugPrintf()` - Formatted debug output

## How to Use

1. **Edit ESP32_Config.h**:
   - Set your WiFi credentials
   - Set your server URL
   - Configure camera settings

2. **Upload to ESP32**:
   - Open `esp32_simple_sender_v1.ino` in Arduino IDE
   - All `.ino` files in the same folder will be compiled together
   - Upload to your ESP32-CAM

3. **Monitor Serial Output**:
   - Open Serial Monitor at 115200 baud
   - Use commands: pause, resume, capture, interval, status

## Benefits of Multi-File Structure

✅ **Separation of Concerns**: Each module has a single, clear purpose
✅ **Easy Navigation**: Find functions quickly by module name
✅ **Independent Development**: Work on modules without affecting others
✅ **Better Testing**: Test individual modules separately
✅ **Cleaner Code**: Smaller files are easier to read and understand
✅ **Team Collaboration**: Multiple people can work on different modules
✅ **Maintainability**: Bugs are easier to isolate and fix

## Arduino IDE Behavior

In Arduino IDE:
- All `.ino` files in the same directory are automatically compiled together
- They are concatenated in alphabetical order
- The file with the same name as the folder must contain `setup()` and `loop()`
- `globals.h` is included in each module to access shared variables and functions

## Adding New Features

To add a new feature:
1. Determine which module it belongs to
2. Add function declaration to `globals.h`
3. Implement function in appropriate `.ino` file
4. Call the function from main loop or another module

## Python Server Integration

This modular ESP32 code is designed to work with a Python server that:
- Receives images via HTTP POST
- Performs analysis/processing on the PC
- Returns results to the ESP32

See Python server files for details.

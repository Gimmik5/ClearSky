# ESP32-CAM SD Card Implementation - Quick Start Guide

## 🎯 Goal
Add SD card functionality to your ESP32-CAM project for:
- Local image backup (before upload to server)
- Data logging (capture metadata to CSV)
- Offline operation capability
- **Verify everything works WITHOUT needing a PC card reader!**

---

## 📋 Prerequisites

### Hardware
- ✅ ESP32-CAM module
- ✅ MicroSD card (8GB-32GB recommended)
- ✅ Card formatted as **FAT32**

### Check Your SD Card
1. Insert SD card into any device that can read it (phone, camera, etc.)
2. Format as **FAT32** (NOT exFAT, NOT NTFS)
3. Safely eject
4. Insert into ESP32-CAM SD card slot (metal contacts facing toward PCB)

**Important:** Insert SD card BEFORE powering on ESP32!

---

## 🚀 Step 1: Test SD Card Functionality

### Upload Standalone Test Script

1. **Open Arduino IDE**
2. **Open the file:** `sd_card_test.ino`
3. **Select your board:** AI Thinker ESP32-CAM
4. **Upload to ESP32**
5. **Open Serial Monitor:** Set to **115200 baud**

### What You'll See

```
========================================
ESP32-CAM SD Card Test
========================================

Test 1: Initializing SD Card...
✅ SD Card initialized successfully!

Test 2: Card Information
----------------------------------------
Card Type: SDHC
Card Size: 16384 MB
Total Space: 16064 MB
Used Space: 128 MB
Free Space: 15936 MB
✅ Card info retrieved

Test 3: Writing Test Files
----------------------------------------
✅ Created /test.txt
✅ Created /data.csv
✅ Created /testdir/
✅ Created /testdir/nested.txt

Test 4: Reading Test Files
----------------------------------------
Contents of /test.txt:
---
ESP32-CAM SD Card Test
This is a test file.
Timestamp: 5234
---
✅ File read successfully

Test 5: Listing All Files
----------------------------------------
Listing directory: /
  DIR : /testdir
  FILE: test.txt		SIZE: 67
  FILE: data.csv		SIZE: 89
✅ Directory listing complete

Test 6: Appending to File
----------------------------------------
✅ Data appended to /test.txt
...

🎉 All tests passed!
========================================

Your SD card is working correctly!
```

### ❌ If Tests Fail

**"SD Card init failed":**
- Check SD card is inserted (metal contacts toward PCB)
- Power cycle ESP32 with card inserted
- Try reformatting card as FAT32
- Try a different SD card (some cards incompatible)

**"Failed to open file":**
- Card might be write-protected
- Card might be corrupt
- Reformat as FAT32

---

## 🔧 Step 2: Integrate Into Your Project

### 2.1 Add Configuration to ESP32_Config.h

Add these lines to your `ESP32_Config.h`:

```cpp
// ===== SD CARD SETTINGS =====
#define SD_CARD_ENABLE true            // Enable SD card
#define SD_SAVE_IMAGES true            // Save images to SD
#define SD_LOG_CAPTURES true           // Log metadata to CSV
#define SD_IMAGE_DIR "/images"         // Image directory
#define SD_LOG_DIR "/logs"             // Log directory
#define SD_MAX_IMAGES 100              // Max images before cleanup
#define SD_MIN_FREE_SPACE_MB 50        // Min free space (MB)
#define SD_AUTO_DELETE_OLD true        // Auto-delete when full
```

### 2.2 Update globals.h

Add these function declarations to your `globals.h`:

```cpp
// SD Card functions
bool initSDCard();
bool saveImageToSD(camera_fb_t* fb, const char* filename);
String generateImageFilename();
bool logCaptureToSD(const char* timestamp, size_t imageSize, bool uploadSuccess);
void cleanupOldImages();
void printSDStatus();
void listSDFiles();
bool sdIsAvailable();
int sdGetImageCount();
```

### 2.3 Add sd_card_module.ino

Copy `sd_card_module.ino` into your ESP32 project folder (same directory as your .ino files).

### 2.4 Update system_init.ino

Add SD card initialization to your `setup()`:

```cpp
void setup() {
  initSystem();
  initLED();
  initWatchdog();
  
  // Initialize camera
  if (!initCamera()) {
    debugPrint("❌ Camera init failed - halting");
    while(1) delay(1000);
  }
  
  // Initialize WiFi
  if (!initWiFi()) {
    debugPrint("❌ WiFi init failed - halting");
    while(1) delay(1000);
  }
  
  // Initialize SD Card (NEW!)
  initSDCard();  // Non-blocking - continues even if fails
  
  printStartupInfo();
  
  lastCaptureTime = millis();
  delay(1000);
  captureAndSend();
}
```

### 2.5 Update upload_module.ino

Modify `captureAndSend()` to save to SD card:

```cpp
void captureAndSend() {
  debugPrint("📷 Capturing image...");
  blinkCapture();
  
  camera_fb_t* fb = captureImageWithRetry();
  if (!fb) {
    return;
  }
  
  // NEW: Save to SD card first
  #if SD_CARD_ENABLE
    if (sdIsAvailable()) {
      String filename = generateImageFilename();
      saveImageToSD(fb, filename.c_str());
    }
  #endif
  
  // Upload to server
  bool uploadSuccess = false;
  if (checkWiFiConnection()) {
    uploadSuccess = uploadImage(fb);
    if (uploadSuccess) {
      blinkSuccess();
    } else {
      blinkError();
    }
  }
  
  // NEW: Log capture to CSV
  #if SD_CARD_ENABLE
    char timestamp[32];
    snprintf(timestamp, sizeof(timestamp), "%lu", millis());
    logCaptureToSD(timestamp, fb->len, uploadSuccess);
    
    // Cleanup if needed
    cleanupOldImages();
  #endif
  
  esp_camera_fb_return(fb);
}
```

### 2.6 Add Serial Commands

Add to `serial_commands.ino`:

```cpp
else if (cmd == "sd" || cmd == "sdstatus") {
  printSDStatus();
}
else if (cmd == "sdlist") {
  listSDFiles();
}
```

---

## 🧪 Step 3: Test Integration

### Upload and Monitor

1. Upload modified code to ESP32
2. Open Serial Monitor (115200 baud)
3. Watch startup sequence

### Expected Output

```
========================================
ESP32-CAM Image Sender V1 Modular
========================================
✅ System initialized
✅ Camera initialized
✅ WiFi connected

Initializing SD Card...
✅ SD Card initialized
  Card Type: SDHC
  Card Size: 16384 MB
  Free Space: 15936 MB
✅ Created /images
✅ Created /logs

Ready to send images
========================================
```

### Test Capture

Type in Serial Monitor:
```
capture
```

Expected output:
```
📷 Capturing image...
✅ Captured 47832 bytes
✅ Saved to SD: /images/img_12345.jpg (47832 bytes)
✅ Sent to server (HTTP 200)
```

### Check SD Card Status

Type:
```
sd
```

Output:
```
SD Card Status:
----------------------------------------
  ✅ Available
  Total: 16384 MB
  Used: 148 MB
  Free: 16236 MB
  Images: 5
----------------------------------------
```

### List Files

Type:
```
sdlist
```

Output:
```
SD Card Contents:
========================================
📁 images
  📄 img_12345.jpg (47832 bytes)
  📄 img_12346.jpg (45123 bytes)
  📄 img_12347.jpg (48234 bytes)
📁 logs
  📄 captures.csv (512 bytes)
========================================
```

---

## 🌐 Step 4: Web Interface (No Card Reader Needed!)

The web interface lets you browse SD card files from your browser!

### How It Works

1. ESP32 serves file listings
2. You browse files in web browser
3. Download files directly to your PC
4. Delete files remotely

### Setup (Optional)

This requires adding HTTP endpoints to serve files. For now, the Serial Monitor is your primary verification method.

**Future enhancement:** Full web-based SD card browser with download/delete capabilities.

---

## 📊 Verification Checklist

### ✅ Basic Functionality
- [ ] SD card initializes on boot
- [ ] Card info displays in Serial Monitor
- [ ] Files can be created
- [ ] Files can be read back
- [ ] Directory listing works

### ✅ Image Backup
- [ ] Images save to SD card
- [ ] Filenames are generated correctly
- [ ] File sizes match captured size
- [ ] Multiple captures work

### ✅ Logging
- [ ] captures.csv is created
- [ ] Each capture is logged
- [ ] Log includes timestamp, size, upload status

### ✅ Space Management
- [ ] Free space is monitored
- [ ] Old images auto-delete when limit reached
- [ ] Cleanup maintains minimum free space

---

## 🔍 Troubleshooting

### SD Card Not Detected

**Symptoms:**
```
❌ SD Card init failed
```

**Solutions:**
1. Check card is inserted (power off first!)
2. Reformat as FAT32
3. Try different card (some incompatible)
4. Check card size (32GB max recommended)
5. Ensure metal contacts face PCB

### Files Not Saving

**Symptoms:**
```
❌ Failed to open /images/img_12345.jpg
```

**Solutions:**
1. Check free space: `sd` command
2. Check directories exist
3. Card might be write-protected
4. Card might be corrupt

### Can't Read Files Back

**Symptoms:**
```
❌ Failed to open test.txt for reading
```

**Solutions:**
1. File might not have been saved
2. Filename might be wrong
3. Power cycle ESP32
4. Reformat card

### Low Performance

**Symptoms:**
- Slow capture times
- Upload delays

**Solutions:**
1. Use good quality SD card (Class 10)
2. Reduce image size (QVGA instead of VGA)
3. Disable SD logging: `SD_LOG_CAPTURES false`

---

## 📈 Next Steps

### Phase 1: Current ✅
- SD card initialization
- Image backup
- CSV logging
- Serial verification

### Phase 2: Enhanced Storage
- Organized by date folders (`/images/2026/02/05/`)
- Multiple file formats (JSON metadata)
- Compression for old images

### Phase 3: Web Interface
- Browse files via web browser
- Download files directly
- Delete files remotely
- View thumbnails

### Phase 4: Offline Operation
- Store images when WiFi unavailable
- Batch upload when WiFi restored
- Sync status tracking

---

## 💡 Usage Tips

### Daily Operation

1. **Monitor space:** Check `sd` command regularly
2. **Export data:** Download captures.csv for analysis
3. **Backup images:** Let auto-cleanup run or manually download important ones

### Best Practices

- **Format:** Always use FAT32
- **Size:** 8-32GB cards work best
- **Quality:** Use Class 10 or better
- **Backup:** Download important images via Serial before they auto-delete

### Serial Commands Reference

```
sd        - Show SD card status
sdlist    - List all files
capture   - Capture and save image
status    - Show overall system status
```

---

## 🎯 Success Criteria

You know it's working when:

✅ SD card initializes on boot
✅ Each capture saves to SD card
✅ Can list files via `sdlist`
✅ captures.csv updates with each capture
✅ Free space decreases with each image
✅ Auto-cleanup runs when limit reached

---

## 🆘 Getting Help

If you're stuck:

1. **Check Serial output** - Most issues show here
2. **Try test script** - `sd_card_test.ino` isolates SD issues
3. **Reformat card** - Fixes 90% of problems
4. **Try different card** - Some cards incompatible

---

## 📝 Summary

**What you have:**
- SD card backup for every image
- CSV logging of all captures
- Auto space management
- Serial-based verification (no card reader needed!)

**What you can do:**
- Run completely offline (backup mode)
- Recover from upload failures
- Track all captures in CSV
- Monitor storage via Serial

**What's next:**
- Web-based file browser
- Offline operation mode
- Date-organized storage
- Image compression

---

**Your ESP32-CAM now has professional-grade local storage!** 💾✨

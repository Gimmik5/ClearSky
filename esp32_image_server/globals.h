/*
 * Global Variables and Function Declarations - V1.1 PULL Mode
 * Shared across all module files
 */

#ifndef GLOBALS_H
#define GLOBALS_H

#include "esp_camera.h"
#include "WiFi.h"
#include "WebServer.h"
#include "HTTPClient.h"
#include "SD_MMC.h"
#include "FS.h"
#include <vector>
#include <algorithm>
#include "ESP32_Config.h"

// ===== GLOBAL VARIABLES =====

// Capture / system state
extern bool          systemPaused;
extern unsigned long lastCaptureTime;
extern int           captureInterval;
extern int           uploadFailCount;

// Server state (defined in server_module.ino)
extern unsigned long captureCount;
extern unsigned long lastCaptureMs;

// Web server instance (defined in server_module.ino)
extern WebServer server;

// V1.1 SD card state
extern bool sdCardAvailable;   // true after successful initSDCard()
extern int  sdQueueCount;      // Approximate count of images in queue

// SD file info struct for browser
struct SDFileInfo {
  String name;
  String path;
  size_t size;
  bool is_directory;
};

// ===== FUNCTION DECLARATIONS =====

// -- System initialization (system_init.ino) --
void initSystem();
void initLED();
void initWatchdog();
void printStartupInfo();

// -- Camera (camera_module.ino) --
bool         initCamera();
bool         configureCameraSettings(camera_config_t* config);
bool         configureCameraSensor();
void         printCameraInfo();
camera_fb_t* captureImage();
camera_fb_t* captureImageWithRetry();

// -- WiFi (wifi_module.ino) --
bool initWiFi();
bool connectToWiFi();
bool checkWiFiConnection();
void reconnectWiFi();
void printWiFiInfo();

// -- Server (server_module.ino) --
void initServer();
void handleServerClients();
void printServerInfo();
void handleRoot();
void handleCapture();
void handleStatus();
void handleNotFound();
void handleQueueList();         // V1.1
void handleQueueServe();        // V1.1
void handleQueueDelete();       // V1.1
bool isPollerActive();          // V1.1

// -- Upload (upload_module.ino) - for Push Mode only, not used in Pull
void captureAndSend();
bool uploadImage(camera_fb_t* fb);
bool sendHTTPRequest(HTTPClient* http, camera_fb_t* fb);
void handleUploadSuccess(String response);
void handleUploadFailure(int httpCode);

// -- SD card (sd_module.ino) --
bool    initSDCard();
int     getSDUsagePercent();
void    checkAndCleanStorage();
String  saveImageToSD(camera_fb_t* fb, const String& timestamp);
uint8_t* readImageFromSD(const String& filename, size_t& outSize);
bool    deleteImageFromSD(const String& filename);
int     countQueuedImages();
void    getQueuedImageList(std::vector<String>& files);
void    printSDStatus();

// -- Time (time_module.ino) --
void   initNTP();
bool   isNTPSynced();
String getTimestamp();

// -- Serial commands (serial_commands.ino) --
void checkSerialCommands();
void handlePauseCommand();
void handleResumeCommand();
void handleCaptureCommand();
void handleIntervalCommand(String cmd);
void handleStatusCommand();
void printCommandHelp();
void printStatus();

// -- LED (led_module.ino) --
void blinkLED(int times);
void blinkSuccess();
void blinkError();
void blinkCapture();

// -- Utilities (utils.ino) --
void debugPrint(const char* message);
void debugPrintf(const char* format, ...);

// -- SD Browser (sd_browser.ino) --
void handleSDList();
void handleSDBrowse();
void handleSDFile();
void handleSDDelete();
void handleSDStats();

// -- Control (control_module.ino) --
void handleControlPause();
void handleControlResume();
void handleControlCapture();
void handleControlStatus();

#endif // GLOBALS_H

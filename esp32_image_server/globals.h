/*
 * Global Variables and Function Declarations
 * Shared across all module files
 */

#ifndef GLOBALS_H
#define GLOBALS_H

#include "esp_camera.h"
#include "WiFi.h"
#include "WebServer.h"
#include "HTTPClient.h"  // Added for upload functionality
#include "ESP32_Config.h"

// ===== GLOBAL VARIABLES =====
extern bool          systemPaused;
extern unsigned long lastCaptureTime;
extern int           captureInterval;
extern int           uploadFailCount;

// Server state (defined in server_module.ino)
extern unsigned long captureCount;
extern unsigned long lastCaptureMs;

// Web server instance (defined in server_module.ino)
extern WebServer server;


// ===== FUNCTION DECLARATIONS =====

// System initialization (defined in system_init.ino)
void initSystem();
void initLED();
void initWatchdog();
void printStartupInfo();

// Camera functions (defined in camera_module.ino)
bool initCamera();
bool configureCameraSettings(camera_config_t* config);
bool configureCameraSensor();
void printCameraInfo();
camera_fb_t* captureImage();
camera_fb_t* captureImageWithRetry();

// WiFi functions (defined in wifi_module.ino)
bool initWiFi();
bool connectToWiFi();
bool checkWiFiConnection();
void reconnectWiFi();
void printWiFiInfo();

// Server functions (defined in server_module.ino)
void initServer();
void handleServerClients();
void printServerInfo();
void handleRoot();
void handleCapture();
void handleStatus();
void handleNotFound();

// Upload functions (defined in upload_module.ino) - for Push Mode
void captureAndSend();
bool uploadImage(camera_fb_t* fb);
bool sendHTTPRequest(HTTPClient* http, camera_fb_t* fb);
void handleUploadSuccess(String response);
void handleUploadFailure(int httpCode);

// Serial command functions (defined in serial_commands.ino)
void checkSerialCommands();
void handlePauseCommand();
void handleResumeCommand();
void handleCaptureCommand();
void handleIntervalCommand(String cmd);
void handleStatusCommand();
void printCommandHelp();
void printStatus();

// LED functions (defined in led_module.ino)
void blinkLED(int times);
void blinkSuccess();
void blinkError();
void blinkCapture();

// Utility functions (defined in utils.ino)
void debugPrint(const char* message);
void debugPrintf(const char* format, ...);

#endif // GLOBALS_H

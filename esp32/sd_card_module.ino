/*
 * SD Card Module
 * Handles SD card initialization, image backup, CSV logging, and auto-cleanup
 * 
 * Requires SD_CARD_ENABLE true in ESP32_Config.h
 */

#include "globals.h"
#include "SD_MMC.h"
#include "FS.h"

// ===== INTERNAL STATE =====

static bool sdAvailable = false;
static int sdImageCount = 0;

// ===== INITIALISATION =====

bool initSDCard() {
  #if !SD_CARD_ENABLE
    return false;
  #endif

  debugPrint("Initializing SD Card...");

  if (!SD_MMC.begin("/sdcard", true)) {  // true = 1-bit mode (compatible with GPIO)
    debugPrint("x SD Card init failed");
    sdAvailable = false;
    return false;
  }

  uint8_t cardType = SD_MMC.cardType();
  if (cardType == CARD_NONE) {
    debugPrint("x No SD card attached");
    sdAvailable = false;
    return false;
  }

  sdAvailable = true;

  #if ENABLE_SERIAL_OUTPUT
    Serial.println("✔ SD Card initialized");
    Serial.printf("  Card Type: %s\n", 
      cardType == CARD_MMC  ? "MMC"  :
      cardType == CARD_SD   ? "SD"   :
      cardType == CARD_SDHC ? "SDHC" : "UNKNOWN");
    Serial.printf("  Card Size: %llu MB\n", SD_MMC.cardSize() / (1024 * 1024));
    Serial.printf("  Free Space: %llu MB\n", 
                  (SD_MMC.totalBytes() - SD_MMC.usedBytes()) / (1024 * 1024));
  #endif

  // Create required directories
  if (!SD_MMC.exists(SD_IMAGE_DIR)) {
    SD_MMC.mkdir(SD_IMAGE_DIR);
    debugPrint("✔ Created /images");
  }
  if (!SD_MMC.exists(SD_LOG_DIR)) {
    SD_MMC.mkdir(SD_LOG_DIR);
    debugPrint("✔ Created /logs");
  }

  sdImageCount = countSDImages();
  return true;
}

// ===== IMAGE SAVING =====

bool saveImageToSD(camera_fb_t* fb, const char* filename) {
  if (!sdAvailable || !fb) return false;

  #if !SD_SAVE_IMAGES
    return false;
  #endif

  // Build full path
  char filepath[64];
  snprintf(filepath, sizeof(filepath), "%s/%s", SD_IMAGE_DIR, filename);

  File file = SD_MMC.open(filepath, FILE_WRITE);
  if (!file) {
    debugPrintf("x Failed to open %s", filepath);
    return false;
  }

  file.write(fb->buf, fb->len);
  file.close();

  sdImageCount++;
  debugPrintf("✔ Saved to SD: %s (%u bytes)", filepath, fb->len);
  return true;
}

String generateImageFilename() {
  char filename[32];
  snprintf(filename, sizeof(filename), "img_%lu.jpg", millis());
  return String(filename);
}

// ===== CSV LOGGING =====

bool logCaptureToSD(const char* timestamp, size_t imageSize, bool uploadSuccess) {
  if (!sdAvailable) return false;

  #if !SD_LOG_CAPTURES
    return false;
  #endif

  char logPath[64];
  snprintf(logPath, sizeof(logPath), "%s/captures.csv", SD_LOG_DIR);

  // Write header if file doesn't exist
  if (!SD_MMC.exists(logPath)) {
    File header = SD_MMC.open(logPath, FILE_WRITE);
    if (header) {
      header.println("timestamp,image_size,upload_success,free_space_mb");
      header.close();
    }
  }

  File log = SD_MMC.open(logPath, FILE_APPEND);
  if (!log) {
    debugPrint("x Failed to open captures.csv");
    return false;
  }

  uint64_t freeMB = (SD_MMC.totalBytes() - SD_MMC.usedBytes()) / (1024 * 1024);
  log.printf("%s,%u,%d,%llu\n", timestamp, imageSize, uploadSuccess ? 1 : 0, freeMB);
  log.close();
  return true;
}

// ===== AUTO CLEANUP =====

void cleanupOldImages() {
  if (!sdAvailable) return;

  #if !SD_AUTO_DELETE_OLD
    return;
  #endif

  uint64_t freeMB = (SD_MMC.totalBytes() - SD_MMC.usedBytes()) / (1024 * 1024);
  bool tooManyImages = sdImageCount > SD_MAX_IMAGES;
  bool lowSpace = freeMB < SD_MIN_FREE_SPACE_MB;

  if (!tooManyImages && !lowSpace) return;

  debugPrint("SD cleanup triggered...");

  File dir = SD_MMC.open(SD_IMAGE_DIR);
  if (!dir) return;

  // Find and delete oldest file
  String oldestName = "";
  unsigned long oldestTime = ULONG_MAX;

  File entry = dir.openNextFile();
  while (entry) {
    if (!entry.isDirectory()) {
      unsigned long t = entry.getLastWrite();
      if (t < oldestTime) {
        oldestTime = t;
        oldestName = String(entry.name());
      }
    }
    entry = dir.openNextFile();
  }
  dir.close();

  if (oldestName.length() > 0) {
    char delPath[64];
    snprintf(delPath, sizeof(delPath), "%s/%s", SD_IMAGE_DIR, oldestName.c_str());
    SD_MMC.remove(delPath);
    sdImageCount--;
    debugPrintf("✔ Deleted oldest: %s", oldestName.c_str());
  }
}

// ===== STATUS AND LISTING =====

void printSDStatus() {
  #if ENABLE_SERIAL_OUTPUT
    Serial.println("\nSD Card Status:");
    Serial.println("----------------------------------------");
    if (!sdAvailable) {
      Serial.println("  x Not available");
    } else {
      uint64_t totalMB = SD_MMC.totalBytes() / (1024 * 1024);
      uint64_t usedMB  = SD_MMC.usedBytes()  / (1024 * 1024);
      uint64_t freeMB  = totalMB - usedMB;
      Serial.println("  ✔ Available");
      Serial.printf("  Total: %llu MB\n", totalMB);
      Serial.printf("  Used: %llu MB\n",  usedMB);
      Serial.printf("  Free: %llu MB\n",  freeMB);
      Serial.printf("  Images: %d\n",     sdImageCount);
    }
    Serial.println("----------------------------------------\n");
  #endif
}

void listSDFiles() {
  #if ENABLE_SERIAL_OUTPUT
    if (!sdAvailable) {
      Serial.println("x SD card not available");
      return;
    }

    Serial.println("\nSD Card Contents:");
    Serial.println("========================================");
    listDirectory(SD_MMC, SD_IMAGE_DIR, 1);
    listDirectory(SD_MMC, SD_LOG_DIR, 1);
    Serial.println("========================================\n");
  #endif
}

// ===== HELPER FUNCTIONS =====

bool sdIsAvailable() {
  return sdAvailable;
}

int sdGetImageCount() {
  return sdImageCount;
}

uint64_t sdGetFreeSpace() {
  if (!sdAvailable) return 0;
  return SD_MMC.totalBytes() - SD_MMC.usedBytes();
}

// ===== INTERNAL HELPERS =====

static int countSDImages() {
  if (!sdAvailable) return 0;
  int count = 0;
  File dir = SD_MMC.open(SD_IMAGE_DIR);
  if (!dir) return 0;
  File entry = dir.openNextFile();
  while (entry) {
    if (!entry.isDirectory()) count++;
    entry = dir.openNextFile();
  }
  dir.close();
  return count;
}

static void listDirectory(fs::FS &fs, const char* dirname, uint8_t levels) {
  File root = fs.open(dirname);
  if (!root || !root.isDirectory()) return;

  Serial.printf("📁 %s\n", dirname);
  File file = root.openNextFile();
  while (file) {
    if (file.isDirectory()) {
      if (levels > 0) listDirectory(fs, file.name(), levels - 1);
    } else {
      Serial.printf("  📄 %s (%u bytes)\n", file.name(), file.size());
    }
    file = root.openNextFile();
  }
}

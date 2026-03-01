/*
 * SD Card Module - PULL Mode Edition (V1.1)
 * 
 * Core SD operations for AI Thinker ESP32-CAM:
 *   - Initialization (1-bit SD_MMC)
 *   - Save images to offline queue (/offline/)
 *   - Storage cleanup (80% -> 50%)
 *   - List/read/delete operations for server endpoints
 * 
 * PULL Mode Architecture:
 *   - Images saved to SD when Python poller is unreachable
 *   - Python checks /queue endpoint periodically
 *   - Python fetches each queued image via /queue/<filename>
 *   - Python tells ESP32 to delete via /queue/delete/<filename>
 * 
 * SD Card Pins (1-bit SD_MMC):
 *   CLK  -> GPIO 14
 *   CMD  -> GPIO 15
 *   DAT0 -> GPIO 2  (boot-mode pin - remove card when flashing!)
 */

#include "globals.h"
#include "SD_MMC.h"
#include "FS.h"

// ===== PRIVATE HELPERS =====

// Collect all .jpg files in SD_QUEUE_DIR, sorted ascending (oldest first)
static void collectSortedFileList(std::vector<String>& files) {
  File root = SD_MMC.open(SD_QUEUE_DIR);
  if (!root || !root.isDirectory()) return;

  File entry = root.openNextFile();
  while (entry) {
    if (!entry.isDirectory()) {
      String name = entry.name();
      if (name.endsWith(".jpg")) {
        // Strip directory prefix, keep just filename
        int lastSlash = name.lastIndexOf('/');
        if (lastSlash >= 0) {
          name = name.substring(lastSlash + 1);
        }
        files.push_back(name);
      }
    }
    entry = root.openNextFile();
  }
  root.close();

  // Sort ascending by filename (timestamp format = lexicographic order)
  std::sort(files.begin(), files.end());
}

// ===== PUBLIC API =====

bool initSDCard() {
  /*
   * Mount SD card in 1-bit SD_MMC mode.
   * GPIO 2 (DAT0) is the boot-mode pin - remove SD card when flashing.
   */
  if (!SD_MMC.begin("/sdcard", true)) {   // true = 1-bit mode
    debugPrint("[SD] Mount failed - check card is inserted");
    sdCardAvailable = false;
    return false;
  }

  uint8_t cardType = SD_MMC.cardType();
  if (cardType == CARD_NONE) {
    debugPrint("[SD] No card detected");
    sdCardAvailable = false;
    return false;
  }

  // Create queue directory
  if (!SD_MMC.exists(SD_QUEUE_DIR)) {
    SD_MMC.mkdir(SD_QUEUE_DIR);
  }

  sdCardAvailable = true;

  uint64_t totalMB = SD_MMC.totalBytes() / (1024 * 1024);
  uint64_t usedMB  = SD_MMC.usedBytes()  / (1024 * 1024);
  debugPrintf("[SD] Ready  Total: %lluMB  Used: %lluMB", totalMB, usedMB);
  
  return true;
}

int getSDUsagePercent() {
  if (!sdCardAvailable) return 0;
  uint64_t total = SD_MMC.totalBytes();
  if (total == 0) return 0;
  return (int)((SD_MMC.usedBytes() * 100) / total);
}

void checkAndCleanStorage() {
  /*
   * If usage >= 80%, delete every other file (oldest first)
   * until usage drops below 50%.
   */
  if (!sdCardAvailable) return;

  int usagePct = getSDUsagePercent();
  if (usagePct < SD_WARN_PERCENT) return;

  debugPrintf("[SD] Storage at %d%% - cleaning (target: %d%%)",
              usagePct, SD_TARGET_PERCENT);

  std::vector<String> files;
  collectSortedFileList(files);

  if (files.empty()) {
    debugPrint("[SD] No queued images to delete");
    return;
  }

  int deleted = 0;
  for (size_t i = 1; i < files.size(); i += 2) {
    String fullPath = String(SD_QUEUE_DIR) + "/" + files[i];
    if (SD_MMC.remove(fullPath.c_str())) {
      deleted++;
      debugPrintf("[SD] Deleted: %s", files[i].c_str());
    }
    if (getSDUsagePercent() < SD_TARGET_PERCENT) break;
  }

  debugPrintf("[SD] Cleanup complete - deleted %d files, usage now %d%%",
              deleted, getSDUsagePercent());
}

String saveImageToSD(camera_fb_t* fb, const String& timestamp) {
  /*
   * Save a captured image to the offline queue.
   * Filename: YYYYMMDD_HHMMSS.jpg
   * Returns full path on success, empty string on failure.
   */
  if (!sdCardAvailable) {
    debugPrint("[SD] Card not available");
    return "";
  }

  checkAndCleanStorage();

  String path = String(SD_QUEUE_DIR) + "/" + timestamp + ".jpg";

  File file = SD_MMC.open(path.c_str(), FILE_WRITE);
  if (!file) {
    debugPrintf("[SD] Failed to open: %s", path.c_str());
    return "";
  }

  size_t written = file.write(fb->buf, fb->len);
  file.close();

  if (written != fb->len) {
    debugPrintf("[SD] Write incomplete (%u/%u bytes)", written, fb->len);
    SD_MMC.remove(path.c_str());
    return "";
  }

  sdQueueCount++;
  debugPrintf("[SD] Saved offline: %s  (%u bytes)", timestamp.c_str(), written);
  return path;
}

uint8_t* readImageFromSD(const String& filename, size_t& outSize) {
  /*
   * Read a queued image into a heap-allocated buffer.
   * Caller MUST free() the returned pointer.
   * Returns nullptr on failure.
   */
  outSize = 0;
  if (!sdCardAvailable) return nullptr;

  String path = String(SD_QUEUE_DIR) + "/" + filename;

  File file = SD_MMC.open(path.c_str(), FILE_READ);
  if (!file) {
    debugPrintf("[SD] Cannot open: %s", filename.c_str());
    return nullptr;
  }

  outSize = file.size();
  if (outSize == 0) {
    file.close();
    return nullptr;
  }

  uint8_t* buf = (uint8_t*)malloc(outSize);
  if (!buf) {
    debugPrintf("[SD] malloc(%u) failed", outSize);
    file.close();
    outSize = 0;
    return nullptr;
  }

  size_t bytesRead = file.read(buf, outSize);
  file.close();

  if (bytesRead != outSize) {
    debugPrintf("[SD] Read mismatch (%u/%u)", bytesRead, outSize);
    free(buf);
    outSize = 0;
    return nullptr;
  }

  return buf;
}

bool deleteImageFromSD(const String& filename) {
  /*
   * Delete a single queued image.
   * Called by Python after successful fetch.
   */
  if (!sdCardAvailable) return false;

  String path = String(SD_QUEUE_DIR) + "/" + filename;
  bool ok = SD_MMC.remove(path.c_str());
  
  if (ok) {
    if (sdQueueCount > 0) sdQueueCount--;
    debugPrintf("[SD] Deleted: %s", filename.c_str());
  } else {
    debugPrintf("[SD] Failed to delete: %s", filename.c_str());
  }
  
  return ok;
}

int countQueuedImages() {
  if (!sdCardAvailable) return 0;
  std::vector<String> files;
  collectSortedFileList(files);
  sdQueueCount = files.size();
  return sdQueueCount;
}

void getQueuedImageList(std::vector<String>& files) {
  /*
   * Fill 'files' vector with sorted (oldest-first) filenames.
   * Used by /queue endpoint to return JSON list.
   */
  files.clear();
  if (!sdCardAvailable) return;
  collectSortedFileList(files);
}

void printSDStatus() {
  if (!sdCardAvailable) {
    debugPrint("[SD] Not available");
    return;
  }
  
  uint64_t totalMB = SD_MMC.totalBytes() / (1024 * 1024);
  uint64_t usedMB  = SD_MMC.usedBytes()  / (1024 * 1024);
  int pct = getSDUsagePercent();
  int queued = countQueuedImages();

  debugPrintf("[SD] Total: %lluMB  Used: %lluMB (%d%%)  Queued: %d images",
              totalMB, usedMB, pct, queued);
}

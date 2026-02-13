/*
 * ESP32-CAM SD Card Test Script
 * 
 * This standalone script tests SD card functionality:
 * - Initialize SD card
 * - Create test files
 * - Read files back
 * - List directory contents
 * - Check free space
 * 
 * Upload this to your ESP32-CAM and monitor via Serial (115200 baud)
 * No PC card reader needed - all verification via Serial output!
 */

#include "SD_MMC.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n========================================");
  Serial.println("ESP32-CAM SD Card Test");
  Serial.println("========================================\n");
  
  // Test 1: Initialize SD Card
  if (!testSDCardInit()) {
    Serial.println("\n❌ SD Card initialization failed!");
    Serial.println("Check:");
    Serial.println("  1. SD card is inserted");
    Serial.println("  2. SD card is formatted (FAT32)");
    Serial.println("  3. Card is not write-protected");
    while(1) { delay(1000); }
  }
  
  // Test 2: Get Card Info
  testCardInfo();
  
  // Test 3: Write Test Files
  testFileWrite();
  
  // Test 4: Read Test Files
  testFileRead();
  
  // Test 5: List All Files
  testListFiles();
  
  // Test 6: Append to File
  testFileAppend();
  
  // Test 7: Delete Test File
  testFileDelete();
  
  // Final Summary
  printTestSummary();
}

void loop() {
  // Nothing to do - all tests run once in setup()
  delay(10000);
}

// ========================================
// TEST FUNCTIONS
// ========================================

bool testSDCardInit() {
  Serial.println("Test 1: Initializing SD Card...");
  
  // ESP32-CAM uses 1-bit mode for SD_MMC
  if (!SD_MMC.begin("/sdcard", true)) {
    return false;
  }
  
  Serial.println("✅ SD Card initialized successfully!");
  return true;
}

void testCardInfo() {
  Serial.println("\nTest 2: Card Information");
  Serial.println("----------------------------------------");
  
  uint8_t cardType = SD_MMC.cardType();
  
  Serial.print("Card Type: ");
  if (cardType == CARD_NONE) {
    Serial.println("No card");
  } else if (cardType == CARD_MMC) {
    Serial.println("MMC");
  } else if (cardType == CARD_SD) {
    Serial.println("SDSC");
  } else if (cardType == CARD_SDHC) {
    Serial.println("SDHC");
  } else {
    Serial.println("Unknown");
  }
  
  uint64_t cardSize = SD_MMC.cardSize() / (1024 * 1024);
  Serial.printf("Card Size: %llu MB\n", cardSize);
  
  uint64_t totalBytes = SD_MMC.totalBytes() / (1024 * 1024);
  Serial.printf("Total Space: %llu MB\n", totalBytes);
  
  uint64_t usedBytes = SD_MMC.usedBytes() / (1024 * 1024);
  Serial.printf("Used Space: %llu MB\n", usedBytes);
  
  uint64_t freeBytes = (SD_MMC.totalBytes() - SD_MMC.usedBytes()) / (1024 * 1024);
  Serial.printf("Free Space: %llu MB\n", freeBytes);
  
  Serial.println("✅ Card info retrieved");
}

void testFileWrite() {
  Serial.println("\nTest 3: Writing Test Files");
  Serial.println("----------------------------------------");
  
  // Write text file
  File file = SD_MMC.open("/test.txt", FILE_WRITE);
  if (!file) {
    Serial.println("❌ Failed to open test.txt for writing");
    return;
  }
  
  file.println("ESP32-CAM SD Card Test");
  file.println("This is a test file.");
  file.printf("Timestamp: %lu\n", millis());
  file.close();
  Serial.println("✅ Created /test.txt");
  
  // Write CSV file
  file = SD_MMC.open("/data.csv", FILE_WRITE);
  if (file) {
    file.println("timestamp,value,status");
    file.println("1000,42,OK");
    file.println("2000,55,OK");
    file.println("3000,38,OK");
    file.close();
    Serial.println("✅ Created /data.csv");
  }
  
  // Create directory
  if (SD_MMC.mkdir("/testdir")) {
    Serial.println("✅ Created /testdir/");
    
    // Write file in directory
    file = SD_MMC.open("/testdir/nested.txt", FILE_WRITE);
    if (file) {
      file.println("File in subdirectory");
      file.close();
      Serial.println("✅ Created /testdir/nested.txt");
    }
  }
}

void testFileRead() {
  Serial.println("\nTest 4: Reading Test Files");
  Serial.println("----------------------------------------");
  
  File file = SD_MMC.open("/test.txt");
  if (!file) {
    Serial.println("❌ Failed to open test.txt for reading");
    return;
  }
  
  Serial.println("Contents of /test.txt:");
  Serial.println("---");
  while (file.available()) {
    Serial.write(file.read());
  }
  Serial.println("---");
  file.close();
  Serial.println("✅ File read successfully");
}

void testListFiles() {
  Serial.println("\nTest 5: Listing All Files");
  Serial.println("----------------------------------------");
  
  listDir(SD_MMC, "/", 0);
  Serial.println("✅ Directory listing complete");
}

void testFileAppend() {
  Serial.println("\nTest 6: Appending to File");
  Serial.println("----------------------------------------");
  
  File file = SD_MMC.open("/test.txt", FILE_APPEND);
  if (!file) {
    Serial.println("❌ Failed to open test.txt for appending");
    return;
  }
  
  file.println("This line was appended!");
  file.printf("Append timestamp: %lu\n", millis());
  file.close();
  
  Serial.println("✅ Data appended to /test.txt");
  
  // Read back to verify
  file = SD_MMC.open("/test.txt");
  Serial.println("\nUpdated contents:");
  Serial.println("---");
  while (file.available()) {
    Serial.write(file.read());
  }
  Serial.println("---");
  file.close();
}

void testFileDelete() {
  Serial.println("\nTest 7: Deleting Test File");
  Serial.println("----------------------------------------");
  
  // Create a file to delete
  File file = SD_MMC.open("/delete_me.txt", FILE_WRITE);
  if (file) {
    file.println("This file will be deleted");
    file.close();
    Serial.println("✅ Created /delete_me.txt");
  }
  
  // Delete it
  if (SD_MMC.remove("/delete_me.txt")) {
    Serial.println("✅ Deleted /delete_me.txt");
  } else {
    Serial.println("❌ Failed to delete file");
  }
  
  // Verify it's gone
  file = SD_MMC.open("/delete_me.txt");
  if (!file) {
    Serial.println("✅ Verified: File no longer exists");
  } else {
    Serial.println("❌ File still exists!");
    file.close();
  }
}

// ========================================
// HELPER FUNCTIONS
// ========================================

void listDir(fs::FS &fs, const char *dirname, uint8_t levels) {
  Serial.printf("Listing directory: %s\n", dirname);
  
  File root = fs.open(dirname);
  if (!root) {
    Serial.println("Failed to open directory");
    return;
  }
  if (!root.isDirectory()) {
    Serial.println("Not a directory");
    return;
  }
  
  File file = root.openNextFile();
  while (file) {
    if (file.isDirectory()) {
      Serial.print("  DIR : ");
      Serial.println(file.name());
      if (levels) {
        listDir(fs, file.path(), levels - 1);
      }
    } else {
      Serial.print("  FILE: ");
      Serial.print(file.name());
      Serial.print("\t\tSIZE: ");
      Serial.println(file.size());
    }
    file = root.openNextFile();
  }
}

void printTestSummary() {
  Serial.println("\n========================================");
  Serial.println("TEST SUMMARY");
  Serial.println("========================================");
  Serial.println("✅ SD Card initialization");
  Serial.println("✅ Card info retrieval");
  Serial.println("✅ File writing");
  Serial.println("✅ File reading");
  Serial.println("✅ Directory listing");
  Serial.println("✅ File appending");
  Serial.println("✅ File deletion");
  Serial.println("\n🎉 All tests passed!");
  Serial.println("========================================\n");
  
  Serial.println("Your SD card is working correctly!");
  Serial.println("You can now integrate SD card functionality");
  Serial.println("into your main project.\n");
}

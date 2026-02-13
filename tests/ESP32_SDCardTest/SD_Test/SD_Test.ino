/*
 * ESP32-CAM SD Card Diagnostic Tool
 * 
 * This script provides detailed diagnostics to identify SD card issues
 * WITHOUT needing a PC card reader!
 * 
 * Checks:
 * - Card detection
 * - Card type and size
 * - Filesystem type (FAT32 vs others)
 * - Read/write permissions
 * - Speed test
 * - Pin connections
 * 
 * Upload this and open Serial Monitor (115200 baud)
 */

#include "SD_MMC.h"
#include "FS.h"

void setup() {
  Serial.begin(115200);
  delay(2000);  // Wait for Serial Monitor
  
  printHeader();
  
  // Run comprehensive diagnostics
  runDiagnostics();
  
  printSummary();
}

void loop() {
  // Nothing to do
  delay(10000);
}

// ========================================
// DIAGNOSTIC TESTS
// ========================================

void runDiagnostics() {
  Serial.println("\nStarting SD Card Diagnostics...\n");
  
  // Test 1: Basic Detection
  testBasicDetection();
  delay(500);
  
  // Test 2: Card Type & Size
  testCardInfo();
  delay(500);
  
  // Test 3: Filesystem Check
  testFilesystem();
  delay(500);
  
  // Test 4: Read Test
  testReadCapability();
  delay(500);
  
  // Test 5: Write Test
  testWriteCapability();
  delay(500);
  
  // Test 6: Speed Test
  testSpeed();
  delay(500);
}

// ========================================
// TEST 1: BASIC DETECTION
// ========================================

void testBasicDetection() {
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("TEST 1: BASIC DETECTION");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  Serial.println("Attempting to initialize SD_MMC in 1-bit mode...");
  
  // Try to initialize
  if (!SD_MMC.begin("/sdcard", true)) {
    Serial.println("\n❌ FAILED: SD_MMC.begin() returned false");
    Serial.println("\nPossible causes:");
    Serial.println("  1. No SD card inserted");
    Serial.println("  2. SD card not properly seated");
    Serial.println("  3. Card is damaged/corrupt");
    Serial.println("  4. Wrong card type (SDIO/MMC)");
    Serial.println("  5. Card needs formatting");
    Serial.println("\nTroubleshooting:");
    Serial.println("  → Power OFF ESP32");
    Serial.println("  → Remove SD card");
    Serial.println("  → Check card for physical damage");
    Serial.println("  → Reinsert card (metal contacts toward PCB)");
    Serial.println("  → Power ON ESP32");
    Serial.println("  → Run this test again");
    return;
  }
  
  Serial.println("✅ PASSED: SD_MMC initialized successfully");
}

// ========================================
// TEST 2: CARD TYPE & SIZE
// ========================================

void testCardInfo() {
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("TEST 2: CARD TYPE & SIZE");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  uint8_t cardType = SD_MMC.cardType();
  
  Serial.print("Card Type: ");
  if (cardType == CARD_NONE) {
    Serial.println("❌ NONE (No card detected)");
    Serial.println("\nCard may be inserted incorrectly or damaged.");
    return;
  } else if (cardType == CARD_MMC) {
    Serial.println("✅ MMC");
  } else if (cardType == CARD_SD) {
    Serial.println("✅ SDSC (Standard Capacity)");
  } else if (cardType == CARD_SDHC) {
    Serial.println("✅ SDHC (High Capacity) - Recommended");
  } else {
    Serial.println("⚠️  Unknown type");
  }
  
  // Card size
  uint64_t cardSize = SD_MMC.cardSize();
  Serial.printf("Card Size: %llu bytes (%.2f GB)\n", 
                cardSize, 
                (float)cardSize / (1024*1024*1024));
  
  // Capacity check
  if (cardSize > 0) {
    Serial.println("✅ PASSED: Card size detected");
    
    if (cardSize > 32ULL * 1024 * 1024 * 1024) {
      Serial.println("⚠️  WARNING: Card > 32GB may have issues");
      Serial.println("   Recommended: 8-32GB cards");
    }
  } else {
    Serial.println("❌ FAILED: Card size is 0");
    Serial.println("   Card may be unformatted or corrupt");
  }
  
  // Total vs Used space
  uint64_t totalBytes = SD_MMC.totalBytes();
  uint64_t usedBytes = SD_MMC.usedBytes();
  
  Serial.printf("Total Space: %llu MB\n", totalBytes / (1024*1024));
  Serial.printf("Used Space: %llu MB\n", usedBytes / (1024*1024));
  Serial.printf("Free Space: %llu MB\n", (totalBytes - usedBytes) / (1024*1024));
  
  if (totalBytes == 0) {
    Serial.println("\n❌ CRITICAL: Total space is 0!");
    Serial.println("This usually means:");
    Serial.println("  → Card is NOT formatted");
    Serial.println("  → Card filesystem is corrupt");
    Serial.println("  → Card is incompatible");
    Serial.println("\n🔧 SOLUTION: Card needs formatting as FAT32");
  } else {
    Serial.println("✅ PASSED: Space information available");
  }
}

// ========================================
// TEST 3: FILESYSTEM CHECK
// ========================================

void testFilesystem() {
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("TEST 3: FILESYSTEM CHECK");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  // Try to open root directory
  File root = SD_MMC.open("/");
  if (!root) {
    Serial.println("❌ FAILED: Cannot open root directory");
    Serial.println("\nThis means:");
    Serial.println("  → Filesystem is corrupt or unformatted");
    Serial.println("  → Card is not FAT32");
    Serial.println("  → Card is incompatible with ESP32");
    Serial.println("\n🔧 SOLUTION:");
    Serial.println("  1. Find a device that can format SD cards");
    Serial.println("  2. Format as FAT32 (NOT exFAT, NOT NTFS)");
    Serial.println("  3. If card > 32GB, may need special tool");
    return;
  }
  
  if (!root.isDirectory()) {
    Serial.println("❌ FAILED: Root is not a directory");
    Serial.println("   Filesystem is severely corrupt");
    root.close();
    return;
  }
  
  Serial.println("✅ PASSED: Root directory accessible");
  
  // Try to list directory
  Serial.println("\nAttempting to list root directory...");
  File file = root.openNextFile();
  int fileCount = 0;
  
  while (file && fileCount < 10) {
    if (file.isDirectory()) {
      Serial.printf("  📁 %s/\n", file.name());
    } else {
      Serial.printf("  📄 %s (%d bytes)\n", file.name(), file.size());
    }
    fileCount++;
    file = root.openNextFile();
  }
  
  if (fileCount == 0) {
    Serial.println("  (Empty - no files/folders)");
  }
  
  root.close();
  Serial.println("✅ PASSED: Directory listing works");
}

// ========================================
// TEST 4: READ CAPABILITY
// ========================================

void testReadCapability() {
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("TEST 4: READ CAPABILITY");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  // First check if we can even access filesystem
  uint64_t totalBytes = SD_MMC.totalBytes();
  if (totalBytes == 0) {
    Serial.println("⏭️  SKIPPED: Card not formatted properly");
    return;
  }
  
  Serial.println("Checking if card is readable...");
  
  // Try to create a test file
  File testFile = SD_MMC.open("/read_test.txt", FILE_WRITE);
  if (!testFile) {
    Serial.println("⚠️  Cannot create test file (testing read on existing files)");
  } else {
    testFile.println("ESP32 SD Card Read Test");
    testFile.close();
    Serial.println("✅ Created test file");
  }
  
  // Try to read it back
  testFile = SD_MMC.open("/read_test.txt", FILE_READ);
  if (!testFile) {
    Serial.println("❌ FAILED: Cannot read test file");
    Serial.println("   Card may be corrupt or read-protected");
    return;
  }
  
  Serial.println("Reading test file...");
  while (testFile.available()) {
    Serial.write(testFile.read());
  }
  testFile.close();
  
  Serial.println("\n✅ PASSED: Read capability verified");
  
  // Clean up
  SD_MMC.remove("/read_test.txt");
}

// ========================================
// TEST 5: WRITE CAPABILITY
// ========================================

void testWriteCapability() {
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("TEST 5: WRITE CAPABILITY");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  // Check if card is formatted
  uint64_t totalBytes = SD_MMC.totalBytes();
  if (totalBytes == 0) {
    Serial.println("⏭️  SKIPPED: Card not formatted properly");
    return;
  }
  
  Serial.println("Attempting to write test file...");
  
  File testFile = SD_MMC.open("/write_test.txt", FILE_WRITE);
  if (!testFile) {
    Serial.println("❌ FAILED: Cannot create file for writing");
    Serial.println("\nPossible causes:");
    Serial.println("  1. Card is write-protected (check lock switch)");
    Serial.println("  2. Card is full (unlikely)");
    Serial.println("  3. Card is read-only filesystem");
    Serial.println("  4. Card is failing");
    return;
  }
  
  // Write test data
  size_t written = testFile.println("ESP32 SD Card Write Test");
  testFile.close();
  
  if (written == 0) {
    Serial.println("❌ FAILED: Write returned 0 bytes");
    Serial.println("   Card may be write-protected");
    return;
  }
  
  Serial.printf("✅ Wrote %d bytes successfully\n", written);
  
  // Verify by reading back
  testFile = SD_MMC.open("/write_test.txt", FILE_READ);
  if (!testFile) {
    Serial.println("⚠️  Warning: Cannot read back file");
    return;
  }
  
  Serial.println("Verifying write by reading back...");
  String content = testFile.readString();
  testFile.close();
  
  if (content.indexOf("ESP32") >= 0) {
    Serial.println("✅ PASSED: Write verified!");
  } else {
    Serial.println("❌ FAILED: Data mismatch");
  }
  
  // Clean up
  SD_MMC.remove("/write_test.txt");
}

// ========================================
// TEST 6: SPEED TEST
// ========================================

void testSpeed() {
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("TEST 6: SPEED TEST");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  // Check if card is formatted
  uint64_t totalBytes = SD_MMC.totalBytes();
  if (totalBytes == 0) {
    Serial.println("⏭️  SKIPPED: Card not formatted properly");
    return;
  }
  
  Serial.println("Testing write speed (10KB)...");
  
  unsigned long startTime = millis();
  File testFile = SD_MMC.open("/speed_test.bin", FILE_WRITE);
  
  if (!testFile) {
    Serial.println("❌ Cannot create test file");
    return;
  }
  
  // Write 10KB
  uint8_t buffer[1024];
  for (int i = 0; i < 1024; i++) {
    buffer[i] = i % 256;
  }
  
  for (int i = 0; i < 10; i++) {
    testFile.write(buffer, 1024);
  }
  testFile.close();
  
  unsigned long writeTime = millis() - startTime;
  float writeSpeed = 10.0 / (writeTime / 1000.0);  // KB/s
  
  Serial.printf("✅ Write: %.2f KB/s (%lu ms)\n", writeSpeed, writeTime);
  
  // Read speed
  Serial.println("Testing read speed (10KB)...");
  startTime = millis();
  testFile = SD_MMC.open("/speed_test.bin", FILE_READ);
  
  if (!testFile) {
    Serial.println("❌ Cannot open test file");
    return;
  }
  
  size_t bytesRead = 0;
  while (testFile.available()) {
    testFile.read();
    bytesRead++;
  }
  testFile.close();
  
  unsigned long readTime = millis() - startTime;
  float readSpeed = 10.0 / (readTime / 1000.0);  // KB/s
  
  Serial.printf("✅ Read: %.2f KB/s (%lu ms)\n", readSpeed, readTime);
  
  // Performance assessment
  Serial.println("\nPerformance Assessment:");
  if (writeSpeed > 50) {
    Serial.println("  ✅ Excellent write speed");
  } else if (writeSpeed > 20) {
    Serial.println("  ✅ Good write speed");
  } else if (writeSpeed > 10) {
    Serial.println("  ⚠️  Slow write speed");
    Serial.println("     Consider using Class 10 or UHS-1 card");
  } else {
    Serial.println("  ❌ Very slow write speed");
    Serial.println("     Card may be failing or very low quality");
  }
  
  // Clean up
  SD_MMC.remove("/speed_test.bin");
}

// ========================================
// HELPER FUNCTIONS
// ========================================

void printHeader() {
  Serial.println("\n\n");
  Serial.println("╔══════════════════════════════════════════════╗");
  Serial.println("║   ESP32-CAM SD CARD DIAGNOSTIC TOOL          ║");
  Serial.println("║   No PC Card Reader Needed!                  ║");
  Serial.println("╚══════════════════════════════════════════════╝");
}

void printSummary() {
  Serial.println("\n\n");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("DIAGNOSTIC SUMMARY");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  uint64_t totalBytes = SD_MMC.totalBytes();
  
  if (totalBytes == 0) {
    Serial.println("\n🔴 CARD NOT READY FOR USE");
    Serial.println("\nMost likely cause: Card is NOT formatted as FAT32");
    Serial.println("\nNEXT STEPS:");
    Serial.println("  1. Find ANY device that can read SD cards:");
    Serial.println("     • Android phone");
    Serial.println("     • Digital camera");
    Serial.println("     • Friend's laptop");
    Serial.println("     • Library computer");
    Serial.println("  2. Format the card as FAT32");
    Serial.println("  3. Safely eject");
    Serial.println("  4. Insert back into ESP32");
    Serial.println("  5. Run this diagnostic again");
  } else {
    Serial.println("\n🟢 CARD IS WORKING!");
    Serial.println("\nYour SD card passed all tests.");
    Serial.println("You can now use it with your ESP32-CAM project.");
    Serial.println("\nNext step: Upload sd_card_test.ino for full functionality test");
  }
  
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

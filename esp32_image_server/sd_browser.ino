/*
 * SD Browser Module (V1.1)
 * 
 * Web-based SD card file browser endpoints
 * 
 * New endpoints:
 *   /sd/list           - List all files on SD card (JSON)
 *   /sd/browse         - HTML browser interface
 *   /sd/file/<path>    - Download/view a specific file
 *   /sd/delete/<path>  - Delete a file
 *   /sd/stats          - SD card statistics (JSON)
 */

#include "globals.h"

// ===== SD CARD LIST ENDPOINT =====

void handleSDList() {
  /*
   * GET /sd/list
   * Returns JSON array of all files on SD card
   */
  #if !ENABLE_SD_CARD
    server.send(503, "application/json", "{\"error\":\"SD card disabled\"}");
    return;
  #endif
  
  if (!sdCardAvailable) {
    server.send(503, "application/json", "{\"error\":\"SD card not available\"}");
    return;
  }
  
  std::vector<SDFileInfo> files;
  
  File root = SD_MMC.open("/");
  if (root && root.isDirectory()) {
    File entry = root.openNextFile();
    
    while (entry) {
      SDFileInfo info;
      info.name = String(entry.name());
      info.path = String(entry.name());
      info.size = entry.size();
      info.is_directory = entry.isDirectory();
      
      files.push_back(info);
      entry = root.openNextFile();
    }
    root.close();
  }
  
  // Build JSON response
  String json = "{\"files\":[";
  for (size_t i = 0; i < files.size(); i++) {
    if (i > 0) json += ",";
    json += "{";
    json += "\"name\":\"" + files[i].name + "\",";
    json += "\"path\":\"" + files[i].path + "\",";
    json += "\"size\":" + String(files[i].size) + ",";
    json += "\"is_directory\":" + String(files[i].is_directory ? "true" : "false");
    json += "}";
  }
  json += "],";
  json += "\"total\":" + String(files.size());
  json += "}";
  
  server.send(200, "application/json", json);
}

// ===== SD CARD BROWSER HTML =====

void handleSDBrowse() {
  /*
   * GET /sd/browse
   * HTML interface for browsing SD card
   */
  #if !ENABLE_SD_CARD
    server.send(503, "text/html", "<html><body><h1>SD Card Disabled</h1></body></html>");
    return;
  #endif
  
  if (!sdCardAvailable) {
    server.send(503, "text/html", "<html><body><h1>SD Card Not Available</h1></body></html>");
    return;
  }
  
  String html = "<!DOCTYPE html><html><head>";
  html += "<title>SD Card Browser</title>";
  html += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
  html += "<style>";
  html += "body{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}";
  html += ".card{background:white;border-radius:8px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}";
  html += "h1{color:#333;margin-bottom:20px}";
  html += ".stats{display:flex;gap:20px;margin-bottom:20px;padding:15px;background:#f0f0f0;border-radius:5px}";
  html += ".stat{flex:1;text-align:center}";
  html += ".stat-value{font-size:1.5em;font-weight:bold;color:#667eea}";
  html += ".stat-label{font-size:0.8em;color:#666;margin-top:5px}";
  html += "table{width:100%;border-collapse:collapse}";
  html += "th{background:#667eea;color:white;padding:12px;text-align:left}";
  html += "td{padding:10px;border-bottom:1px solid #ddd}";
  html += "tr:hover{background:#f9f9f9}";
  html += ".btn{padding:5px 10px;border:1px solid #ddd;background:white;border-radius:4px;cursor:pointer}";
  html += ".btn:hover{background:#f0f0f0}";
  html += ".btn-danger{color:#e74c3c;border-color:#e74c3c}";
  html += ".btn-danger:hover{background:#ffebee}";
  html += "</style></head><body>";
  
  html += "<div class=\"card\">";
  html += "<h1>SD Card Browser</h1>";
  
  // Stats
  uint64_t totalBytes = SD_MMC.totalBytes();
  uint64_t usedBytes = SD_MMC.usedBytes();
  uint64_t totalMB = totalBytes / (1024 * 1024);
  uint64_t usedMB = usedBytes / (1024 * 1024);
  int usagePct = getSDUsagePercent();
  
  html += "<div class=\"stats\">";
  html += "<div class=\"stat\"><div class=\"stat-value\">" + String(totalMB) + " MB</div><div class=\"stat-label\">Total</div></div>";
  html += "<div class=\"stat\"><div class=\"stat-value\">" + String(usedMB) + " MB</div><div class=\"stat-label\">Used</div></div>";
  html += "<div class=\"stat\"><div class=\"stat-value\">" + String(usagePct) + "%</div><div class=\"stat-label\">Usage</div></div>";
  html += "<div class=\"stat\"><div class=\"stat-value\">" + String(sdQueueCount) + "</div><div class=\"stat-label\">Queued</div></div>";
  html += "</div>";
  
  // File list
  html += "<table><thead><tr><th>Name</th><th>Size</th><th>Type</th><th>Actions</th></tr></thead><tbody>";
  
  File root = SD_MMC.open("/");
  if (root && root.isDirectory()) {
    File entry = root.openNextFile();
    
    while (entry) {
      String name = entry.name();
      size_t size = entry.size();
      bool isDir = entry.isDirectory();
      
      html += "<tr>";
      html += "<td>" + name + "</td>";
      html += "<td>" + String(size) + " bytes</td>";
      html += "<td>" + String(isDir ? "Directory" : "File") + "</td>";
      html += "<td>";
      if (!isDir) {
        html += "<button class=\"btn\" onclick=\"window.open('/sd/file" + name + "')\">View</button> ";
        html += "<button class=\"btn btn-danger\" onclick=\"if(confirm('Delete " + name + "?'))window.location='/sd/delete" + name + "'\">Delete</button>";
      }
      html += "</td>";
      html += "</tr>";
      
      entry = root.openNextFile();
    }
    root.close();
  }
  
  html += "</tbody></table>";
  html += "<br><button class=\"btn\" onclick=\"location.reload()\">Refresh</button>";
  html += " <button class=\"btn\" onclick=\"window.location='/'\">Home</button>";
  html += "</div>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

// ===== SD FILE SERVE =====

void handleSDFile() {
  /*
   * GET /sd/file/<path>
   * Serve a file from SD card
   */
  #if !ENABLE_SD_CARD
    server.send(503, "text/plain", "SD card disabled");
    return;
  #endif
  
  if (!sdCardAvailable) {
    server.send(503, "text/plain", "SD card not available");
    return;
  }
  
  String uri = server.uri();
  String path = uri.substring(8);  // Remove "/sd/file"
  
  // Security check
  if (path.indexOf("..") >= 0) {
    server.send(400, "text/plain", "Invalid path");
    return;
  }
  
  File file = SD_MMC.open(path.c_str(), FILE_READ);
  if (!file || file.isDirectory()) {
    server.send(404, "text/plain", "File not found");
    return;
  }
  
  size_t fileSize = file.size();
  
  // Determine MIME type
  String contentType = "application/octet-stream";
  if (path.endsWith(".jpg") || path.endsWith(".jpeg")) {
    contentType = "image/jpeg";
  } else if (path.endsWith(".txt")) {
    contentType = "text/plain";
  } else if (path.endsWith(".json")) {
    contentType = "application/json";
  }
  
  // Stream file to client
  server.setContentLength(fileSize);
  server.send(200, contentType, "");
  
  WiFiClient client = server.client();
  uint8_t buf[512];
  size_t remaining = fileSize;
  
  while (remaining > 0) {
    size_t toRead = min(remaining, sizeof(buf));
    size_t bytesRead = file.read(buf, toRead);
    
    if (bytesRead > 0) {
      client.write(buf, bytesRead);
      remaining -= bytesRead;
    } else {
      break;
    }
  }
  
  file.close();
}

// ===== SD FILE DELETE =====

void handleSDDelete() {
  /*
   * GET /sd/delete/<path>
   * Delete a file from SD card
   */
  #if !ENABLE_SD_CARD
    server.send(503, "text/plain", "SD card disabled");
    return;
  #endif
  
  if (!sdCardAvailable) {
    server.send(503, "text/plain", "SD card not available");
    return;
  }
  
  String uri = server.uri();
  String path = uri.substring(10);  // Remove "/sd/delete"
  
  // Security check
  if (path.indexOf("..") >= 0) {
    server.send(400, "text/plain", "Invalid path");
    return;
  }
  
  if (SD_MMC.remove(path.c_str())) {
    // Redirect back to browser
    server.sendHeader("Location", "/sd/browse");
    server.send(303, "text/plain", "File deleted");
  } else {
    server.send(500, "text/plain", "Delete failed");
  }
}

// ===== SD STATS =====

void handleSDStats() {
  /*
   * GET /sd/stats
   * SD card statistics (JSON)
   */
  #if !ENABLE_SD_CARD
    server.send(503, "application/json", "{\"error\":\"SD card disabled\"}");
    return;
  #endif
  
  if (!sdCardAvailable) {
    server.send(503, "application/json", "{\"error\":\"SD card not available\"}");
    return;
  }
  
  uint64_t totalBytes = SD_MMC.totalBytes();
  uint64_t usedBytes = SD_MMC.usedBytes();
  
  String json = "{";
  json += "\"available\":true,";
  json += "\"total_bytes\":" + String((uint32_t)(totalBytes / 1024)) + ",";
  json += "\"used_bytes\":" + String((uint32_t)(usedBytes / 1024)) + ",";
  json += "\"total_mb\":" + String(totalBytes / (1024 * 1024)) + ",";
  json += "\"used_mb\":" + String(usedBytes / (1024 * 1024)) + ",";
  json += "\"usage_percent\":" + String(getSDUsagePercent()) + ",";
  json += "\"queue_count\":" + String(sdQueueCount);
  json += "}";
  
  server.send(200, "application/json", json);
}

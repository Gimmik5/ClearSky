"""
ESP32 Poller Module - V1.1 with SD Queue Support

Changes from V1.0:
  - Before each live poll, checks /queue endpoint for queued images
  - Fetches all queued images in chronological order (oldest first)
  - Processes each with its original capture timestamp from filename
  - Tells ESP32 to delete each file after successful fetch
  - Resumes normal live polling after queue is empty
"""

import time
import requests
import numpy as np
import cv2
from datetime import datetime
from analysis_core import analyze_image, get_analysis_summary
from data_manager_sqlite import data_manager
from image_storage import save_image


class ESP32Poller:
    """Manages ESP32 communication and polling with SD queue support"""
    
    def __init__(self, esp32_ip, esp32_port, poll_interval, request_timeout):
        self.esp32_ip = esp32_ip
        self.esp32_port = esp32_port
        self.poll_interval = poll_interval
        self.request_timeout = request_timeout
        
        # Endpoints
        self.capture_url = f"http://{esp32_ip}:{esp32_port}/capture"
        self.status_url = f"http://{esp32_ip}:{esp32_port}/status"
        self.queue_url = f"http://{esp32_ip}:{esp32_port}/queue"
        
        self.total_count = 0
        self.fail_count = 0
        self.queue_synced_count = 0
    
    def check_esp32_reachable(self):
        """Check if ESP32 is responding to status requests"""
        print(f"[Poller] Checking ESP32 at {self.esp32_ip}...")
        
        while True:
            try:
                resp = requests.get(self.status_url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"[Poller] ✓ ESP32 reachable")
                    print(f"[Poller]   RSSI: {data.get('wifi_rssi')} dBm  |  Heap: {data.get('freeHeap')} bytes")
                    
                    # Check if SD queue has waiting images
                    if data.get('sd_available'):
                        queue_count = data.get('sd_queue_count', 0)
                        if queue_count > 0:
                            print(f"[Poller]   📁 {queue_count} image(s) in offline queue")
                    
                    break
            except Exception:
                print(f"[Poller] ✗ ESP32 not reachable yet, retrying in 10s...")
                time.sleep(10)
    
    def fetch_queue_list(self):
        """
        Fetch list of queued images from ESP32.
        Returns list of filenames (oldest first), or empty list on error.
        """
        try:
            resp = requests.get(self.queue_url, timeout=5)
            if resp.status_code == 200:
                files = resp.json()
                if isinstance(files, list):
                    return files
        except Exception as e:
            print(f"[Poller] Could not fetch queue list: {e}")
        
        return []
    
    def fetch_queued_image(self, filename):
        """
        Fetch a specific queued image from ESP32.
        Returns (image_data, timestamp) on success, or (None, None) on failure.
        """
        url = f"http://{self.esp32_ip}:{self.esp32_port}/queue/{filename}"
        
        try:
            resp = requests.get(url, timeout=self.request_timeout, stream=True)
            if resp.status_code == 200:
                image_data = resp.content
                
                # Extract timestamp from filename (YYYYMMDD_HHMMSS.jpg)
                timestamp = filename.replace('.jpg', '').replace('.JPG', '')
                
                return image_data, timestamp
        except Exception as e:
            print(f"[Poller] Failed to fetch {filename}: {e}")
        
        return None, None
    
    def delete_queued_image(self, filename):
        """Tell ESP32 to delete a queued image after successful processing"""
        url = f"http://{self.esp32_ip}:{self.esp32_port}/queue/delete/{filename}"
        
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                result = resp.json()
                return result.get('deleted', False)
        except Exception:
            pass
        
        return False
    
    def process_queued_images(self):
        """
        Fetch and process all queued images from ESP32.
        Returns number of images successfully synced.
        """
        files = self.fetch_queue_list()
        
        if not files:
            return 0
        
        print(f"\n[Poller] ═══ Queue Sync: {len(files)} image(s) pending ═══")
        
        synced = 0
        
        for filename in files:
            print(f"[Poller] Fetching queued: {filename}")
            
            image_data, timestamp = self.fetch_queued_image(filename)
            
            if not image_data or not timestamp:
                print(f"[Poller] ✗ Failed to fetch {filename}")
                continue
            
            # Decode JPEG
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                print(f"[Poller] ✗ Failed to decode {filename}")
                continue
            
            # Save and analyze with original timestamp
            image_path = save_image(image, timestamp)
            analysis_results = analyze_image(image)
            
            # Mark as from SD in analysis results
            analysis_results['from_sd'] = True
            
            data_manager.update_latest(timestamp, image_path, analysis_results)
            data_manager.save_data()
            
            print(f"[Poller] ✓ Processed {filename}")
            print(f"[Poller]   {get_analysis_summary(analysis_results)}")
            
            # Tell ESP32 to delete this file
            if self.delete_queued_image(filename):
                print(f"[Poller] ✓ Deleted from ESP32 SD card")
            else:
                print(f"[Poller] ⚠ Delete request failed (file may remain on SD)")
            
            synced += 1
            
            # Brief delay between fetches
            time.sleep(0.5)
        
        print(f"[Poller] ═══ Queue Sync Complete: {synced}/{len(files)} synced ═══\n")
        
        self.queue_synced_count += synced
        return synced
    
    def fetch_and_process_live_image(self):
        """
        Fetch live image from ESP32 /capture endpoint.
        Returns True if successful, False otherwise.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n[Poller] Fetching live image...")
        
        try:
            resp = requests.get(self.capture_url, timeout=self.request_timeout, stream=True)
            
            if resp.status_code == 200:
                image_data = resp.content
                print(f"[Poller] ✓ Received {len(image_data)} bytes")
                
                # Decode JPEG
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is not None:
                    image_path = save_image(image, timestamp)
                    analysis_results = analyze_image(image)
                    
                    # Mark as live capture
                    analysis_results['from_sd'] = False
                    
                    data_manager.update_latest(timestamp, image_path, analysis_results)
                    data_manager.save_data()
                    print(f"[Poller] {get_analysis_summary(analysis_results)}")
                    return True
                else:
                    print(f"[Poller] ✗ Failed to decode JPEG")
                    return False
            else:
                print(f"[Poller] ✗ ESP32 returned HTTP {resp.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"[Poller] ✗ Connection refused - ESP32 unreachable")
            return False
        except requests.exceptions.Timeout:
            print(f"[Poller] ✗ Request timed out after {self.request_timeout}s")
            return False
        except Exception as e:
            print(f"[Poller] ✗ Unexpected error: {e}")
            return False
    
    def print_stats(self):
        """Print current polling statistics"""
        success_count = self.total_count - self.fail_count
        success_rate = (success_count / self.total_count * 100) if self.total_count > 0 else 0
        print(f"[Poller] Stats: {success_count}/{self.total_count} successful ({success_rate:.0f}%)")
        if self.queue_synced_count > 0:
            print(f"[Poller]        {self.queue_synced_count} synced from SD queue")
    
    def run(self):
        """Main polling loop - run in background thread"""
        print("\n[Poller] Starting - waiting 5 seconds for server to initialize...")
        time.sleep(5)
        
        self.check_esp32_reachable()
        
        print(f"[Poller] Running every {self.poll_interval}s - Ctrl+C to stop\n")
        
        while True:
            t_start = time.time()
            
            # ── V1.1: Check queue before live polling ──
            try:
                queued_count = self.process_queued_images()
                if queued_count > 0:
                    # Don't count queue syncs in total_count
                    pass
            except Exception as e:
                print(f"[Poller] Queue sync error: {e}")
            
            # ── Live capture ──
            success = self.fetch_and_process_live_image()
            
            if success:
                self.total_count += 1
            else:
                self.fail_count += 1
                self.total_count += 1
            
            # Print stats
            self.print_stats()
            
            # Wait for next poll
            elapsed = time.time() - t_start
            wait = max(0, self.poll_interval - elapsed)
            print(f"[Poller] Next capture in {wait:.0f}s")
            time.sleep(wait)

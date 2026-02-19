"""
ESP32 Poller Module
Handles periodic image capture from ESP32 and analysis
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
    """Manages ESP32 communication and polling"""
    
    def __init__(self, esp32_ip, esp32_port, poll_interval, request_timeout):
        self.esp32_ip = esp32_ip
        self.esp32_port = esp32_port
        self.poll_interval = poll_interval
        self.request_timeout = request_timeout
        self.capture_url = f"http://{esp32_ip}:{esp32_port}/capture"
        self.status_url = f"http://{esp32_ip}:{esp32_port}/status"
        
        self.total_count = 0
        self.fail_count = 0
    
    def check_esp32_reachable(self):
        """Check if ESP32 is responding to status requests"""
        print(f"[Poller] Checking ESP32 at {self.esp32_ip}...")
        
        while True:
            try:
                resp = requests.get(self.status_url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"[Poller] ✓ ESP32 reachable")
                    print(f"[Poller]   RSSI: {data.get('wifi_rssi')} dBm  |  Heap: {data.get('free_heap')} bytes")
                    break
            except Exception:
                print(f"[Poller] ✗ ESP32 not reachable yet, retrying in 10s...")
                time.sleep(10)
    
    def fetch_and_process_image(self):
        """
        Fetch image from ESP32, decode it, and run analysis
        Returns True if successful, False otherwise
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n[Poller] Fetching image from ESP32...")
        
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
    
    def run(self):
        """Main polling loop - run in background thread"""
        print("\n[Poller] Starting - waiting 5 seconds for server to initialise...")
        time.sleep(5)
        
        self.check_esp32_reachable()
        
        print(f"[Poller] Running every {self.poll_interval}s - Ctrl+C to stop\n")
        
        while True:
            t_start = time.time()
            
            # Fetch and process image
            success = self.fetch_and_process_image()
            
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

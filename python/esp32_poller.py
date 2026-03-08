"""
ESP32 Poller Module - V1.2 Robust Edition

NEW IN V1.2:
- Retry logic with exponential backoff
- Longer timeouts for SD card operations
- Graceful handling of ESP32 crashes/resets
- Better error recovery
- Health monitoring
- Automatic pause when ESP32 is struggling

ENHANCED FEATURES:
- Syncs queue in batches of 200 images (ESP32 limit)
- Automatically checks for more images after each batch
- Continues syncing until queue is completely empty
- Periodic queue rechecks (every 60s) instead of every poll
- Progress tracking for large queue syncs
- Prevents memory exhaustion on both ESP32 and Python
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
    """Manages ESP32 communication and polling with batched SD queue support"""
    
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
        
        # Queue sync management
        self.last_queue_check = 0
        self.queue_check_interval = 60  # Check for more images every 60 seconds
        self.polls_since_queue_check = 0
        
        # Health monitoring - NEW
        self.consecutive_failures = 0
        self.esp32_healthy = True
        self.last_successful_contact = time.time()
    
    def check_esp32_reachable(self):
        """Check if ESP32 is responding to status requests"""
        print(f"[Poller] Checking ESP32 at {self.esp32_ip}...")
        
        while True:
            try:
                resp = requests.get(self.status_url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"[Poller] ✓ ESP32 reachable")
                    print(f"[Poller]   RSSI: {data.get('wifi_rssi')} dBm  |  Heap: {data.get('freeHeap')} bytes")
                    
                    # Check if SD queue has waiting images
                    if data.get('sd_available'):
                        queue_count = data.get('sd_queue_count', 0)
                        if queue_count > 0:
                            print(f"[Poller]   📁 {queue_count} image(s) in offline queue")
                    
                    self.esp32_healthy = True
                    self.last_successful_contact = time.time()
                    break
            except Exception as e:
                print(f"[Poller] ✗ ESP32 not reachable yet: {e}")
                print(f"[Poller]   Retrying in 10s...")
                time.sleep(10)
    
    def wait_for_esp32_recovery(self, wait_time=30):
        """
        Wait for ESP32 to recover from crash/reset.
        Used when we detect ESP32 is down.
        """
        print(f"\n[Poller] ⚠️  ESP32 appears down - waiting {wait_time}s for recovery...")
        time.sleep(wait_time)
        
        # Try to re-establish contact
        try:
            resp = requests.get(self.status_url, timeout=10)
            if resp.status_code == 200:
                print(f"[Poller] ✓ ESP32 recovered!")
                self.esp32_healthy = True
                self.consecutive_failures = 0
                self.last_successful_contact = time.time()
                return True
        except Exception:
            pass
        
        print(f"[Poller] ✗ ESP32 still not responding")
        return False
    
    def fetch_with_retry(self, url, timeout, max_retries=3, operation_name="request"):
        """
        Fetch URL with retry logic and exponential backoff.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            operation_name: Name for logging
        
        Returns:
            Response object or None on failure
        """
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.get(url, timeout=timeout, stream=True)
                
                # Success - reset failure counter
                self.consecutive_failures = 0
                self.esp32_healthy = True
                self.last_successful_contact = time.time()
                
                return resp
                
            except requests.exceptions.ConnectionError:
                print(f"[Poller] ✗ Connection refused on {operation_name} (attempt {attempt}/{max_retries})")
                
                if attempt < max_retries:
                    wait = 5 * attempt  # Exponential backoff: 5s, 10s, 15s
                    print(f"[Poller]   Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    # All retries failed - ESP32 might be down
                    self.consecutive_failures += 1
                    if self.consecutive_failures >= 3:
                        self.esp32_healthy = False
                        print(f"[Poller] ⚠️  ESP32 marked unhealthy after {self.consecutive_failures} failures")
            
            except requests.exceptions.Timeout:
                print(f"[Poller] ✗ Timeout on {operation_name} (attempt {attempt}/{max_retries})")
                
                if attempt < max_retries:
                    wait = 3 * attempt  # Shorter backoff for timeouts
                    print(f"[Poller]   Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    self.consecutive_failures += 1
            
            except Exception as e:
                print(f"[Poller] ✗ Error on {operation_name}: {e}")
                if attempt >= max_retries:
                    self.consecutive_failures += 1
                    break
                time.sleep(2)
        
        return None
    
    def fetch_queue_list(self):
        """
        Fetch list of queued images from ESP32.
        ESP32 limits to 200 files to prevent memory exhaustion.
        Returns list of filenames (oldest first), or empty list on error.
        """
        # Longer timeout for queue list (SD card might be slow)
        resp = self.fetch_with_retry(
            self.queue_url, 
            timeout=30,  # Increased from 15
            max_retries=2,
            operation_name="queue list"
        )
        
        if resp and resp.status_code == 200:
            try:
                files = resp.json()
                if isinstance(files, list):
                    return files
            except Exception as e:
                print(f"[Poller] Could not parse queue list: {e}")
        
        return []
    
    def fetch_queued_image(self, filename):
        """
        Fetch a specific queued image from ESP32.
        Returns (image_data, timestamp) on success, or (None, None) on failure.
        """
        url = f"http://{self.esp32_ip}:{self.esp32_port}/queue/{filename}"
        
        # Much longer timeout for image fetch (SD read + network transfer)
        resp = self.fetch_with_retry(
            url,
            timeout=60,  # Increased from 15
            max_retries=3,
            operation_name=f"fetch {filename}"
        )
        
        if resp and resp.status_code == 200:
            try:
                image_data = resp.content
                
                # Extract timestamp from filename
                timestamp = filename.replace('.jpg', '').replace('.JPG', '')
                if '/' in timestamp:
                    timestamp = timestamp.split('/')[-1]
                
                return image_data, timestamp
            except Exception as e:
                print(f"[Poller] Error processing {filename}: {e}")
        
        return None, None
    
    def delete_queued_image(self, filename):
        """Tell ESP32 to delete a queued image after successful processing"""
        url = f"http://{self.esp32_ip}:{self.esp32_port}/queue/delete/{filename}"
        
        resp = self.fetch_with_retry(
            url,
            timeout=15,  # Increased from 5
            max_retries=2,
            operation_name=f"delete {filename}"
        )
        
        if resp and resp.status_code == 200:
            try:
                result = resp.json()
                return result.get('deleted', False)
            except Exception:
                pass
        
        return False
    
    def process_queued_images_batch(self):
        """
        Fetch and process ONE BATCH of queued images from ESP32.
        ESP32 limits to 200 files per request.
        
        Returns:
            Number of images successfully synced in this batch
        """
        # Check ESP32 health before attempting batch
        if not self.esp32_healthy:
            print(f"[Poller] ⚠️  Skipping batch - ESP32 unhealthy")
            if self.wait_for_esp32_recovery():
                print(f"[Poller] ESP32 recovered, resuming...")
            else:
                return 0
        
        files = self.fetch_queue_list()
        
        if not files:
            return 0
        
        batch_size = len(files)
        print(f"\n[Poller] ═══ Queue Batch: {batch_size} image(s) ═══")
        
        synced = 0
        batch_failures = 0
        
        for i, filename in enumerate(files, 1):
            print(f"[Poller] [{i}/{batch_size}] Fetching: {filename}")
            
            image_data, timestamp = self.fetch_queued_image(filename)
            
            if not image_data or not timestamp:
                print(f"[Poller] ✗ Failed to fetch {filename}")
                batch_failures += 1
                
                # If too many failures in batch, pause
                if batch_failures >= 5:
                    print(f"[Poller] ⚠️  Too many failures in batch, pausing...")
                    if not self.wait_for_esp32_recovery(20):
                        print(f"[Poller] Aborting batch")
                        break
                    batch_failures = 0  # Reset counter after recovery
                
                continue
            
            # Decode JPEG
            try:
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    print(f"[Poller] ✗ Failed to decode {filename}")
                    continue
            except Exception as e:
                print(f"[Poller] ✗ Decode error: {e}")
                continue
            
            # Save and analyze with original timestamp
            try:
                image_path = save_image(image, timestamp)
                analysis_results = analyze_image(image)
                
                # Mark as from SD in analysis results
                analysis_results['from_sd'] = True
                
                data_manager.update_latest(timestamp, image_path, analysis_results)
                data_manager.save_data()
                
                print(f"[Poller] ✓ Processed {filename}")
                print(f"[Poller]   {get_analysis_summary(analysis_results)}")
            except Exception as e:
                print(f"[Poller] ✗ Processing error: {e}")
                continue
            
            # Tell ESP32 to delete this file
            if self.delete_queued_image(filename):
                print(f"[Poller] ✓ Deleted from ESP32")
            else:
                print(f"[Poller] ⚠ Delete failed (file may remain)")
            
            synced += 1
            
            # Brief delay between fetches
            time.sleep(0.5)
        
        print(f"[Poller] ═══ Batch Complete: {synced}/{batch_size} synced ═══")
        
        return synced
    
    def sync_all_queued_images(self):
        """
        Sync ALL queued images in batches of 200.
        Continues checking for more until queue is empty.
        
        Returns:
            Total number of images synced across all batches
        """
        total_synced = 0
        batch_num = 0
        
        print(f"\n[Poller] 🔄 Starting queue sync...")
        
        while True:
            batch_num += 1
            
            # Sync one batch (up to 200 images)
            synced = self.process_queued_images_batch()
            total_synced += synced
            
            if synced == 0:
                # Queue is empty or ESP32 having issues
                break
            
            if synced < 200:
                # Partial batch means we got all remaining images
                print(f"[Poller] Queue empty (partial batch)")
                break
            
            # If we synced exactly 200, there might be more
            print(f"[Poller] Batch {batch_num} complete ({total_synced} total so far)")
            print(f"[Poller] Checking for more images...")
            time.sleep(3)  # Slightly longer pause to let ESP32 breathe
        
        if total_synced > 0:
            print(f"\n[Poller] ✅ Queue sync complete!")
            print(f"[Poller]    Total synced: {total_synced} images")
            print(f"[Poller]    Batches: {batch_num}")
            if batch_num > 0:
                print(f"[Poller]    Avg per batch: {total_synced/batch_num:.0f}\n")
        
        self.queue_synced_count += total_synced
        return total_synced
    
    def should_check_queue(self):
        """
        Determine if we should check the queue now.
        """
        current_time = time.time()
        
        # First check
        if self.last_queue_check == 0:
            return True
        
        # Periodic recheck
        if current_time - self.last_queue_check >= self.queue_check_interval:
            return True
        
        return False
    
    def fetch_and_process_live_image(self):
        """
        Fetch live image from ESP32 /capture endpoint.
        Returns True if successful, False otherwise.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n[Poller] Fetching live image...")
        
        # Check if ESP32 is healthy
        if not self.esp32_healthy:
            print(f"[Poller] ⚠️  ESP32 unhealthy, attempting recovery...")
            if not self.wait_for_esp32_recovery():
                return False
        
        resp = self.fetch_with_retry(
            self.capture_url,
            timeout=30,  # Increased from 15
            max_retries=2,
            operation_name="live capture"
        )
        
        if not resp:
            return False
        
        if resp.status_code == 200:
            try:
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
            except Exception as e:
                print(f"[Poller] ✗ Processing error: {e}")
                return False
        else:
            print(f"[Poller] ✗ ESP32 returned HTTP {resp.status_code}")
            return False
    
    def print_stats(self):
        """Print current polling statistics"""
        success_count = self.total_count - self.fail_count
        success_rate = (success_count / self.total_count * 100) if self.total_count > 0 else 0
        
        health_icon = "✅" if self.esp32_healthy else "⚠️ "
        print(f"[Poller] {health_icon} Stats: {success_count}/{self.total_count} successful ({success_rate:.0f}%)")
        
        if self.queue_synced_count > 0:
            print(f"[Poller]        {self.queue_synced_count} synced from SD queue")
        
        if not self.esp32_healthy:
            time_since_contact = time.time() - self.last_successful_contact
            print(f"[Poller]        ⚠️  ESP32 unhealthy ({time_since_contact:.0f}s since last contact)")
    
    def run(self):
        """Main polling loop - run in background thread"""
        print("\n[Poller] Starting - waiting 5 seconds for server to initialize...")
        time.sleep(5)
        
        self.check_esp32_reachable()
        
        print(f"[Poller] Running every {self.poll_interval}s")
        print(f"[Poller] Queue check every {self.queue_check_interval}s")
        print(f"[Poller] Ctrl+C to stop\n")
        
        # Initial queue sync on startup
        print("[Poller] Performing initial queue sync...")
        print("[Poller] ⏸️  Live captures paused during queue sync\n")
        synced = self.sync_all_queued_images()
        self.last_queue_check = time.time()
        
        if synced > 0:
            print(f"\n[Poller] ▶️  Queue sync complete - resuming live captures\n")
        
        while True:
            t_start = time.time()
            self.polls_since_queue_check += 1
            
            # ── Periodic Queue Check ──
            queue_sync_active = False
            if self.should_check_queue():
                print(f"\n[Poller] 🔍 Periodic queue check ({self.polls_since_queue_check} polls since last check)...")
                
                # Check if there are queued images
                queue_files = self.fetch_queue_list()
                if queue_files:
                    print(f"[Poller] ⏸️  {len(queue_files)} queued images found - pausing live captures")
                    queue_sync_active = True
                    
                    # Sync entire queue without interruption
                    synced = self.sync_all_queued_images()
                    self.last_queue_check = time.time()
                    self.polls_since_queue_check = 0
                    
                    if synced > 0:
                        print(f"[Poller] ▶️  Queue sync complete - resuming live captures\n")
                else:
                    print(f"[Poller] Queue is empty")
                    self.last_queue_check = time.time()
                    self.polls_since_queue_check = 0
            
            # ── Live capture ──
            # ONLY capture if NOT syncing queue
            if not queue_sync_active:
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
                
                queue_check_in = self.queue_check_interval - (time.time() - self.last_queue_check)
                print(f"[Poller] Next capture in {wait:.0f}s (queue check in {queue_check_in:.0f}s)")
                time.sleep(wait)
            else:
                # Skip wait if we just did queue sync
                print(f"[Poller] Queue sync completed, continuing immediately...")
                self.last_queue_check = time.time()

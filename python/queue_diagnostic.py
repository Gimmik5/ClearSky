"""
Queue Sync Diagnostic Tool

Run this to check if ESP32 queue sync is working properly.

Usage:
    python queue_diagnostic.py [ESP32_IP]
    
Example:
    python queue_diagnostic.py REDACTED
"""

import sys
import requests
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python queue_diagnostic.py [ESP32_IP]")
        print("Example: python queue_diagnostic.py REDACTED")
        sys.exit(1)
    
    esp32_ip = sys.argv[1]
    esp32_port = 80
    
    print("=" * 60)
    print("ESP32 Queue Sync Diagnostic")
    print("=" * 60)
    print(f"\nESP32: {esp32_ip}:{esp32_port}\n")
    
    # Step 1: Check if ESP32 is reachable
    print("[1/5] Checking ESP32 connectivity...")
    try:
        resp = requests.get(f"http://{esp32_ip}:{esp32_port}/status", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✓ ESP32 is reachable")
            print(f"    Uptime: {data.get('uptime', 0)}s")
            print(f"    Free heap: {data.get('freeHeap', 0)} bytes")
            print(f"    WiFi RSSI: {data.get('wifi_rssi', 0)} dBm")
        else:
            print(f"  ✗ HTTP {resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"  ✗ Cannot reach ESP32: {e}")
        sys.exit(1)
    
    # Step 2: Check SD card status
    print("\n[2/5] Checking SD card...")
    sd_available = data.get('sd_available', False)
    if sd_available:
        queue_count = data.get('sd_queue_count', 0)
        usage_pct = data.get('sd_usage_percent', 0)
        print(f"  ✓ SD card available")
        print(f"    Queue count: {queue_count}")
        print(f"    Usage: {usage_pct}%")
    else:
        print(f"  ✗ SD card not available")
        print(f"    Queue sync requires SD card to be working")
        sys.exit(1)
    
    # Step 3: Check queue endpoint
    print("\n[3/5] Checking /queue endpoint...")
    try:
        resp = requests.get(f"http://{esp32_ip}:{esp32_port}/queue", timeout=5)
        if resp.status_code == 200:
            files = resp.json()
            print(f"  ✓ Queue endpoint works")
            print(f"    Files in queue: {len(files)}")
            if len(files) > 0:
                print(f"    Oldest: {files[0]}")
                print(f"    Newest: {files[-1]}")
            else:
                print(f"    ⚠ Queue is empty (no images to sync)")
        else:
            print(f"  ✗ HTTP {resp.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Step 4: Try fetching a queued image
    print("\n[4/5] Testing queue file fetch...")
    if len(files) > 0:
        test_file = files[0]
        try:
            resp = requests.get(
                f"http://{esp32_ip}:{esp32_port}/queue/{test_file}", 
                timeout=10,
                stream=True
            )
            if resp.status_code == 200:
                size = len(resp.content)
                print(f"  ✓ Successfully fetched {test_file}")
                print(f"    Size: {size} bytes")
            else:
                print(f"  ✗ HTTP {resp.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    else:
        print(f"  ⊘ Skipped (no files in queue)")
    
    # Step 5: Check Python poller
    print("\n[5/5] Checking Python poller code...")
    try:
        with open('esp32_poller.py', 'r') as f:
            code = f.read()
            
        if 'process_queued_images' in code:
            print(f"  ✓ Poller has queue sync function")
        else:
            print(f"  ✗ Poller missing queue sync function")
            print(f"    Your esp32_poller.py is outdated!")
            print(f"    Replace with the V1.1 version")
            
        if 'fetch_queue_list' in code:
            print(f"  ✓ Poller can fetch queue list")
        else:
            print(f"  ✗ Poller missing queue list function")
            
        # Check if queue sync is actually called
        if 'process_queued_images()' in code:
            print(f"  ✓ Queue sync is called in run loop")
        else:
            print(f"  ✗ Queue sync NOT called in run loop")
            print(f"    Even though function exists, it's not being used!")
    except FileNotFoundError:
        print(f"  ✗ esp32_poller.py not found in current directory")
        print(f"    Run this script from your python/ folder")
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)
    
    # Summary
    print("\nSUMMARY:")
    if sd_available and len(files) > 0:
        print(f"  • ESP32 has {len(files)} image(s) queued")
        print(f"  • These should sync when Python starts polling")
        print(f"\nNEXT STEPS:")
        print(f"  1. Make sure you're using the V1.1 esp32_poller.py")
        print(f"  2. Start the Python server: python main.py")
        print(f"  3. Watch console for '[Poller] Queue Sync' messages")
        print(f"  4. Images should sync oldest-first automatically")
    elif sd_available and len(files) == 0:
        print(f"  • ESP32 SD card is working but queue is empty")
        print(f"  • This is normal if poller was running the whole time")
        print(f"\nTO TEST QUEUE SYNC:")
        print(f"  1. Stop Python server (Ctrl+C)")
        print(f"  2. Visit http://{esp32_ip}/control/capture a few times")
        print(f"  3. Check queue: http://{esp32_ip}/queue")
        print(f"  4. Restart Python server and watch it sync")
    else:
        print(f"  • SD card is not available on ESP32")
        print(f"  • Check SD card is inserted and formatted as FAT32")
        print(f"  • Verify ENABLE_SD_CARD true in ESP32_Config.h")
    
    print()

if __name__ == '__main__':
    main()

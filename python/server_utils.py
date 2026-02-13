"""
Server Utilities Module
Helper functions for server startup and configuration
"""

import socket
import os
from python_config import (
    ENABLE_BRIGHTNESS_ANALYSIS, ENABLE_COLOR_ANALYSIS, ENABLE_SKY_FEATURES,
    SAVE_IMAGES, IMAGE_DIR, SAVE_ANALYSIS_DATA, DATA_FILE
)


def print_banner():
    """Print startup banner with ASCII art"""
    print("\n" + "="*60)
    print(" "*15 + "ESP32-CAM Sky Predictor Server")
    print(" "*20 + "V1 Modular Edition")
    print("="*60)
    print_configuration()


def print_configuration():
    """Print current configuration settings"""
    print("\nConfiguration:")
    print(f"  - Brightness Analysis: {'ON' if ENABLE_BRIGHTNESS_ANALYSIS else 'OFF'}")
    print(f"  - Color Analysis: {'ON' if ENABLE_COLOR_ANALYSIS else 'OFF'}")
    print(f"  - Sky Features: {'ON' if ENABLE_SKY_FEATURES else 'OFF'}")
    print(f"  - Save Images: {'ON' if SAVE_IMAGES else 'OFF'}")
    
    if SAVE_IMAGES:
        print(f"    Location: {os.path.abspath(IMAGE_DIR)}")
    
    print(f"  - Save Data: {'ON' if SAVE_ANALYSIS_DATA else 'OFF'}")
    
    if SAVE_ANALYSIS_DATA:
        print(f"    Location: {os.path.abspath(DATA_FILE)}")
    
    print()


def print_startup_info(port):
    """
    Print server startup information
    
    Args:
        port: Server port number
    """
    local_ip = get_local_ip()
    
    print("Server starting on:")
    print(f"  Local:   http://localhost:{port}")
    print(f"  Network: http://{local_ip}:{port}")
    print()
    print("Update your ESP32 with:")
    print(f'  const char* SERVER_URL = "http://{local_ip}:{port}/upload";')
    print()
    print("Web Interface:")
    print(f"  Main:  http://localhost:{port}")
    print(f"  Stats: http://localhost:{port}/stats")
    print()
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")


def get_local_ip():
    """
    Get local IP address
    
    Returns:
        str: Local IP address or 'unknown'
    """
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "unknown"


def validate_environment():
    """
    Validate that required directories exist
    
    Returns:
        bool: True if environment is valid
    """
    errors = []
    
    if SAVE_IMAGES:
        if not os.path.exists(IMAGE_DIR):
            try:
                os.makedirs(IMAGE_DIR)
                print(f"✓ Created image directory: {IMAGE_DIR}")
            except Exception as e:
                errors.append(f"Cannot create image directory: {e}")
    
    if errors:
        print("\n⚠️  Environment validation errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True

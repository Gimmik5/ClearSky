"""
Sky Predictor Server - V1 Modular (Refactored)
Main Entry Point - runs Flask web server + ESP32 poller together

Usage:
    python main.py

Press Ctrl+C to stop everything
"""

import threading
from python_config import HOST, PORT, DEBUG
from server_utils import print_banner, print_startup_info
from server_init import initialize_server
from graceful_shutdown import register_signal_handlers
from esp32_poller import ESP32Poller
from web_server import create_flask_app, start_web_server


# ── ESP32 Configuration ────────────────────────────────────────────────────────
ESP32_IP              = "192.168.1.104"  # Update if ESP32 IP changes
ESP32_PORT            = 80
POLL_INTERVAL_SECONDS = 10
REQUEST_TIMEOUT       = 15


def main():
    """Main entry point"""
    
    # Register signal handlers for graceful shutdown
    register_signal_handlers()
    
    # Print banner and startup info
    print_banner()
    
    # Initialize database and check migrations
    initialize_server()
    
    print_startup_info(PORT)
    
    # Create Flask app
    app = create_flask_app()
    
    # Start ESP32 poller in background thread
    poller = ESP32Poller(
        esp32_ip=ESP32_IP,
        esp32_port=ESP32_PORT,
        poll_interval=POLL_INTERVAL_SECONDS,
        request_timeout=REQUEST_TIMEOUT
    )
    
    poller_thread = threading.Thread(target=poller.run, daemon=True)
    poller_thread.start()
    print("[Poller] Background thread started")
    
    # Start web server (blocks main thread)
    start_web_server(app, HOST, PORT)


if __name__ == '__main__':
    main()

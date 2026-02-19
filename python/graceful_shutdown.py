"""
Graceful Shutdown Module
Handles signal handling and clean server shutdown
"""

import signal
import sys


def register_signal_handlers():
    """Register Ctrl+C handler for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)


def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) signal gracefully"""
    print("\n\n" + "="*60)
    print("Server shutting down...")
    print("="*60)
    sys.exit(0)


def print_shutdown_message():
    """Print shutdown completion message"""
    print("\n\n" + "="*60)
    print("Server stopped by user")
    print("="*60)

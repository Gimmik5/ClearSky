"""
Web Server Module
Handles Flask app creation and Waitress server configuration
"""

from flask import Flask
from python_config import ENABLE_CORS
from routes import register_routes


def create_flask_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    if ENABLE_CORS:
        from flask_cors import CORS
        CORS(app)
    
    register_routes(app)
    return app


def start_web_server(app, host, port):
    """
    Start the Waitress web server
    Blocks until server is stopped
    """
    from waitress import serve
    
    print(f"\nStarting Waitress server (multi-threaded)...")
    print("Press Ctrl+C to stop\n")
    
    try:
        serve(
            app,
            host=host,
            port=port,
            threads=8,
            channel_timeout=30,
            cleanup_interval=10
        )
    except KeyboardInterrupt:
        from graceful_shutdown import print_shutdown_message
        print_shutdown_message()

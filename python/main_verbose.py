"""
Verbose Server Wrapper
Logs ALL incoming connections including those that fail before routes
"""

from flask import Flask, request
from python_config import HOST, PORT, DEBUG, ENABLE_CORS
from routes import register_routes
from server_utils import print_banner, print_startup_info
from database_schema import create_database
import logging

# Set up verbose logging
logging.basicConfig(level=logging.DEBUG)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.DEBUG)

# Create Flask app
app = Flask(__name__)

if ENABLE_CORS:
    from flask_cors import CORS
    CORS(app)

# Add middleware to log every single request
@app.before_request
def log_request_info():
    print(f"\n{'='*60}")
    print(f"INCOMING REQUEST")
    print(f"{'='*60}")
    print(f"Client IP: {request.remote_addr}")
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"Headers:")
    for header, value in request.headers:
        print(f"  {header}: {value}")
    if request.method == "POST":
        print(f"Content-Length: {request.content_length}")
        print(f"Content-Type: {request.content_type}")
    print(f"{'='*60}\n")

# Register all routes
register_routes(app)

if __name__ == '__main__':
    print_banner()
    
    # Initialize database
    print("Initializing database...")
    create_database()
    
    # Check for JSON migration
    from migrate_json_to_sqlite import check_migration_needed
    if check_migration_needed():
        print("\n⚠️  Old JSON data detected!")
        print("   Run 'python migrate_json_to_sqlite.py' to migrate\n")
    
    print_startup_info(PORT)
    
    print("\n" + "="*60)
    print("VERBOSE LOGGING ENABLED")
    print("All incoming connections will be logged")
    print("="*60 + "\n")
    
    # Start Flask server with verbose logging
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)

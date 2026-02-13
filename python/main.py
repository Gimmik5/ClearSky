"""
Sky Predictor Server - V1 Modular
Main Entry Point

Usage:
    python main.py
"""

from flask import Flask
from python_config import HOST, PORT, DEBUG, ENABLE_CORS
from routes import register_routes
from server_utils import print_banner, print_startup_info
from database_schema import create_database

# Create Flask app
app = Flask(__name__)

if ENABLE_CORS:
    from flask_cors import CORS
    CORS(app)

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
    
    # Start Flask server
    app.run(host=HOST, port=PORT, debug=DEBUG)

# ClearSky V2.0 - Quick Reference Guide

## 🔄 Import Changes Cheat Sheet

This guide shows exactly how to update your imports during migration.

---

## Configuration Imports

### Before (V1)
```python
from python_config import (
    HOST, PORT, DEBUG,
    ESP32_IP, ESP32_PORT,
    ENABLE_BRIGHTNESS_ANALYSIS,
    DATABASE_PATH
)
```

### After (V2)
```python
from config.settings import HOST, PORT, DEBUG
from config.hardware_config import ESP32_IP, ESP32_PORT
from config.analysis_config import ENABLE_BRIGHTNESS_ANALYSIS
from config.database_config import DATABASE_PATH
```

### Or use grouped import
```python
from config import settings, hardware, analysis, database

# Access as:
settings.HOST
hardware.ESP32_IP
analysis.ENABLE_BRIGHTNESS_ANALYSIS
database.DATABASE_PATH
```

---

## Database Imports

### Before (V1)
```python
from data_manager_sqlite import data_manager
from database_schema import initialize_database
from database_operations import get_latest_record, get_all_records
from image_storage import save_image, get_image_path
```

### After (V2)
```python
from data.manager import data_manager
from data.schema import initialize_database
from data.operations import get_latest_record, get_all_records
from data.storage.image_storage import save_image, get_image_path
```

### Or use package-level imports
```python
from data import data_manager, initialize_database
from data.operations import get_latest_record, get_all_records
from data.storage import save_image, get_image_path
```

---

## Analysis Imports

### Before (V1)
```python
from analysis_core import analyze_image
from brightness_analysis import analyze_brightness
from color_analysis import analyze_color
from sky_features import detect_sky_features
```

### After (V2)
```python
from analysis.core import analyze_image
from analysis.brightness import analyze_brightness
from analysis.color import analyze_color
from analysis.sky_features import detect_sky_features
```

### Better: Use unified pipeline
```python
from analysis import AnalysisPipeline

pipeline = AnalysisPipeline()
results = pipeline.analyze(image)
```

---

## Hardware Imports

### Before (V1)
```python
from esp32_poller import ESP32Poller
```

### After (V2)
```python
from hardware.poller import ESP32Poller
```

### Or with new connection management
```python
from hardware.poller import ESP32Poller
from hardware.connection import ESP32Connection
from hardware.protocol import ImageProtocol
```

---

## Web Imports

### Before (V1)
```python
from web_server import create_flask_app, start_web_server
from routes import register_routes
from web_templates import HTML_TEMPLATE, STATS_PAGE_TEMPLATE
```

### After (V2)
```python
from web.app import create_flask_app, start_web_server
from web.routes import register_all_routes
# Templates are now files, not Python strings
```

### Individual route blueprints
```python
from web.routes.main_routes import main_bp
from web.routes.api_routes import api_bp
from web.routes.gallery_routes import gallery_bp
from web.routes.viewer_routes import viewer_bp

app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(gallery_bp, url_prefix='/gallery')
app.register_blueprint(viewer_bp, url_prefix='/viewer')
```

---

## Utilities Imports

### Before (V1)
```python
from server_utils import print_banner, print_startup_info
from graceful_shutdown import register_signal_handlers
```

### After (V2)
```python
from utils.server_utils import print_banner, print_startup_info
from utils.shutdown import register_signal_handlers
from utils.logger import get_logger

logger = get_logger(__name__)
```

---

## 🏗️ Code Pattern Changes

### 1. Configuration Loading

#### Before (V1)
```python
# python_config.py
HOST = "0.0.0.0"
PORT = 8080
DEBUG = True
ESP32_IP = "192.168.1.104"
```

#### After (V2)
```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Server settings
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# .env file
# HOST=0.0.0.0
# PORT=8080
# FLASK_DEBUG=True
```

---

### 2. Database Initialization

#### Before (V1)
```python
# In main.py
from database_schema import initialize_database
initialize_database()
```

#### After (V2)
```python
# In main.py
from data.schema import initialize_database
initialize_database()

# Or better: use initialization script
from scripts.init_database import setup_database
setup_database()
```

---

### 3. Flask App Creation

#### Before (V1)
```python
# web_server.py
from flask import Flask
from flask_cors import CORS

def create_flask_app():
    app = Flask(__name__)
    CORS(app)
    return app
```

#### After (V2)
```python
# web/app.py
from flask import Flask
from flask_cors import CORS
from web.routes import register_all_routes

def create_flask_app():
    app = Flask(__name__)
    app.config.from_object('config.settings')
    CORS(app)
    register_all_routes(app)
    return app
```

---

### 4. Route Registration

#### Before (V1)
```python
# routes.py - everything in one file
from flask import request, jsonify

def register_routes(app):
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/latest')
    def api_latest():
        return jsonify(data_manager.get_latest())
```

#### After (V2)
```python
# web/routes/main_routes.py
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

# web/routes/api_routes.py
from flask import Blueprint, jsonify
from data.manager import data_manager

api_bp = Blueprint('api', __name__)

@api_bp.route('/latest')
def api_latest():
    return jsonify(data_manager.get_latest())

# web/routes/__init__.py
from web.routes.main_routes import main_bp
from web.routes.api_routes import api_bp

def register_all_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
```

---

### 5. Template Usage

#### Before (V1)
```python
# web_templates.py
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>ClearSky</title></head>
<body>
    <h1>{{ title }}</h1>
</body>
</html>
"""

# In route
return render_template_string(HTML_TEMPLATE, title="ClearSky")
```

#### After (V2)
```python
# web/templates/index.html
<!DOCTYPE html>
<html>
<head><title>ClearSky</title></head>
<body>
    <h1>{{ title }}</h1>
</body>
</html>

# In route
return render_template('index.html', title="ClearSky")
```

---

### 6. Logging

#### Before (V1)
```python
print("[Poller] Starting ESP32 polling...")
print(f"[ERROR] Failed to connect: {error}")
```

#### After (V2)
```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Starting ESP32 polling...")
logger.error(f"Failed to connect: {error}")
```

---

### 7. Analysis Pipeline

#### Before (V1)
```python
# In esp32_poller.py
from brightness_analysis import analyze_brightness
from color_analysis import analyze_color
from sky_features import detect_sky_features

# Analyze separately
brightness_result = analyze_brightness(image)
color_result = analyze_color(image)
sky_result = detect_sky_features(image)

# Combine manually
result = {**brightness_result, **color_result, **sky_result}
```

#### After (V2)
```python
# In hardware/poller.py
from analysis import AnalysisPipeline

pipeline = AnalysisPipeline()
result = pipeline.analyze(image)  # All-in-one
```

---

## 🧪 Testing Patterns

### Unit Test Example (NEW in V2)

```python
# tests/test_analysis/test_brightness.py
import pytest
from analysis.brightness import analyze_brightness
from PIL import Image
import numpy as np

def test_analyze_brightness_very_bright():
    # Create test image (white)
    img = Image.new('RGB', (100, 100), (255, 255, 255))
    result = analyze_brightness(img)
    
    assert result['brightness_average'] > 200
    assert result['brightness_condition'] == 'Very Bright'

def test_analyze_brightness_dark():
    # Create test image (black)
    img = Image.new('RGB', (100, 100), (0, 0, 0))
    result = analyze_brightness(img)
    
    assert result['brightness_average'] < 50
    assert result['brightness_condition'] == 'Dark'
```

### Integration Test Example

```python
# tests/test_web/test_routes.py
import pytest
from web.app import create_flask_app

@pytest.fixture
def client():
    app = create_flask_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'ClearSky' in response.data

def test_api_latest(client):
    response = client.get('/api/latest')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
```

---

## 📦 Package Structure Best Practices

### config/__init__.py
```python
"""Configuration management for ClearSky"""
from config.settings import *
from config import hardware_config as hardware
from config import analysis_config as analysis
from config import database_config as database

__all__ = ['settings', 'hardware', 'analysis', 'database']
```

### data/__init__.py
```python
"""Data layer for ClearSky"""
from data.manager import data_manager
from data.schema import initialize_database
from data import operations

__all__ = ['data_manager', 'initialize_database', 'operations']
```

### analysis/__init__.py
```python
"""Image analysis modules"""
from analysis.core import AnalysisPipeline
from analysis.brightness import analyze_brightness
from analysis.color import analyze_color
from analysis.sky_features import detect_sky_features

__all__ = [
    'AnalysisPipeline',
    'analyze_brightness',
    'analyze_color',
    'detect_sky_features'
]
```

### web/__init__.py
```python
"""Web interface for ClearSky"""
from web.app import create_flask_app, start_web_server

__all__ = ['create_flask_app', 'start_web_server']
```

---

## 🔧 Utility Functions

### Logger Setup (NEW)

```python
# utils/logger.py
import logging
import sys
from config.settings import LOG_LEVEL, LOG_FILE

def get_logger(name):
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Usage
from utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Application started")
```

---

## 🚀 Main Entry Point

### Updated main.py (V2)

```python
"""
ClearSky V2.0 - Sky Monitoring System
Main application entry point
"""
import threading
from config import settings, hardware
from utils.server_utils import print_banner, print_startup_info
from utils.shutdown import register_signal_handlers
from utils.logger import get_logger
from scripts.init_database import initialize_server
from hardware.poller import ESP32Poller
from web import create_flask_app, start_web_server

logger = get_logger(__name__)

def main():
    """Main entry point"""
    # Setup
    register_signal_handlers()
    print_banner()
    initialize_server()
    print_startup_info(settings.PORT)
    
    # Create Flask app
    app = create_flask_app()
    
    # Start ESP32 poller
    poller = ESP32Poller(
        esp32_ip=hardware.ESP32_IP,
        esp32_port=hardware.ESP32_PORT,
        poll_interval=hardware.POLL_INTERVAL_SECONDS,
        request_timeout=hardware.REQUEST_TIMEOUT
    )
    
    poller_thread = threading.Thread(target=poller.run, daemon=True)
    poller_thread.start()
    logger.info("Poller thread started")
    
    # Start web server
    start_web_server(app, settings.HOST, settings.PORT)

if __name__ == '__main__':
    main()
```

---

## 📝 Environment Variables (.env)

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production

# Server Configuration
HOST=0.0.0.0
PORT=8080

# Database Configuration
DATABASE_PATH=./clearsky.db
DATABASE_BACKUP_PATH=./backups/

# ESP32 Configuration
ESP32_IP=192.168.1.104
ESP32_PORT=80
POLL_INTERVAL_SECONDS=10
REQUEST_TIMEOUT=15

# Analysis Configuration
ENABLE_BRIGHTNESS_ANALYSIS=True
ENABLE_COLOR_ANALYSIS=True
ENABLE_SKY_FEATURES=True

# Image Storage
IMAGE_DIR=./images/
MAX_IMAGE_AGE_DAYS=30

# Thresholds
BRIGHTNESS_VERY_BRIGHT=180
BRIGHTNESS_BRIGHT=130
BRIGHTNESS_MODERATE=80
BRIGHTNESS_DIM=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/clearsky.log
```

---

## 🎯 Quick Migration Commands

### Step-by-step migration
```bash
# 1. Create branch
git checkout -b v2.0-restructure

# 2. Create folder structure
bash setup_v2_structure.sh

# 3. Copy files (example for config)
cp python_config.py config/settings.py

# 4. Update imports in the new file
sed -i 's/from python_config/from config.settings/g' config/settings.py

# 5. Find all files that import python_config
grep -r "from python_config" --include="*.py"

# 6. Update each file's imports
# (Do this manually or create a script)

# 7. Test import
python -c "from config import settings; print(settings.HOST)"

# 8. Commit changes
git add .
git commit -m "feat: migrate config module to config/ directory"
```

---

## 🔍 Troubleshooting Import Issues

### Common Error: Module not found
```
ModuleNotFoundError: No module named 'config'
```

**Solution**: Add `__init__.py` to the directory
```bash
touch config/__init__.py
```

### Common Error: Circular import
```
ImportError: cannot import name 'X' from partially initialized module 'Y'
```

**Solution**: Move import inside function or restructure dependencies
```python
# Instead of:
from analysis.core import AnalysisPipeline

def process():
    pipeline = AnalysisPipeline()

# Do:
def process():
    from analysis.core import AnalysisPipeline
    pipeline = AnalysisPipeline()
```

### Common Error: Relative import beyond top-level
```
ValueError: attempted relative import beyond top-level package
```

**Solution**: Use absolute imports
```python
# Instead of:
from ..config import settings

# Do:
from config import settings
```

---

This quick reference should speed up your migration significantly!

# ClearSky V2.0 - Architecture & Migration Plan

## 📋 Executive Summary

ClearSky V2.0 introduces a clean, modular architecture with proper separation of concerns:
- **Web layer** decoupled from business logic
- **Database** as the single source of truth
- **Analysis** as independent, testable modules
- **ESP32 polling** isolated from web concerns
- **Scalable structure** ready for ML integration

---

## 🌳 Git Branch Strategy

### Creating V2.0 Branch

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create and switch to v2.0-restructure branch
git checkout -b v2.0-restructure

# Verify you're on the new branch
git branch
```

### Commit Strategy
```bash
# Initial structure commit
git add .
git commit -m "feat: V2.0 folder structure and reorganization"

# Module migration commits (do these incrementally)
git commit -m "feat: migrate database modules to data/"
git commit -m "feat: migrate web modules to web/"
git commit -m "feat: migrate analysis modules to analysis/"
git commit -m "feat: migrate ESP32 polling to hardware/"
git commit -m "feat: add configuration management to config/"
git commit -m "docs: update documentation for V2.0"

# Final merge back to main when stable
git checkout main
git merge v2.0-restructure
git push origin main
```

---

## 📁 Proposed V2.0 Folder Structure

### Python Application Root
```
clearsky/
├── config/                      # Configuration management
│   ├── __init__.py
│   ├── settings.py             # Centralized config (replaces python_config.py)
│   ├── database_config.py      # DB-specific settings
│   ├── hardware_config.py      # ESP32 settings
│   └── analysis_config.py      # Analysis thresholds and params
│
├── data/                        # Database layer
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schema.py               # Database schema (from database_schema.py)
│   ├── operations.py           # CRUD operations (from database_operations.py)
│   ├── manager.py              # Data manager (from data_manager_sqlite.py)
│   ├── migrations/             # Database migrations
│   │   ├── __init__.py
│   │   └── migrate_json_to_sqlite.py
│   └── storage/                # File storage management
│       ├── __init__.py
│       └── image_storage.py
│
├── analysis/                    # Image analysis modules
│   ├── __init__.py
│   ├── core.py                 # Core analysis logic (from analysis_core.py)
│   ├── brightness.py           # Brightness analysis (from brightness_analysis.py)
│   ├── color.py                # Color analysis (from color_analysis.py)
│   ├── sky_features.py         # Sky-specific features
│   └── ml/                     # Machine learning (future)
│       ├── __init__.py
│       ├── models/             # Trained models storage
│       ├── training/           # Training scripts
│       └── inference.py        # ML inference pipeline
│
├── hardware/                    # ESP32 communication
│   ├── __init__.py
│   ├── poller.py               # ESP32 poller (from esp32_poller.py)
│   ├── connection.py           # Connection management
│   └── protocol.py             # Communication protocol
│
├── web/                         # Web interface layer
│   ├── __init__.py
│   ├── app.py                  # Flask app factory (from web_server.py)
│   ├── routes/                 # Route handlers
│   │   ├── __init__.py
│   │   ├── main_routes.py     # Home, stats
│   │   ├── api_routes.py      # JSON API endpoints
│   │   ├── gallery_routes.py  # Gallery views
│   │   └── viewer_routes.py   # Image viewer
│   ├── templates/              # HTML templates
│   │   ├── base.html          # Base template (from template_base.py)
│   │   ├── index.html         # Main page
│   │   ├── stats.html         # Statistics page
│   │   ├── gallery/
│   │   │   ├── index.html
│   │   │   └── day.html
│   │   └── viewer/
│   │       └── viewer.html
│   ├── static/                 # Static assets
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   └── viewer.css
│   │   ├── js/
│   │   │   ├── api_client.js
│   │   │   ├── gallery.js
│   │   │   └── viewer.js
│   │   └── img/
│   │       └── favicon.ico
│   └── components/             # Reusable template components
│       ├── __init__.py
│       ├── daily_view.py
│       └── image_viewer.py
│
├── utils/                       # Shared utilities
│   ├── __init__.py
│   ├── server_utils.py         # Server helpers (banner, etc.)
│   ├── shutdown.py             # Graceful shutdown (from graceful_shutdown.py)
│   ├── logger.py               # Centralized logging
│   └── diagnostics.py          # Queue diagnostic tools
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_analysis/
│   │   ├── test_brightness.py
│   │   ├── test_color.py
│   │   └── test_sky_features.py
│   ├── test_data/
│   │   ├── test_operations.py
│   │   └── test_manager.py
│   ├── test_hardware/
│   │   └── test_poller.py
│   └── test_web/
│       ├── test_routes.py
│       └── test_api.py
│
├── scripts/                     # Utility scripts
│   ├── init_database.py        # Database initialization
│   ├── diagnostic_queue.py     # Queue diagnostics
│   └── export_data.py          # Data export utilities
│
├── docs/                        # Documentation
│   ├── API.md                  # API documentation
│   ├── ARCHITECTURE.md         # Architecture overview
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── TROUBLESHOOTING.md
│
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore
└── README.md
```

### ESP32 Firmware Structure (if separate repo)
```
clearsky-firmware/
├── src/
│   ├── main.cpp                # Main entry point
│   ├── camera/
│   │   ├── camera_init.h
│   │   ├── camera_init.cpp
│   │   └── camera_config.h
│   ├── network/
│   │   ├── wifi_manager.h
│   │   ├── wifi_manager.cpp
│   │   └── web_server.h
│   ├── sensors/                # Future sensor integration
│   │   └── placeholder.txt
│   └── utils/
│       ├── logger.h
│       └── config.h
├── lib/                        # External libraries
├── include/                    # Header files
├── test/                       # Unit tests
├── platformio.ini              # PlatformIO config
└── README.md
```

---

## 🔄 Migration Path

### Phase 1: Create Structure (Week 1)
1. Create new folder structure
2. Add `__init__.py` to all Python packages
3. Create empty placeholder files
4. Set up basic imports

### Phase 2: Migrate Core Modules (Week 1-2)
1. **Config Migration**
   - Move `python_config.py` → `config/settings.py`
   - Create specialized config modules
   - Add environment variable support (.env)

2. **Database Migration**
   - Move database modules to `data/`
   - Refactor imports throughout codebase
   - Update all references

3. **Analysis Migration**
   - Move analysis modules to `analysis/`
   - Create unified analysis interface
   - Add analysis pipeline

4. **Hardware Migration**
   - Move `esp32_poller.py` → `hardware/poller.py`
   - Extract connection logic
   - Add retry mechanisms

### Phase 3: Web Refactor (Week 2-3)
1. **Split Routes**
   - Break `routes.py` into logical route modules
   - Create route blueprints
   - Separate API from page routes

2. **Template Organization**
   - Convert inline templates to files
   - Move to `web/templates/`
   - Create base template with inheritance
   - Extract CSS/JS to static files

3. **Component Extraction**
   - Move `daily_view.py` → `web/components/`
   - Move `image_viewer.py` → `web/components/`
   - Create reusable component system

### Phase 4: Testing & Documentation (Week 3-4)
1. Add unit tests for each module
2. Add integration tests
3. Update documentation
4. Create deployment guide

---

## 🎯 Key Architectural Changes

### 1. Database-Centric Design
**Current**: Web server sometimes generates data on-the-fly
**V2.0**: Database is the single source of truth

```python
# OLD: Direct analysis in route
@app.route('/analyze/<filename>')
def analyze(filename):
    image = load_image(filename)
    result = analyze_image(image)  # On-the-fly
    return jsonify(result)

# NEW: Database query only
@app.route('/analyze/<filename>')
def analyze(filename):
    result = db.get_analysis(filename)  # Pre-analyzed
    return jsonify(result)
```

### 2. Decoupled Web Layer
**Current**: Routes import analysis directly
**V2.0**: Routes only interact with data layer

```python
# OLD: web/routes.py imports analysis modules directly
from brightness_analysis import analyze_brightness
from color_analysis import analyze_color

# NEW: web/routes.py only imports data layer
from data.manager import data_manager
```

### 3. Async Analysis Pipeline
**Current**: Synchronous polling and analysis
**V2.0**: Background workers with queue

```python
# NEW: Analysis queue
from analysis.core import AnalysisQueue

queue = AnalysisQueue()
queue.add_image(image_path)
# Worker processes in background
# Results written to database
# Web server reads from database
```

---

## 🛠️ Recommended Tools & Libraries

### Web Development
1. **Frontend Framework** (Choose one based on complexity)
   - **htmx** - Minimal JS, perfect for your use case
     - Pros: Simple, no build step, progressive enhancement
     - Use: AJAX updates without page refresh
   - **Alpine.js** - Lightweight reactivity
     - Pros: Vue-like syntax, <10KB, no build step
     - Use: Interactive components (galleries, viewers)
   - **Vue.js** - Full framework (if going complex)
     - Pros: Component-based, reactive, good docs
     - Use: Rich dashboard with real-time updates

2. **CSS Framework**
   - **Tailwind CSS** - Utility-first (recommended)
   - **Bootstrap 5** - Component library (simpler)
   - **DaisyUI** - Tailwind components (best of both)

3. **Chart/Visualization**
   - **Chart.js** - Simple, responsive charts
   - **Plotly.js** - Interactive scientific plots
   - **D3.js** - Full control (steeper learning curve)

4. **Template Engine**
   - Stick with **Jinja2** (Flask default)
   - Consider template inheritance strategy

### Database
1. **SQLAlchemy ORM** - Add for cleaner DB code
2. **Alembic** - Database migrations
3. **SQLite Browser** - Visual DB inspection

### Testing
1. **pytest** - Test framework
2. **pytest-cov** - Code coverage
3. **pytest-flask** - Flask testing utilities
4. **Faker** - Generate test data

### Development
1. **Flask-DebugToolbar** - Development debugging
2. **Flask-Limiter** - Rate limiting
3. **python-dotenv** - Environment variables
4. **black** - Code formatting
5. **flake8** - Linting
6. **mypy** - Type checking

### Machine Learning (Future)
1. **scikit-learn** - Traditional ML
   - Sky condition classification
   - Weather pattern recognition
2. **TensorFlow Lite** or **ONNX** - Lightweight inference
3. **OpenCV** - Advanced image processing
4. **PIL/Pillow** - Current image library (keep)

### C++ Learning & ESP32
1. **PlatformIO** - Modern ESP32 development
   - Better than Arduino IDE
   - Built-in testing, debugging
   - Library management
2. **ESP-IDF** - Official Espressif framework
   - More control than Arduino
   - Professional development
3. **GoogleTest** - C++ unit testing
4. **Doxygen** - C++ documentation
5. **VS Code + PlatformIO** - Best development setup

### Monitoring & Diagnostics
1. **Flask-Monitoring-Dashboard** - Performance tracking
2. **Prometheus + Grafana** - Time-series metrics
3. **Sentry** - Error tracking
4. **Loguru** - Better logging than standard library

### DevOps
1. **Docker** - Containerization
2. **Docker Compose** - Multi-container apps
3. **GitHub Actions** - CI/CD pipeline
4. **Pre-commit hooks** - Code quality gates

---

## 📊 Data Flow Architecture (V2.0)

```
┌─────────────┐
│   ESP32     │
│   Camera    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────┐
│  hardware/      │
│  poller.py      │ ← Fetches images every N seconds
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  analysis/      │
│  pipeline       │ ← Analyzes images (brightness, color, sky)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  data/          │
│  database       │ ← Stores results + image metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  web/           │
│  routes         │ ← Reads from database ONLY
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Browser        │
│  (User)         │ ← Views pre-analyzed data
└─────────────────┘
```

**Key Principle**: Web layer NEVER triggers analysis. It only displays what's already in the database.

---

## 🚀 Quick Start Migration Script

Create this script to automate the folder creation:

```bash
#!/bin/bash
# setup_v2_structure.sh

echo "Creating ClearSky V2.0 folder structure..."

# Create main directories
mkdir -p config data/migrations data/storage analysis/ml/models analysis/ml/training
mkdir -p hardware web/routes web/templates/gallery web/templates/viewer
mkdir -p web/static/css web/static/js web/static/img web/components
mkdir -p utils tests/test_analysis tests/test_data tests/test_hardware tests/test_web
mkdir -p scripts docs

# Create __init__.py files
touch config/__init__.py data/__init__.py data/migrations/__init__.py data/storage/__init__.py
touch analysis/__init__.py analysis/ml/__init__.py hardware/__init__.py
touch web/__init__.py web/routes/__init__.py web/components/__init__.py
touch utils/__init__.py tests/__init__.py

# Create placeholder files
touch config/settings.py config/database_config.py config/hardware_config.py
touch data/models.py data/schema.py data/operations.py data/manager.py
touch analysis/core.py analysis/brightness.py analysis/color.py
touch hardware/poller.py hardware/connection.py
touch web/app.py web/routes/main_routes.py web/routes/api_routes.py
touch utils/logger.py utils/shutdown.py
touch .env.example requirements.txt

echo "✓ V2.0 structure created successfully!"
echo "Next steps:"
echo "1. Run this script: bash setup_v2_structure.sh"
echo "2. Copy files from root to new locations"
echo "3. Update imports in each file"
echo "4. Test each module independently"
```

---

## 📈 Benefits of V2.0 Architecture

### 1. Maintainability
- Clear module boundaries
- Easy to locate code
- Single responsibility principle

### 2. Testability
- Each module can be tested independently
- Mock dependencies easily
- Better test coverage

### 3. Scalability
- Add ML models without touching web code
- Support multiple ESP32 devices
- Easy to add new analysis features

### 4. Performance
- Database queries are fast
- No on-the-fly analysis blocking requests
- Can cache results efficiently

### 5. Team Collaboration
- Clear ownership of modules
- Parallel development possible
- Less merge conflicts

### 6. Future-Ready
- Ready for microservices split
- Ready for async/await Python
- Ready for ML integration
- Ready for mobile app backend

---

## 🎓 Learning Resources

### Web Development
- **htmx**: https://htmx.org/docs/
- **Alpine.js**: https://alpinejs.dev/start-here
- **Tailwind**: https://tailwindcss.com/docs

### Python
- **Flask Mega-Tutorial**: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/en/14/orm/tutorial.html
- **pytest**: https://docs.pytest.org/en/stable/

### ESP32/C++
- **PlatformIO**: https://docs.platformio.org/en/latest/
- **ESP32 Camera Guide**: https://randomnerdtutorials.com/esp32-cam-take-photo-display-web-server/
- **Modern C++**: https://www.learncpp.com/

### Machine Learning
- **scikit-learn**: https://scikit-learn.org/stable/tutorial/index.html
- **TensorFlow Lite**: https://www.tensorflow.org/lite/guide
- **OpenCV Python**: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html

---

## 🎯 Priority Recommendations

### Week 1 - Foundation
1. Create branch: `v2.0-restructure`
2. Run folder structure script
3. Migrate config module
4. Set up `.env` file support

### Week 2 - Core Migration
1. Migrate database modules
2. Migrate analysis modules
3. Update all imports
4. Test each module

### Week 3 - Web Refactor
1. Split routes into blueprints
2. Move templates to files
3. Extract CSS/JS
4. Add htmx for interactivity

### Week 4 - Polish
1. Add tests
2. Update documentation
3. Performance optimization
4. Deployment preparation

---

## 📞 Next Steps

1. **Review this plan** and adjust based on your priorities
2. **Create the branch** and folder structure
3. **Start with config migration** (smallest, easiest)
4. **Test incrementally** - don't migrate everything at once
5. **Ask questions** if anything is unclear

This is a living document - update it as you learn more during migration!

---

**Version**: 1.0  
**Date**: 2026-03-10  
**Author**: ClearSky Development Team

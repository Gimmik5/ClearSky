# ClearSky V2.0 - Tools & Technologies Guide

## 📚 Comprehensive Tool Recommendations

This guide provides detailed information about recommended tools, libraries, and technologies for ClearSky V2.0 development.

---

## 🎨 Frontend Development

### 1. htmx - Recommended for ClearSky ⭐

**Why htmx is perfect for your use case:**
- No build step required - just include a CDN script
- AJAX updates without writing JavaScript
- Progressive enhancement - works without JS enabled
- Minimal learning curve
- Perfect for database-driven content updates

**Installation:**
```html
<!-- In your base.html template -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

**Example: Auto-refresh latest image**
```html
<!-- web/templates/index.html -->
<div hx-get="/api/latest" 
     hx-trigger="every 10s" 
     hx-swap="innerHTML">
    Loading latest image...
</div>

<!-- Server returns just the HTML fragment, not full page -->
```

**Example: Load more images**
```html
<button hx-get="/api/images?page=2" 
        hx-target="#image-list" 
        hx-swap="beforeend">
    Load More
</button>
```

**Resources:**
- Official Docs: https://htmx.org/docs/
- Examples: https://htmx.org/examples/
- Tutorial: https://htmx.org/docs/#introduction

---

### 2. Alpine.js - Lightweight Reactivity

**When to use:**
- Interactive UI components (dropdowns, modals, tabs)
- Client-side filtering and sorting
- Simple state management
- Form validation

**Installation:**
```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

**Example: Image gallery with tabs**
```html
<div x-data="{ activeTab: 'today' }">
    <div class="tabs">
        <button @click="activeTab = 'today'" 
                :class="{ 'active': activeTab === 'today' }">
            Today
        </button>
        <button @click="activeTab = 'week'" 
                :class="{ 'active': activeTab === 'week' }">
            This Week
        </button>
    </div>
    
    <div x-show="activeTab === 'today'">
        <!-- Today's images -->
    </div>
    
    <div x-show="activeTab === 'week'">
        <!-- Week's images -->
    </div>
</div>
```

**Example: Image viewer with zoom**
```html
<div x-data="{ zoomed: false }">
    <img :class="{ 'zoomed': zoomed }" 
         @click="zoomed = !zoomed"
         src="sky_image.jpg">
</div>
```

**Resources:**
- Docs: https://alpinejs.dev/
- Playground: https://alpinejs.dev/start-here#playground

---

### 3. CSS Frameworks

#### Tailwind CSS (Recommended) ⭐

**Why Tailwind:**
- Utility-first approach
- No custom CSS needed for most cases
- Responsive by default
- Great with htmx/Alpine
- Excellent documentation

**Installation (CDN - simplest):**
```html
<script src="https://cdn.tailwindcss.com"></script>
```

**Example: ClearSky Card**
```html
<div class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
    <img class="w-full h-64 object-cover rounded-md" src="sky.jpg">
    <div class="mt-4">
        <h3 class="text-xl font-bold text-gray-800">Clear Sky</h3>
        <p class="text-gray-600">Brightness: 180 | Score: 95%</p>
    </div>
</div>
```

**Alternative: DaisyUI (Tailwind + Components)**
```html
<!-- Includes pre-built components like buttons, cards, modals -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/full.min.css" rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>

<!-- Now you can use: -->
<button class="btn btn-primary">Analyze</button>
<div class="card bg-base-100 shadow-xl">...</div>
```

---

### 4. Chart Libraries

#### Chart.js - Simple & Responsive ⭐

**Perfect for:**
- Sky brightness over time
- Color distribution pie charts
- Daily/weekly comparisons

**Installation:**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

**Example: Brightness Timeline**
```html
<canvas id="brightnessChart"></canvas>

<script>
const ctx = document.getElementById('brightnessChart');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: timestamps,  // From your API
        datasets: [{
            label: 'Sky Brightness',
            data: brightness_values,  // From your API
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Sky Brightness Over Time'
            }
        }
    }
});
</script>
```

**Integration with htmx:**
```python
# In your route
@api_bp.route('/chart-data')
def chart_data():
    records = data_manager.get_last_n_records(100)
    return jsonify({
        'timestamps': [r['timestamp'] for r in records],
        'brightness': [r['brightness_average'] for r in records]
    })
```

---

#### Plotly.js - Interactive Scientific Charts

**When to use:**
- 3D color space visualizations
- Interactive hover tooltips
- Zoom/pan functionality
- Complex multi-axis charts

**Installation:**
```html
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
```

**Example: 3D RGB Color Space**
```javascript
const trace = {
    x: red_values,
    y: green_values,
    z: blue_values,
    mode: 'markers',
    marker: {
        color: colors,
        size: 12,
    },
    type: 'scatter3d'
};

Plotly.newPlot('colorSpace', [trace]);
```

---

## 🗄️ Database & ORM

### SQLAlchemy - Python SQL Toolkit & ORM

**Why add SQLAlchemy:**
- Type-safe database operations
- Automatic schema migrations (with Alembic)
- Easier testing with mock objects
- Better query composition
- Relationship management

**Installation:**
```bash
pip install SQLAlchemy alembic
```

**Example: Define Models**
```python
# data/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SkyObservation(Base):
    __tablename__ = 'sky_observations'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    image_filename = Column(String, nullable=False)
    
    # Analysis results
    clear_sky_score = Column(Float)
    sky_condition = Column(String)
    brightness_average = Column(Float)
    brightness_condition = Column(String)
    
    # Colors
    color_red = Column(Float)
    color_green = Column(Float)
    color_blue = Column(Float)
    
    # Features
    blue_dominant = Column(Boolean)
    blue_coverage_percent = Column(Float)
    gray_coverage_percent = Column(Float)
    white_coverage_percent = Column(Float)
    
    def __repr__(self):
        return f"<SkyObservation(timestamp={self.timestamp}, score={self.clear_sky_score})>"
```

**Example: Query with ORM**
```python
# Instead of raw SQL
from data.models import SkyObservation
from sqlalchemy.orm import Session

# Get latest observation
latest = session.query(SkyObservation)\
    .order_by(SkyObservation.timestamp.desc())\
    .first()

# Get clear skies only
clear_skies = session.query(SkyObservation)\
    .filter(SkyObservation.clear_sky_score > 80)\
    .all()

# Get average brightness by date
from sqlalchemy import func
avg_by_date = session.query(
    func.date(SkyObservation.timestamp).label('date'),
    func.avg(SkyObservation.brightness_average).label('avg_brightness')
).group_by(func.date(SkyObservation.timestamp)).all()
```

---

### Alembic - Database Migrations

**Why use migrations:**
- Track database schema changes over time
- Easy rollback if something breaks
- Team collaboration on schema
- Automatic migration generation

**Setup:**
```bash
# Initialize Alembic
alembic init data/migrations

# Create migration
alembic revision --autogenerate -m "Add sky observation table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Example Migration:**
```python
# data/migrations/versions/001_add_sky_observations.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'sky_observations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('timestamp', sa.DateTime, index=True),
        sa.Column('image_filename', sa.String, nullable=False),
        sa.Column('clear_sky_score', sa.Float),
        # ... other columns
    )

def downgrade():
    op.drop_table('sky_observations')
```

---

## 🧪 Testing Framework

### pytest - Python Testing ⭐

**Installation:**
```bash
pip install pytest pytest-cov pytest-flask faker
```

**Project Test Structure:**
```
tests/
├── conftest.py              # Shared fixtures
├── test_analysis/
│   ├── test_brightness.py
│   ├── test_color.py
│   └── test_sky_features.py
├── test_data/
│   ├── test_models.py
│   ├── test_operations.py
│   └── test_manager.py
├── test_hardware/
│   └── test_poller.py
└── test_web/
    ├── test_routes.py
    └── test_api.py
```

**Example: Brightness Analysis Test**
```python
# tests/test_analysis/test_brightness.py
import pytest
from analysis.brightness import analyze_brightness
from PIL import Image

class TestBrightnessAnalysis:
    
    @pytest.fixture
    def white_image(self):
        """Create a white test image"""
        return Image.new('RGB', (100, 100), (255, 255, 255))
    
    @pytest.fixture
    def black_image(self):
        """Create a black test image"""
        return Image.new('RGB', (100, 100), (0, 0, 0))
    
    def test_very_bright_image(self, white_image):
        result = analyze_brightness(white_image)
        assert result['brightness_average'] > 200
        assert result['brightness_condition'] == 'Very Bright'
    
    def test_dark_image(self, black_image):
        result = analyze_brightness(black_image)
        assert result['brightness_average'] < 50
        assert result['brightness_condition'] == 'Dark'
    
    def test_returns_correct_keys(self, white_image):
        result = analyze_brightness(white_image)
        assert 'brightness_average' in result
        assert 'brightness_condition' in result
```

**Example: API Testing**
```python
# tests/test_web/test_api.py
import pytest
from web.app import create_flask_app

@pytest.fixture
def client():
    app = create_flask_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_latest_returns_json(client):
    response = client.get('/api/latest')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.get_json()
    assert 'timestamp' in data
    assert 'clear_sky_score' in data

def test_api_latest_with_no_data(client, monkeypatch):
    # Mock empty database
    def mock_get_latest():
        return None
    
    monkeypatch.setattr('data.manager.data_manager.get_latest', mock_get_latest)
    
    response = client.get('/api/latest')
    assert response.status_code == 404
```

**Running Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_analysis/test_brightness.py

# Run specific test
pytest tests/test_analysis/test_brightness.py::test_very_bright_image

# Run with verbose output
pytest -v

# Run and show print statements
pytest -s
```

---

## 🔍 Code Quality Tools

### Black - Code Formatter ⭐

**Why Black:**
- Consistent code style across project
- No configuration needed
- Fast and reliable
- PEP 8 compliant

**Installation & Usage:**
```bash
pip install black

# Format all files
black .

# Check without modifying
black --check .

# Format specific file
black web/routes/api_routes.py
```

**pyproject.toml Configuration:**
```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
```

---

### Flake8 - Linting

**Installation:**
```bash
pip install flake8
```

**Usage:**
```bash
# Check all files
flake8

# Specific directory
flake8 web/

# With output to file
flake8 > flake8_report.txt
```

**Setup (.flake8):**
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    build,
    dist
```

---

### mypy - Type Checking

**Why type hints:**
- Catch bugs before runtime
- Better IDE autocomplete
- Self-documenting code
- Easier refactoring

**Installation:**
```bash
pip install mypy
```

**Example with Type Hints:**
```python
# analysis/brightness.py
from PIL import Image
from typing import Dict, Any

def analyze_brightness(image: Image.Image) -> Dict[str, Any]:
    """Analyze image brightness.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary with brightness metrics
    """
    brightness_avg: float = calculate_brightness(image)
    condition: str = get_brightness_condition(brightness_avg)
    
    return {
        'brightness_average': brightness_avg,
        'brightness_condition': condition
    }
```

**Run mypy:**
```bash
# Check all files
mypy .

# Specific module
mypy analysis/

# With configuration
mypy --config-file mypy.ini
```

---

## 🤖 Machine Learning (Future)

### 1. scikit-learn - Traditional ML

**Use cases for ClearSky:**
- Sky condition classification (clear, cloudy, partly cloudy)
- Weather prediction based on sky patterns
- Anomaly detection (unusual sky conditions)
- Clustering similar sky conditions

**Installation:**
```bash
pip install scikit-learn
```

**Example: Sky Condition Classifier**
```python
# analysis/ml/training/train_classifier.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load training data
X, y = load_sky_features_and_labels()

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Evaluate
accuracy = clf.score(X_test, y_test)
print(f"Accuracy: {accuracy:.2f}")

# Save model
joblib.dump(clf, 'analysis/ml/models/sky_classifier.joblib')
```

**Example: Using Trained Model**
```python
# analysis/ml/inference.py
import joblib
from typing import Dict, Any

class SkyClassifier:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)
    
    def predict(self, features: Dict[str, float]) -> str:
        """Predict sky condition from features"""
        # Extract features in correct order
        X = [[
            features['brightness_average'],
            features['blue_coverage_percent'],
            features['color_red'],
            features['color_green'],
            features['color_blue']
        ]]
        
        prediction = self.model.predict(X)[0]
        return prediction  # "clear", "cloudy", "partly_cloudy"
```

---

### 2. TensorFlow Lite - Efficient Inference

**Why TFLite:**
- Small model size
- Fast inference
- Can run on ESP32 (future)
- Cross-platform

**Example: Convert model to TFLite**
```python
import tensorflow as tf

# Load your trained model
model = tf.keras.models.load_model('sky_model.h5')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save
with open('sky_model.tflite', 'wb') as f:
    f.write(tflite_model)
```

---

### 3. OpenCV - Advanced Image Processing

**Installation:**
```bash
pip install opencv-python
```

**Example: Cloud Detection**
```python
import cv2
import numpy as np

def detect_clouds(image_path: str) -> Dict[str, Any]:
    """Detect clouds in sky image using OpenCV"""
    # Read image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to detect clouds (bright regions)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Find contours (cloud regions)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    # Calculate cloud coverage
    total_area = img.shape[0] * img.shape[1]
    cloud_area = sum(cv2.contourArea(c) for c in contours)
    cloud_coverage = (cloud_area / total_area) * 100
    
    return {
        'cloud_coverage_percent': cloud_coverage,
        'num_cloud_regions': len(contours),
        'has_clouds': cloud_coverage > 10
    }
```

---

## 🔧 ESP32 Development

### 1. PlatformIO - Modern C++ IDE ⭐

**Why PlatformIO over Arduino IDE:**
- Better code editor (VS Code integration)
- Proper library management
- Built-in testing framework
- Multiple board support
- Debugging support
- Command-line interface

**Installation:**
```bash
# Install VS Code first, then:
# Install PlatformIO extension from VS Code marketplace

# Or via command line:
pip install platformio
```

**Project Structure:**
```
clearsky-firmware/
├── platformio.ini          # Project configuration
├── src/
│   └── main.cpp           # Main code
├── include/               # Header files
├── lib/                   # Project libraries
└── test/                  # Unit tests
```

**platformio.ini Example:**
```ini
[env:esp32cam]
platform = espressif32
board = esp32cam
framework = arduino

# Upload settings
upload_speed = 921600
monitor_speed = 115200

# Libraries
lib_deps = 
    esp32-camera
    ArduinoJson

# Build flags
build_flags = 
    -DCORE_DEBUG_LEVEL=3
```

**Example: Modular ESP32 Code**
```cpp
// src/camera/camera_init.h
#ifndef CAMERA_INIT_H
#define CAMERA_INIT_H

#include "esp_camera.h"

bool initCamera();
camera_fb_t* captureImage();
void releaseImage(camera_fb_t* fb);

#endif

// src/camera/camera_init.cpp
#include "camera_init.h"

bool initCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    // ... more configuration
    
    esp_err_t err = esp_camera_init(&config);
    return (err == ESP_OK);
}

camera_fb_t* captureImage() {
    return esp_camera_fb_get();
}

void releaseImage(camera_fb_t* fb) {
    esp_camera_fb_return(fb);
}
```

---

### 2. ESP-IDF - Official Framework

**When to use:**
- Need low-level control
- Custom hardware peripherals
- Real-time requirements
- Production deployment

**Resources:**
- ESP-IDF Docs: https://docs.espressif.com/projects/esp-idf/
- Getting Started: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/

---

### 3. Unit Testing for C++

**GoogleTest with PlatformIO:**

```cpp
// test/test_camera.cpp
#include <unity.h>
#include "camera_init.h"

void setUp(void) {
    // Setup before each test
}

void tearDown(void) {
    // Cleanup after each test
}

void test_camera_initialization() {
    bool result = initCamera();
    TEST_ASSERT_TRUE(result);
}

void test_camera_capture() {
    camera_fb_t* fb = captureImage();
    TEST_ASSERT_NOT_NULL(fb);
    TEST_ASSERT_GREATER_THAN(0, fb->len);
    releaseImage(fb);
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_camera_initialization);
    RUN_TEST(test_camera_capture);
    return UNITY_END();
}
```

**Run tests:**
```bash
pio test
```

---

## 📊 Monitoring & DevOps

### 1. Docker - Containerization

**Dockerfile Example:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p images logs backups

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "main.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  clearsky:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./images:/app/images
      - ./clearsky.db:/app/clearsky.db
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - ESP32_IP=192.168.1.104
    restart: unless-stopped
```

---

### 2. GitHub Actions - CI/CD

**.github/workflows/test.yml:**
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

## 🎓 Learning Path

### Week 1-2: Frontend
1. Complete htmx tutorial (2 hours)
2. Learn Alpine.js basics (2 hours)
3. Build a simple image gallery with htmx + Alpine (4 hours)
4. Style with Tailwind CSS (2 hours)

### Week 3-4: Testing
1. pytest documentation (3 hours)
2. Write tests for existing code (5 hours)
3. Set up CI/CD (2 hours)

### Week 5-6: Database
1. SQLAlchemy tutorial (4 hours)
2. Migrate to ORM (6 hours)
3. Set up Alembic (2 hours)

### Week 7-8: ESP32
1. PlatformIO basics (3 hours)
2. Migrate Arduino code (5 hours)
3. Add unit tests (4 hours)

### Month 3: Machine Learning
1. scikit-learn basics (8 hours)
2. Collect training data (ongoing)
3. Train first model (4 hours)
4. Deploy model (4 hours)

---

## 📚 Essential Resources

### Documentation
- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **htmx**: https://htmx.org/docs/
- **Tailwind**: https://tailwindcss.com/docs
- **pytest**: https://docs.pytest.org/
- **PlatformIO**: https://docs.platformio.org/

### Tutorials
- **Real Python**: https://realpython.com/ (Flask, SQLAlchemy, testing)
- **Corey Schafer YouTube**: Flask tutorials
- **htmx examples**: https://htmx.org/examples/
- **Random Nerd Tutorials**: ESP32 projects

### Books
- **Flask Web Development** by Miguel Grinberg
- **Test-Driven Development with Python** by Harry Percival
- **Python Machine Learning** by Sebastian Raschka

---

Ready to supercharge your ClearSky development! 🚀

"""
Configuration file for Sky Predictor Server

All settings are centralized here for easy customization.
"""

# ===== SERVER SETTINGS =====
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000       # Server port
DEBUG = False     # Set to True for development

# ===== IMAGE STORAGE =====
SAVE_IMAGES = True                    # Save received images to disk
IMAGE_DIR = "captured_images"         # Directory for saved images
IMAGE_FORMAT = "jpg"                  # Image file format
IMAGE_NAME_FORMAT = "sky_{timestamp}.{format}"  # Filename pattern

# ===== DATA STORAGE =====
SAVE_ANALYSIS_DATA = True             # Save analysis results
DATA_FILE = "analysis_data.json"      # JSON file for analysis history
MAX_HISTORY_ENTRIES = 100             # Maximum entries to keep in memory
MAX_HISTORY_SAVED = 50                # Maximum entries to save to file

# ===== ANALYSIS SETTINGS =====

# Brightness Analysis Thresholds (0-255)
BRIGHTNESS_VERY_BRIGHT = 180          # Clear/sunny threshold
BRIGHTNESS_BRIGHT = 140               # Partly cloudy threshold
BRIGHTNESS_MODERATE = 100             # Cloudy threshold
BRIGHTNESS_DIM = 60                   # Overcast threshold

# Color Analysis Parameters
COLOR_BLUE_DOMINANCE_RED_DIFF = 20    # Blue must be this much higher than red
COLOR_BLUE_DOMINANCE_GREEN_DIFF = 10  # Blue must be this much higher than green
COLOR_GRAY_VARIANCE_THRESHOLD = 30    # Max variance for gray detection

# Sky Features Analysis
SKY_SAMPLE_RATE = 50                  # Sample every Nth pixel (lower = more accurate, slower)
SKY_BLUE_MIN_VALUE = 150              # Minimum blue value for "blue sky"
SKY_BLUE_RED_DIFF = 30                # Blue > red by this much
SKY_BLUE_GREEN_DIFF = 20              # Blue > green by this much
SKY_WHITE_BRIGHTNESS_MIN = 200        # Minimum brightness for "white"
SKY_WHITE_VARIANCE_MAX = 40           # Max color variance for "white"

# Coverage Thresholds (percentages)
COVERAGE_MOSTLY_CLEAR = 60            # % blue for "mostly clear"
COVERAGE_MOSTLY_CLOUDY = 60           # % gray for "mostly cloudy"
COVERAGE_PARTLY_CLOUDY = 40           # % white for "partly cloudy"

# ===== WEB UI SETTINGS =====
AUTO_REFRESH_INTERVAL = 5000          # Milliseconds between auto-refresh
SHOW_DETAILED_STATS = True            # Show detailed color analysis
SHOW_COVERAGE_STATS = True            # Show sky coverage percentages

# ===== LOGGING =====
ENABLE_LOGGING = True                 # Enable console logging
LOG_FILE = "server.log"               # Log file (None = console only)
LOG_LEVEL = "INFO"                    # DEBUG, INFO, WARNING, ERROR

# ===== ADVANCED SETTINGS =====
ENABLE_CORS = False                   # Enable CORS for API access
MAX_IMAGE_SIZE_MB = 10                # Maximum image size to accept
ENABLE_IMAGE_COMPRESSION = False      # Re-compress received images
COMPRESSION_QUALITY = 85              # JPEG quality if compression enabled

# ===== FEATURE FLAGS =====
ENABLE_BRIGHTNESS_ANALYSIS = True     # Brightness-based analysis
ENABLE_COLOR_ANALYSIS = True          # Color-based analysis
ENABLE_SKY_FEATURES = True            # Detailed sky feature detection
ENABLE_HISTORICAL_CHARTS = False      # Generate charts (requires matplotlib)
ENABLE_NOTIFICATIONS = False          # Email/SMS notifications (requires setup)

# ===== NOTIFICATION SETTINGS (if enabled) =====
NOTIFY_ON_CLEAR_SKY = True            # Send notification when sky is clear
CLEAR_SKY_THRESHOLD = 70              # Minimum score to trigger notification
NOTIFICATION_COOLDOWN = 3600          # Seconds between notifications

# Email settings (if notifications enabled)
EMAIL_ENABLED = False
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_FROM = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
EMAIL_TO = "recipient@example.com"

# ===== PRESETS =====
# Uncomment one to use a preset configuration

# PRESET: Fast & Lightweight
# USE_PRESET_FAST = True
try:
    if USE_PRESET_FAST:
        ENABLE_COLOR_ANALYSIS = True
        ENABLE_SKY_FEATURES = False
        SKY_SAMPLE_RATE = 100
        MAX_HISTORY_ENTRIES = 20
        SHOW_DETAILED_STATS = False
except NameError:
    pass

# PRESET: Detailed Analysis
# USE_PRESET_DETAILED = True
try:
    if USE_PRESET_DETAILED:
        ENABLE_COLOR_ANALYSIS = True
        ENABLE_SKY_FEATURES = True
        SKY_SAMPLE_RATE = 25
        MAX_HISTORY_ENTRIES = 200
        SHOW_DETAILED_STATS = True
        SHOW_COVERAGE_STATS = True
except NameError:
    pass

# PRESET: Development/Testing
# USE_PRESET_DEV = True
try:
    if USE_PRESET_DEV:
        DEBUG = True
        SAVE_IMAGES = True
        AUTO_REFRESH_INTERVAL = 3000
        ENABLE_LOGGING = True
        LOG_LEVEL = "DEBUG"
except NameError:
    pass

# ===== VALIDATION =====
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not 1024 <= PORT <= 65535:
        errors.append(f"Invalid PORT: {PORT} (must be 1024-65535)")
    
    if MAX_IMAGE_SIZE_MB < 1:
        errors.append("MAX_IMAGE_SIZE_MB must be at least 1")
    
    if not 0 <= BRIGHTNESS_DIM < BRIGHTNESS_MODERATE < BRIGHTNESS_BRIGHT < BRIGHTNESS_VERY_BRIGHT <= 255:
        errors.append("Brightness thresholds must be in ascending order (0-255)")
    
    if SKY_SAMPLE_RATE < 1:
        errors.append("SKY_SAMPLE_RATE must be at least 1")
    
    if CLEAR_SKY_THRESHOLD < 0 or CLEAR_SKY_THRESHOLD > 100:
        errors.append("CLEAR_SKY_THRESHOLD must be 0-100")
    
    return errors

# Run validation on import
_validation_errors = validate_config()
if _validation_errors:
    print("⚠️  Configuration errors found:")
    for error in _validation_errors:
        print(f"   - {error}")
    print()

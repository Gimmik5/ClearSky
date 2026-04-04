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
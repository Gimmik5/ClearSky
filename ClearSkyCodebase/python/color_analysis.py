"""
Color Analysis Module
Analyzes color characteristics for sky detection
"""

import numpy as np
from python_config import (
    COLOR_BLUE_DOMINANCE_RED_DIFF, COLOR_BLUE_DOMINANCE_GREEN_DIFF,
    COLOR_GRAY_VARIANCE_THRESHOLD
)


def analyze_color(image):
    """
    Analyze color characteristics for sky detection
    
    Args:
        image: OpenCV image (BGR format)
    
    Returns:
        dict: Color analysis results including RGB values and sky condition
    """
    # Calculate average color
    avg_color = np.mean(image, axis=(0, 1))
    b, g, r = avg_color  # OpenCV uses BGR
    
    brightness = calculate_color_brightness(r, g, b)
    
    # Check for blue dominance (clear sky indicator)
    blue_dominant = is_blue_dominant(r, g, b)
    
    # Check for gray (clouds)
    color_variance = calculate_color_variance(r, g, b)
    is_gray = bool(color_variance < COLOR_GRAY_VARIANCE_THRESHOLD)  # Convert to Python bool
    
    # Determine sky condition and score
    condition, blue_score = determine_sky_condition(
        blue_dominant, is_gray, brightness
    )
    
    return {
        "red": float(round(r, 2)),
        "green": float(round(g, 2)),
        "blue": float(round(b, 2)),
        "brightness": float(round(brightness, 2)),
        "color_variance": float(round(color_variance, 2)),
        "blue_dominant": blue_dominant,
        "is_gray": is_gray,
        "condition": condition,
        "blue_sky_score": int(blue_score)
    }


def calculate_color_brightness(r, g, b):
    """
    Calculate brightness from RGB values
    
    Args:
        r, g, b: Red, green, blue values
    
    Returns:
        float: Average brightness
    """
    return (r + g + b) / 3


def is_blue_dominant(r, g, b):
    """
    Check if blue is the dominant color
    
    Args:
        r, g, b: Red, green, blue values
    
    Returns:
        bool: True if blue is dominant
    """
    # Convert to Python bool to avoid numpy bool serialization issues
    return bool((b > r + COLOR_BLUE_DOMINANCE_RED_DIFF) and \
                (b > g + COLOR_BLUE_DOMINANCE_GREEN_DIFF))


def calculate_color_variance(r, g, b):
    """
    Calculate variance between color channels
    
    Args:
        r, g, b: Red, green, blue values
    
    Returns:
        float: Total color variance
    """
    return abs(r - g) + abs(g - b) + abs(b - r)


def determine_sky_condition(blue_dominant, is_gray, brightness):
    """
    Determine sky condition based on color analysis
    
    Args:
        blue_dominant: Whether blue is dominant color
        is_gray: Whether colors are gray/neutral
        brightness: Overall brightness value
    
    Returns:
        tuple: (condition_string, blue_sky_score)
    """
    if blue_dominant and brightness > 100:
        return "☀️ CLEAR BLUE SKY", int((brightness / 255) * 100)
    
    elif is_gray and brightness > 150:
        return "🌫️ BRIGHT OVERCAST", int((brightness / 255) * 50)
    
    elif is_gray and brightness > 100:
        return "☁️ CLOUDY", int((brightness / 255) * 30)
    
    elif is_gray and brightness > 50:
        return "⛈️ DARK CLOUDS", 10
    
    elif brightness < 50:
        return "🌙 NIGHT", 0
    
    else:
        return "🌤️ MIXED", int((brightness / 255) * 40)

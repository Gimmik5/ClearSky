"""
Brightness Analysis Module
Analyzes overall image brightness levels
"""

import cv2
import numpy as np
from python_config import (
    BRIGHTNESS_VERY_BRIGHT, BRIGHTNESS_BRIGHT,
    BRIGHTNESS_MODERATE, BRIGHTNESS_DIM
)


def analyze_brightness(image):
    """
    Analyze overall image brightness
    
    Args:
        image: OpenCV image (BGR format)
    
    Returns:
        dict: {
            'average': float,
            'condition': str,
            'score': int
        }
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    
    # Classify brightness using config thresholds
    condition = classify_brightness(avg_brightness)
    
    # Calculate score (0-100%)
    score = calculate_brightness_score(avg_brightness)
    
    return {
        "average": float(round(avg_brightness, 2)),
        "condition": condition,
        "score": score  # Already int from calculate_brightness_score
    }


def classify_brightness(brightness_value):
    """
    Classify brightness level into descriptive category
    
    Args:
        brightness_value: Average brightness (0-255)
    
    Returns:
        str: Brightness condition description
    """
    if brightness_value > BRIGHTNESS_VERY_BRIGHT:
        return "☀️ VERY BRIGHT - Clear/sunny"
    elif brightness_value > BRIGHTNESS_BRIGHT:
        return "🌤️ BRIGHT - Partly cloudy"
    elif brightness_value > BRIGHTNESS_MODERATE:
        return "⛅ MODERATE - Cloudy"
    elif brightness_value > BRIGHTNESS_DIM:
        return "☁️ DIM - Overcast"
    else:
        return "🌙 DARK - Night/storm"


def calculate_brightness_score(brightness_value):
    """
    Convert brightness to 0-100 score
    
    Args:
        brightness_value: Average brightness (0-255)
    
    Returns:
        int: Score from 0-100
    """
    return int((brightness_value / 255) * 100)

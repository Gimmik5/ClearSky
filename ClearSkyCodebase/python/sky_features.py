"""
Sky Features Analysis Module
Detailed sky feature detection and coverage analysis
"""

from python_config import (
    SKY_SAMPLE_RATE, SKY_BLUE_MIN_VALUE, SKY_BLUE_RED_DIFF, SKY_BLUE_GREEN_DIFF,
    SKY_WHITE_BRIGHTNESS_MIN, SKY_WHITE_VARIANCE_MAX, COLOR_GRAY_VARIANCE_THRESHOLD,
    COVERAGE_MOSTLY_CLEAR, COVERAGE_MOSTLY_CLOUDY, COVERAGE_PARTLY_CLOUDY
)


def analyze_sky_features(image):
    """
    Detailed sky feature analysis - counts pixels of different types
    
    Args:
        image: OpenCV image (BGR format)
    
    Returns:
        dict: Sky coverage percentages and overall assessment
    """
    height, width = image.shape[:2]
    
    # Count pixels by type
    pixel_counts = count_sky_pixels(image, height, width)
    
    # Calculate percentages
    percentages = calculate_coverage_percentages(pixel_counts)
    
    # Overall assessment
    assessment = assess_sky_coverage(percentages)
    
    return {
        "blue_coverage": float(round(percentages['blue'], 1)),
        "gray_coverage": float(round(percentages['gray'], 1)),
        "white_coverage": float(round(percentages['white'], 1)),
        "assessment": assessment,
        "pixels_sampled": int(pixel_counts['total'])
    }


def count_sky_pixels(image, height, width):
    """
    Count pixels of different sky types
    
    Args:
        image: OpenCV image
        height, width: Image dimensions
    
    Returns:
        dict: Pixel counts by type
    """
    blue_pixels = 0
    gray_pixels = 0
    white_pixels = 0
    total_sampled = 0
    
    # Sample pixels using config sample rate
    for y in range(0, height, SKY_SAMPLE_RATE):
        for x in range(0, width, SKY_SAMPLE_RATE):
            b, g, r = image[y, x]
            pixel_type = classify_pixel(r, g, b)
            
            if pixel_type == 'blue':
                blue_pixels += 1
            elif pixel_type == 'white':
                white_pixels += 1
            elif pixel_type == 'gray':
                gray_pixels += 1
            
            total_sampled += 1
    
    return {
        'blue': blue_pixels,
        'gray': gray_pixels,
        'white': white_pixels,
        'total': total_sampled
    }


def classify_pixel(r, g, b):
    """
    Classify a single pixel as blue sky, white, gray, or other
    
    Args:
        r, g, b: Red, green, blue values
    
    Returns:
        str: 'blue', 'white', 'gray', or 'other'
    """
    brightness = (int(r) + int(g) + int(b)) / 3
    color_var = abs(int(r) - int(g)) + abs(int(g) - int(b)) + abs(int(b) - int(r))
    
    # Check for blue sky
    if (b > SKY_BLUE_MIN_VALUE and 
        b > r + SKY_BLUE_RED_DIFF and 
        b > g + SKY_BLUE_GREEN_DIFF):
        return 'blue'
    
    # Check for white/bright
    elif brightness > SKY_WHITE_BRIGHTNESS_MIN and color_var < SKY_WHITE_VARIANCE_MAX:
        return 'white'
    
    # Check for gray
    elif color_var < COLOR_GRAY_VARIANCE_THRESHOLD:
        return 'gray'
    
    else:
        return 'other'


def calculate_coverage_percentages(pixel_counts):
    """
    Calculate coverage percentages from pixel counts
    
    Args:
        pixel_counts: Dict with pixel counts
    
    Returns:
        dict: Coverage percentages
    """
    total = pixel_counts['total']
    
    if total == 0:
        return {'blue': 0, 'gray': 0, 'white': 0}
    
    return {
        'blue': (pixel_counts['blue'] / total) * 100,
        'gray': (pixel_counts['gray'] / total) * 100,
        'white': (pixel_counts['white'] / total) * 100
    }


def assess_sky_coverage(percentages):
    """
    Assess overall sky condition based on coverage percentages
    
    Args:
        percentages: Dict with coverage percentages
    
    Returns:
        str: Overall assessment
    """
    if percentages['blue'] > COVERAGE_MOSTLY_CLEAR:
        return "☀️ Mostly clear"
    elif percentages['gray'] > COVERAGE_MOSTLY_CLOUDY:
        return "☁️ Mostly cloudy"
    elif percentages['white'] > COVERAGE_PARTLY_CLOUDY:
        return "🌥️ Partly cloudy"
    else:
        return "🌤️ Mixed"

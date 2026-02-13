"""
Analysis Core Module
Orchestrates all image analysis functions
"""

from python_config import (
    ENABLE_BRIGHTNESS_ANALYSIS, ENABLE_COLOR_ANALYSIS, ENABLE_SKY_FEATURES
)
from brightness_analysis import analyze_brightness
from color_analysis import analyze_color
from sky_features import analyze_sky_features


def analyze_image(image):
    """
    Perform full analysis on an image
    
    Args:
        image: OpenCV image (BGR format)
    
    Returns:
        dict: Complete analysis results
    """
    results = {}
    
    # Brightness analysis
    if ENABLE_BRIGHTNESS_ANALYSIS:
        results["brightness"] = analyze_brightness(image)
    
    # Color analysis
    if ENABLE_COLOR_ANALYSIS:
        results["color"] = analyze_color(image)
    
    # Sky features
    if ENABLE_SKY_FEATURES:
        results["features"] = analyze_sky_features(image)
    
    # Calculate overall score
    if ENABLE_BRIGHTNESS_ANALYSIS and ENABLE_COLOR_ANALYSIS:
        features = results.get("features")
        results["clear_sky_score"] = calculate_clear_sky_score(
            results["brightness"],
            results["color"],
            features
        )
        results["sky_condition"] = results["color"]["condition"]
    
    return results


def calculate_clear_sky_score(brightness_result, color_result, features_result=None):
    """
    Calculate overall clear sky score from analysis results
    
    Args:
        brightness_result: Result from analyze_brightness()
        color_result: Result from analyze_color()
        features_result: Optional result from analyze_sky_features()
    
    Returns:
        int: Clear sky score (0-100)
    """
    # Base score from brightness and color
    score = (brightness_result["score"] + color_result["blue_sky_score"]) / 2
    
    # Adjust based on features if available
    if features_result:
        score = adjust_score_by_features(score, features_result)
    
    # Ensure score is within 0-100
    return int(max(0, min(100, score)))


def adjust_score_by_features(base_score, features_result):
    """
    Adjust score based on sky feature analysis
    
    Args:
        base_score: Base clear sky score
        features_result: Sky features analysis result
    
    Returns:
        float: Adjusted score
    """
    # Boost score if lots of blue sky
    if features_result["blue_coverage"] > 60:
        return base_score * 1.1
    
    # Reduce score if lots of gray
    elif features_result["gray_coverage"] > 60:
        return base_score * 0.8
    
    return base_score


def get_analysis_summary(results):
    """
    Generate a text summary of analysis results
    
    Args:
        results: Dict from analyze_image()
    
    Returns:
        str: Human-readable summary
    """
    lines = []
    
    if "brightness" in results:
        lines.append(format_brightness_summary(results["brightness"]))
    
    if "color" in results:
        lines.append(format_color_summary(results["color"]))
    
    if "features" in results:
        lines.append(format_features_summary(results["features"]))
    
    if "clear_sky_score" in results:
        lines.append(f"Clear Sky Score: {results['clear_sky_score']}%")
    
    return "\n".join(lines)


def format_brightness_summary(brightness_result):
    """Format brightness results for summary"""
    b = brightness_result
    return f"Brightness: {b['average']:.1f} ({b['condition']})"


def format_color_summary(color_result):
    """Format color results for summary"""
    c = color_result
    rgb = f"R={c['red']:.1f}, G={c['green']:.1f}, B={c['blue']:.1f}"
    return f"Color: {c['condition']}\nRGB: {rgb}"


def format_features_summary(features_result):
    """Format sky features results for summary"""
    f = features_result
    coverage = f"Blue {f['blue_coverage']:.1f}%, Gray {f['gray_coverage']:.1f}%, White {f['white_coverage']:.1f}%"
    return f"Sky Coverage: {coverage}\nAssessment: {f['assessment']}"

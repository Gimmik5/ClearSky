"""
Image Storage Module
Handles saving and loading of captured images
"""

import os
import cv2
from datetime import datetime
from python_config import (
    SAVE_IMAGES, IMAGE_DIR, IMAGE_NAME_FORMAT, IMAGE_FORMAT,
    ENABLE_IMAGE_COMPRESSION, COMPRESSION_QUALITY
)


def save_image(image, timestamp=None):
    """
    Save image to disk
    
    Args:
        image: OpenCV image
        timestamp: Optional timestamp string
    
    Returns:
        str: Path to saved image, or None if saving disabled
    """
    if not SAVE_IMAGES:
        return None
    
    ensure_image_directory()
    
    if timestamp is None:
        timestamp = generate_timestamp()
    
    filepath = generate_image_path(timestamp)
    
    return write_image_to_disk(image, filepath)


def ensure_image_directory():
    """Create image directory if it doesn't exist"""
    if not os.path.exists(IMAGE_DIR):
        try:
            os.makedirs(IMAGE_DIR)
            print(f"✓ Created image directory: {IMAGE_DIR}")
        except Exception as e:
            print(f"Error creating image directory: {e}")


def generate_timestamp():
    """
    Generate timestamp string
    
    Returns:
        str: Timestamp in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_image_path(timestamp):
    """
    Generate full path for image file
    
    Args:
        timestamp: Timestamp string
    
    Returns:
        str: Full file path
    """
    filename = IMAGE_NAME_FORMAT.format(
        timestamp=timestamp,
        format=IMAGE_FORMAT
    )
    return os.path.join(IMAGE_DIR, filename)


def write_image_to_disk(image, filepath):
    """
    Write image to disk with optional compression
    
    Args:
        image: OpenCV image
        filepath: Destination file path
    
    Returns:
        str: Filepath if successful, None otherwise
    """
    try:
        if ENABLE_IMAGE_COMPRESSION:
            cv2.imwrite(filepath, image, [cv2.IMWRITE_JPEG_QUALITY, COMPRESSION_QUALITY])
        else:
            cv2.imwrite(filepath, image)
        
        return filepath
    
    except Exception as e:
        print(f"Error saving image: {e}")
        return None


def load_image(filepath):
    """
    Load image from disk
    
    Args:
        filepath: Path to image file
    
    Returns:
        OpenCV image or None if error
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        return cv2.imread(filepath)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def delete_old_images(keep_count=100):
    """
    Delete old images, keeping only the most recent
    
    Args:
        keep_count: Number of images to keep
    """
    if not SAVE_IMAGES or not os.path.exists(IMAGE_DIR):
        return
    
    try:
        # Get all image files
        files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        # Sort by modification time
        files.sort(key=lambda x: os.path.getmtime(os.path.join(IMAGE_DIR, x)))
        
        # Delete old files
        for file in files[:-keep_count]:
            os.remove(os.path.join(IMAGE_DIR, file))
        
        if len(files) > keep_count:
            print(f"✓ Deleted {len(files) - keep_count} old images")
    
    except Exception as e:
        print(f"Error deleting old images: {e}")

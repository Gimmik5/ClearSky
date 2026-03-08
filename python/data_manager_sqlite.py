"""
Data Manager Module - SQLite Version - FIXED
Properly formats timestamps for web interface compatibility

FIXES:
- Converts database timestamps to YYYYMMDD_HHMMSS format
- Ensures web code can properly separate by days
- Maintains backward compatibility
"""

from datetime import datetime
import os
from database_schema import create_database
from database_operations import (
    insert_capture, insert_sky_analysis, mark_analysis_complete,
    get_latest_capture_with_analysis, get_recent_captures_with_analysis,
    get_statistics, get_daily_statistics, export_to_csv,
    get_capture_count
)


def format_timestamp_for_web(timestamp):
    """
    Convert database timestamp to web-compatible format
    
    Args:
        timestamp: Can be datetime object, ISO string, or YYYYMMDD_HHMMSS string
    
    Returns:
        str: Timestamp in YYYYMMDD_HHMMSS format
    """
    if timestamp is None:
        return None
    
    # If already in correct format, return as-is
    if isinstance(timestamp, str):
        # Check if already in YYYYMMDD_HHMMSS format
        if len(timestamp) == 15 and '_' in timestamp and timestamp[:8].isdigit():
            return timestamp
        
        # Handle NORTS timestamps
        if timestamp.startswith('NORTS_'):
            return timestamp
        
        # Try to parse ISO format from database
        try:
            # SQLite returns: "2026-03-04 14:30:22"
            dt = datetime.fromisoformat(timestamp.replace(' ', 'T'))
            return dt.strftime('%Y%m%d_%H%M%S')
        except:
            pass
        
        # Try other formats
        try:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y%m%d_%H%M%S')
        except:
            pass
    
    # If datetime object
    if isinstance(timestamp, datetime):
        return timestamp.strftime('%Y%m%d_%H%M%S')
    
    # Fallback: return as string
    return str(timestamp)


class DataManager:
    """
    Manages all data storage and retrieval
    
    FIXED: Properly formats timestamps for web interface
    """
    
    def __init__(self):
        """Initialize data manager and ensure database exists"""
        create_database()
        print("✓ Data Manager initialized (SQLite backend)")
    
    
    def update_latest(self, timestamp, image_path, analysis_results):
        """
        Store a new capture and its analysis results
        
        Args:
            timestamp (str): Timestamp string (will be converted to datetime)
            image_path (str): Full path to saved image
            analysis_results (dict): Results from analysis_core.analyze_image()
        """
        # Convert timestamp string to datetime if needed
        if isinstance(timestamp, str):
            # Handle NORTS (No Real Time Sync) fallback timestamps
            if timestamp.startswith("NORTS_"):
                try:
                    millis = int(timestamp.replace("NORTS_", ""))
                    timestamp_dt = datetime.now()
                    print(f"[DataManager] ⚠ NORTS timestamp detected ({millis}ms since boot) - using current time")
                except ValueError:
                    timestamp_dt = datetime.now()
                    print("[DataManager] ⚠ Invalid NORTS timestamp - using current time")
            else:
                # Normal timestamp format: YYYYMMDD_HHMMSS
                try:
                    timestamp_dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                except ValueError:
                    timestamp_dt = datetime.now()
                    print(f"[DataManager] ⚠ Invalid timestamp format '{timestamp}' - using current time")
        else:
            timestamp_dt = timestamp
        
        # Get image filename
        image_filename = os.path.basename(image_path)
        
        # Get image size if file exists
        image_size = None
        if os.path.exists(image_path):
            image_size = os.path.getsize(image_path)
        
        # Insert capture record
        capture_id = insert_capture(
            timestamp=timestamp_dt,
            image_path=image_path,
            image_filename=image_filename,
            image_size_bytes=image_size
        )
        
        # Insert analysis results
        insert_sky_analysis(capture_id, analysis_results)
        
        # Mark analysis as complete
        mark_analysis_complete(capture_id)
        
        return capture_id
    
    
    def add_to_history(self, timestamp, image_path, analysis_results):
        """
        Add to history (same as update_latest for database version)
        Kept for backward compatibility
        """
        return self.update_latest(timestamp, image_path, analysis_results)
    
    
    def get_latest(self):
        """
        Get the latest capture with analysis
        
        Returns:
            dict: Latest capture data with analysis, or None
        """
        result = get_latest_capture_with_analysis()
        
        if not result:
            return {
                "timestamp": None,
                "image_path": None,
                "analysis": {}
            }
        
        # FIXED: Format timestamp for web compatibility
        formatted_timestamp = format_timestamp_for_web(result.get('timestamp'))
        
        # Format for compatibility with old interface
        return {
            "timestamp": formatted_timestamp,
            "image_path": result.get('image_path'),
            "analysis": {
                "clear_sky_score": result.get('clear_sky_score'),
                "summary": result.get('sky_condition'),
                "sky_condition": result.get('sky_condition'),  # Add this too
                "brightness": {
                    "average": result.get('brightness_average'),
                    "score": result.get('brightness_score')
                },
                "sky_features": {
                    "blue_coverage": result.get('blue_coverage_percent'),
                    "gray_coverage": result.get('gray_coverage_percent')
                },
                "from_sd": result.get('from_sd', False)
            }
        }
    
    
    def get_history(self, limit=None):
        """
        Get recent captures with analysis
        
        FIXED: Properly formats timestamps for web interface
        
        Args:
            limit (int): Maximum number of records (default 100)
        
        Returns:
            list: List of capture records with formatted timestamps
        """
        if limit is None:
            limit = 100
        
        results = get_recent_captures_with_analysis(limit)
        
        # Format for compatibility
        history = []
        for row in results:
            # FIXED: Convert database timestamp to web-compatible format
            db_timestamp = row.get('timestamp')
            formatted_timestamp = format_timestamp_for_web(db_timestamp)
            
            history.append({
                "timestamp": formatted_timestamp,  # Now in YYYYMMDD_HHMMSS format
                "image_path": row.get('image_path'),
                "image_filename": row.get('image_filename'),
                "analysis": {
                    "clear_sky_score": row.get('clear_sky_score'),
                    "summary": row.get('sky_condition'),
                    "sky_condition": row.get('sky_condition'),
                    "brightness": {
                        "average": row.get('brightness_average')
                    },
                    "sky_features": {
                        "blue_coverage": row.get('blue_coverage_percent')
                    },
                    "from_sd": row.get('from_sd', False)
                }
            })
        
        return history
    
    
    def get_statistics(self):
        """
        Get overall statistics
        
        Returns:
            dict: Statistics summary
        """
        stats = get_statistics()
        
        # Format for compatibility with old interface
        return {
            "total_count": stats['total_captures'],
            "analyzed_count": stats['analyzed_count'],
            "average_score": stats['avg_clear_sky_score'],
            "max_score": stats['max_clear_sky_score'],
            "min_score": stats['min_clear_sky_score'],
            "clear_days": stats['clear_days_count'],
            "avg_brightness": stats['avg_brightness'],
            "avg_blue_coverage": stats['avg_blue_coverage'],
            "first_capture": stats['first_capture'],
            "last_capture": stats['last_capture']
        }
    
    
    def export_csv(self, filepath=None):
        """
        Export all data to CSV file
        
        Args:
            filepath (str): Path to save CSV (default: sky_data_YYYYMMDD_HHMMSS.csv)
        
        Returns:
            str: Path to created CSV file
        """
        return export_to_csv(filepath)
    
    
    def get_daily_statistics(self, days_back=7):
        """
        Get statistics grouped by day
        
        Args:
            days_back (int): Number of days to include
        
        Returns:
            list: Daily statistics
        """
        return get_daily_statistics(days_back)
    
    
    def get_count(self):
        """Get total count of captures"""
        return get_capture_count()
    def save_data(self):
        """Dummy method for backward compatibility with older poller versions"""
        pass

# Global instance
data_manager = DataManager()

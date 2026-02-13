"""
Data Manager Module - SQLite Version
Replaces JSON-based storage with SQLite database

Maintains same interface as before, but uses database backend
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


class DataManager:
    """
    Manages all data storage and retrieval
    
    Now uses SQLite database instead of JSON files
    Interface remains similar for backward compatibility
    """
    
    def __init__(self):
        """Initialize data manager and ensure database exists"""
        # Ensure database is created
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
            timestamp_dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
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
        
        # Format for compatibility with old interface
        return {
            "timestamp": result.get('timestamp'),
            "image_path": result.get('image_path'),
            "analysis": {
                "clear_sky_score": result.get('clear_sky_score'),
                "summary": result.get('sky_condition'),
                "brightness": {
                    "average": result.get('brightness_average'),
                    "score": result.get('brightness_score')
                },
                "sky_features": {
                    "blue_coverage": result.get('blue_coverage_percent'),
                    "gray_coverage": result.get('gray_coverage_percent')
                }
            }
        }
    
    
    def get_history(self, limit=None):
        """
        Get recent captures with analysis
        
        Args:
            limit (int): Maximum number of records (default 100)
        
        Returns:
            list: List of capture records
        """
        if limit is None:
            limit = 100
        
        results = get_recent_captures_with_analysis(limit)
        
        # Format for compatibility
        history = []
        for row in results:
            history.append({
                "timestamp": row.get('timestamp'),
                "image_path": row.get('image_path'),
                "image_filename": row.get('image_filename'),
                "analysis": {
                    "clear_sky_score": row.get('clear_sky_score'),
                    "summary": row.get('sky_condition'),
                    "brightness": {
                        "average": row.get('brightness_average')
                    },
                    "sky_features": {
                        "blue_coverage": row.get('blue_coverage_percent')
                    }
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
        Export data to CSV file
        
        Args:
            filepath (str): Output file path (auto-generated if None)
        
        Returns:
            str: Path to exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"sky_data_export_{timestamp}.csv"
        
        row_count = export_to_csv(filepath)
        
        print(f"✓ Exported {row_count} records to {filepath}")
        
        return filepath
    
    
    def save_data(self):
        """
        Save data (no-op for database version)
        Database auto-saves on each operation
        Kept for backward compatibility
        """
        pass
    
    
    def load_data(self):
        """
        Load data (no-op for database version)
        Database always has latest data
        Kept for backward compatibility
        """
        pass
    
    
    def get_daily_stats(self, days=7):
        """
        Get daily statistics for recent days
        
        Args:
            days (int): Number of days to retrieve
        
        Returns:
            list: Daily statistics
        """
        return get_daily_statistics(days)
    
    
    def get_capture_count(self):
        """Get total number of captures"""
        return get_capture_count()


# Global instance (singleton pattern)
data_manager = DataManager()


if __name__ == '__main__':
    """Test data manager"""
    print("\n" + "="*60)
    print("Testing Data Manager (SQLite Backend)")
    print("="*60 + "\n")
    
    # Test getting latest
    latest = data_manager.get_latest()
    print("Latest capture:")
    print(f"  Timestamp: {latest.get('timestamp')}")
    print(f"  Image: {latest.get('image_path')}")
    
    # Test getting statistics
    print("\nStatistics:")
    stats = data_manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("Data Manager ready!")
    print("="*60 + "\n")

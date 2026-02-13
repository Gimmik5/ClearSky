"""
Database Operations Module
All database insert/query/update operations

Uses SQLite with simple, direct SQL
No ORM - just clean, fast database operations
"""

import sqlite3
from datetime import datetime
from database_schema import get_database_path


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(get_database_path())
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


# ========================================
# CAPTURE OPERATIONS
# ========================================

def insert_capture(timestamp, image_path, image_filename, image_size_bytes=None, 
                   image_width=None, image_height=None):
    """
    Insert a new capture record
    
    Args:
        timestamp (datetime): When image was captured
        image_path (str): Full path to image file
        image_filename (str): Just the filename
        image_size_bytes (int): File size in bytes
        image_width (int): Image width in pixels
        image_height (int): Image height in pixels
    
    Returns:
        int: capture_id of newly created record
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO captures (
            timestamp, image_path, image_filename, 
            image_size_bytes, image_width, image_height,
            upload_success
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, image_path, image_filename,
        image_size_bytes, image_width, image_height,
        True
    ))
    
    capture_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return capture_id


def get_capture_by_id(capture_id):
    """Get a capture record by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM captures WHERE capture_id = ?
    """, (capture_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None


def get_latest_capture():
    """Get the most recent capture"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM captures 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None


def get_captures_last_n_hours(hours):
    """Get all captures from the last N hours"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM captures 
        WHERE timestamp >= datetime('now', ? || ' hours')
        ORDER BY timestamp DESC
    """, (f'-{hours}',))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def get_captures_by_date_range(start_date, end_date):
    """Get captures within a date range"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM captures 
        WHERE DATE(timestamp) BETWEEN ? AND ?
        ORDER BY timestamp DESC
    """, (start_date, end_date))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def get_capture_count():
    """Get total number of captures"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM captures")
    count = cursor.fetchone()[0]
    
    conn.close()
    return count


def mark_analysis_complete(capture_id):
    """Mark a capture as having completed analysis"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE captures 
        SET analysis_complete = TRUE 
        WHERE capture_id = ?
    """, (capture_id,))
    
    conn.commit()
    conn.close()


# ========================================
# SKY ANALYSIS OPERATIONS
# ========================================

def insert_sky_analysis(capture_id, analysis_results):
    """
    Insert sky analysis results
    
    Args:
        capture_id (int): ID of the capture
        analysis_results (dict): Analysis results from analysis_core.py
    
    Returns:
        int: analysis_id of newly created record
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Extract nested data
    brightness = analysis_results.get('brightness', {})
    color = analysis_results.get('color', {})
    sky = analysis_results.get('sky_features', {})
    
    cursor.execute("""
        INSERT INTO sky_analysis (
            capture_id,
            clear_sky_score,
            sky_condition,
            
            brightness_average,
            brightness_condition,
            brightness_score,
            
            color_red,
            color_green,
            color_blue,
            color_brightness,
            color_variance,
            blue_dominant,
            is_gray,
            blue_sky_score,
            
            blue_coverage_percent,
            gray_coverage_percent,
            white_coverage_percent,
            coverage_assessment,
            pixels_sampled
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        capture_id,
        analysis_results.get('clear_sky_score'),
        analysis_results.get('summary'),
        
        brightness.get('average'),
        brightness.get('condition'),
        brightness.get('score'),
        
        color.get('red'),
        color.get('green'),
        color.get('blue'),
        color.get('brightness'),
        color.get('color_variance'),
        color.get('blue_dominant'),
        color.get('is_gray'),
        color.get('blue_sky_score'),
        
        sky.get('blue_coverage'),
        sky.get('gray_coverage'),
        sky.get('white_coverage'),
        sky.get('assessment'),
        sky.get('pixels_sampled')
    ))
    
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return analysis_id


def get_analysis_by_capture_id(capture_id):
    """Get analysis results for a specific capture"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM sky_analysis WHERE capture_id = ?
    """, (capture_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None


def get_latest_analysis():
    """Get the most recent analysis"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM sky_analysis 
        ORDER BY analyzed_at DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None


# ========================================
# COMBINED QUERIES (Capture + Analysis)
# ========================================

def get_latest_capture_with_analysis():
    """Get latest capture with its analysis results"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.*,
            sa.clear_sky_score,
            sa.sky_condition,
            sa.brightness_average,
            sa.brightness_score,
            sa.blue_coverage_percent,
            sa.gray_coverage_percent
        FROM captures c
        LEFT JOIN sky_analysis sa ON c.capture_id = sa.capture_id
        ORDER BY c.timestamp DESC
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None


def get_recent_captures_with_analysis(limit=10):
    """Get recent captures with their analysis"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.capture_id,
            c.timestamp,
            c.image_path,
            c.image_filename,
            sa.clear_sky_score,
            sa.sky_condition,
            sa.brightness_average,
            sa.blue_coverage_percent
        FROM captures c
        LEFT JOIN sky_analysis sa ON c.capture_id = sa.capture_id
        ORDER BY c.timestamp DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def get_captures_by_score_range(min_score, max_score):
    """Get captures within a clear sky score range"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.timestamp,
            c.image_path,
            sa.clear_sky_score,
            sa.sky_condition
        FROM captures c
        JOIN sky_analysis sa ON c.capture_id = sa.capture_id
        WHERE sa.clear_sky_score BETWEEN ? AND ?
        ORDER BY sa.clear_sky_score DESC
    """, (min_score, max_score))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


# ========================================
# STATISTICS QUERIES
# ========================================

def get_statistics():
    """Get overall statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total captures
    cursor.execute("SELECT COUNT(*) FROM captures")
    total_captures = cursor.fetchone()[0]
    
    # Analysis statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as analyzed_count,
            AVG(clear_sky_score) as avg_score,
            MAX(clear_sky_score) as max_score,
            MIN(clear_sky_score) as min_score,
            AVG(brightness_average) as avg_brightness,
            AVG(blue_coverage_percent) as avg_blue_coverage
        FROM sky_analysis
    """)
    
    analysis_stats = dict(cursor.fetchone())
    
    # Clear days (score >= 70)
    cursor.execute("""
        SELECT COUNT(DISTINCT DATE(c.timestamp)) 
        FROM captures c
        JOIN sky_analysis sa ON c.capture_id = sa.capture_id
        WHERE sa.clear_sky_score >= 70
    """)
    clear_days = cursor.fetchone()[0]
    
    # Date range
    cursor.execute("""
        SELECT MIN(timestamp), MAX(timestamp) FROM captures
    """)
    date_range = cursor.fetchone()
    
    conn.close()
    
    return {
        'total_captures': total_captures,
        'analyzed_count': analysis_stats['analyzed_count'] or 0,
        'avg_clear_sky_score': round(analysis_stats['avg_score'] or 0, 1),
        'max_clear_sky_score': analysis_stats['max_score'] or 0,
        'min_clear_sky_score': analysis_stats['min_score'] or 0,
        'avg_brightness': round(analysis_stats['avg_brightness'] or 0, 1),
        'avg_blue_coverage': round(analysis_stats['avg_blue_coverage'] or 0, 1),
        'clear_days_count': clear_days,
        'first_capture': date_range[0],
        'last_capture': date_range[1]
    }


def get_daily_statistics(days=7):
    """Get daily statistics for the last N days"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            DATE(c.timestamp) as date,
            COUNT(*) as capture_count,
            AVG(sa.clear_sky_score) as avg_score,
            MAX(sa.clear_sky_score) as max_score,
            MIN(sa.clear_sky_score) as min_score
        FROM captures c
        LEFT JOIN sky_analysis sa ON c.capture_id = sa.capture_id
        WHERE c.timestamp >= datetime('now', ? || ' days')
        GROUP BY DATE(c.timestamp)
        ORDER BY date DESC
    """, (f'-{days}',))
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


# ========================================
# DATA EXPORT
# ========================================

def export_to_csv(filepath):
    """Export all data to CSV file"""
    import csv
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.timestamp,
            c.image_filename,
            sa.clear_sky_score,
            sa.sky_condition,
            sa.brightness_average,
            sa.brightness_condition,
            sa.color_red,
            sa.color_green,
            sa.color_blue,
            sa.blue_dominant,
            sa.blue_coverage_percent,
            sa.gray_coverage_percent,
            sa.white_coverage_percent
        FROM captures c
        LEFT JOIN sky_analysis sa ON c.capture_id = sa.capture_id
        ORDER BY c.timestamp DESC
    """)
    
    results = cursor.fetchall()
    
    if results:
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Write CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(results)
    
    conn.close()
    
    return len(results)


# ========================================
# UTILITY FUNCTIONS
# ========================================

def delete_old_captures(days_to_keep=90):
    """Delete captures older than N days (keeps database size manageable)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM captures 
        WHERE timestamp < datetime('now', ? || ' days')
    """, (f'-{days_to_keep}',))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count


def vacuum_database():
    """Optimize database (reclaim space after deletions)"""
    conn = get_connection()
    conn.execute("VACUUM")
    conn.close()


if __name__ == '__main__':
    """Test database operations"""
    from database_schema import create_database
    
    print("\n" + "="*60)
    print("Testing Database Operations")
    print("="*60 + "\n")
    
    # Ensure database exists
    create_database()
    
    # Test statistics
    print("Current Statistics:")
    stats = get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("Database operations module ready!")
    print("="*60 + "\n")

"""
Database Schema Module
Creates and manages SQLite database tables

Focused on lab testing - minimal schema for now
Easily extensible for future sensors
"""

import sqlite3
import os
from datetime import datetime


def get_database_path():
    """Get the database file path"""
    return os.path.join('database', 'sky_predictor.db')


def ensure_database_directory():
    """Create database directory if it doesn't exist"""
    db_dir = os.path.dirname(get_database_path())
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"✓ Created database directory: {db_dir}")


def create_database():
    """
    Create database file and all tables
    Safe to call multiple times - only creates if needed
    """
    ensure_database_directory()
    db_path = get_database_path()
    
    # Check if database already exists
    db_exists = os.path.exists(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if not db_exists:
        print("\n" + "="*60)
        print("Creating new SQLite database")
        print("="*60)
    
    # Create tables
    create_captures_table(cursor)
    create_sky_analysis_table(cursor)
    
    # Future tables (commented out for now)
    # create_sensor_readings_table(cursor)
    # create_daily_summary_table(cursor)
    # create_predictions_table(cursor)
    
    conn.commit()
    conn.close()
    
    if not db_exists:
        print("="*60)
        print(f"✓ Database created: {os.path.abspath(db_path)}")
        print("="*60 + "\n")
    
    return db_path


def create_captures_table(cursor):
    """Create captures table - main table linking everything"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            capture_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            
            -- Image Storage
            image_path TEXT NOT NULL,
            image_filename TEXT NOT NULL,
            image_size_bytes INTEGER,
            
            -- Image Metadata
            image_width INTEGER,
            image_height INTEGER,
            
            -- Status
            upload_success BOOLEAN DEFAULT TRUE,
            analysis_complete BOOLEAN DEFAULT FALSE,
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Ensure unique timestamp
            UNIQUE(timestamp)
        )
    """)
    
    # Create indexes for fast queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON captures(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_date 
        ON captures(DATE(timestamp))
    """)
    
    print("✓ Created table: captures")


def create_sky_analysis_table(cursor):
    """Create sky_analysis table - stores analysis results"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sky_analysis (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            capture_id INTEGER NOT NULL,
            
            -- Overall Scores
            clear_sky_score INTEGER,
            sky_condition TEXT,
            
            -- Brightness Analysis
            brightness_average REAL,
            brightness_condition TEXT,
            brightness_score INTEGER,
            
            -- Color Analysis
            color_red REAL,
            color_green REAL,
            color_blue REAL,
            color_brightness REAL,
            color_variance REAL,
            blue_dominant BOOLEAN,
            is_gray BOOLEAN,
            blue_sky_score INTEGER,
            
            -- Sky Coverage (pixel analysis)
            blue_coverage_percent REAL,
            gray_coverage_percent REAL,
            white_coverage_percent REAL,
            coverage_assessment TEXT,
            pixels_sampled INTEGER,
            
            -- Timestamps
            analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            -- Foreign Key
            FOREIGN KEY (capture_id) REFERENCES captures(capture_id) 
                ON DELETE CASCADE
        )
    """)
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_capture 
        ON sky_analysis(capture_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_clear_sky_score 
        ON sky_analysis(clear_sky_score)
    """)
    
    print("✓ Created table: sky_analysis")


def create_sensor_readings_table(cursor):
    """
    Create sensor_readings table (for future use)
    Commented out for now - will add when sensors are integrated
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            capture_id INTEGER,
            
            -- Light Sensor (TSL2561)
            light_lux REAL,
            light_ir REAL,
            light_visible REAL,
            
            -- Pressure/Temp/Humidity (BME280)
            temperature_celsius REAL,
            pressure_hpa REAL,
            humidity_percent REAL,
            
            -- Derived
            dew_point_celsius REAL,
            
            -- Status
            read_success BOOLEAN DEFAULT TRUE,
            
            FOREIGN KEY (capture_id) REFERENCES captures(capture_id) 
                ON DELETE SET NULL
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
        ON sensor_readings(timestamp)
    """)
    
    print("✓ Created table: sensor_readings (future use)")


def get_database_info():
    """Get information about the database"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    info = {
        'path': os.path.abspath(db_path),
        'size_mb': os.path.getsize(db_path) / (1024 * 1024),
        'tables': []
    }
    
    # Get table names
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    
    for (table_name,) in cursor.fetchall():
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        info['tables'].append({
            'name': table_name,
            'rows': count
        })
    
    conn.close()
    
    return info


def print_database_info():
    """Print database information"""
    info = get_database_info()
    
    if not info:
        print("Database does not exist yet")
        return
    
    print("\n" + "="*60)
    print("DATABASE INFORMATION")
    print("="*60)
    print(f"Location: {info['path']}")
    print(f"Size: {info['size_mb']:.2f} MB")
    print("\nTables:")
    for table in info['tables']:
        print(f"  - {table['name']}: {table['rows']} rows")
    print("="*60 + "\n")


def reset_database():
    """
    Delete and recreate database (for testing)
    WARNING: This deletes all data!
    """
    db_path = get_database_path()
    
    if os.path.exists(db_path):
        response = input(f"⚠️  Delete {db_path}? (yes/no): ")
        if response.lower() == 'yes':
            os.remove(db_path)
            print(f"✓ Deleted {db_path}")
            create_database()
        else:
            print("Cancelled")
    else:
        print("Database does not exist")


if __name__ == '__main__':
    """Run this file directly to create/check database"""
    print("\n" + "="*60)
    print("Sky Predictor Database Setup")
    print("="*60 + "\n")
    
    # Create database
    create_database()
    
    # Show info
    print_database_info()
    
    print("Database ready to use!")
    print("\nNext steps:")
    print("  1. Run main.py to start the server")
    print("  2. Upload images from ESP32")
    print("  3. Check database with: python database_schema.py")
    print()

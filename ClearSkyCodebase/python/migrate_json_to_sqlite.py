"""
Migration Script: JSON to SQLite
Migrates existing JSON data to new SQLite database

Run this ONCE to migrate your existing data
"""

import json
import os
from datetime import datetime
from database_schema import create_database
from database_operations import insert_capture, insert_sky_analysis, mark_analysis_complete


def migrate_json_to_sqlite(json_file='analysis_data.json'):
    """
    Migrate data from JSON file to SQLite database
    
    Args:
        json_file (str): Path to existing JSON data file
    """
    
    print("\n" + "="*60)
    print("JSON to SQLite Migration")
    print("="*60 + "\n")
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"✗ JSON file not found: {json_file}")
        print("  No migration needed - starting fresh with SQLite")
        create_database()
        return
    
    # Load JSON data
    print(f"Loading data from {json_file}...")
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create database
    print("Creating SQLite database...")
    create_database()
    
    # Get history from JSON
    history = data.get('history', [])
    
    if not history:
        print("No history data found in JSON file")
        return
    
    print(f"Found {len(history)} records to migrate\n")
    
    # Migrate each record
    migrated = 0
    errors = 0
    
    for i, record in enumerate(history, 1):
        try:
            # Extract data from JSON record
            timestamp_str = record.get('timestamp')
            image_path = record.get('image_path')
            analysis = record.get('analysis', {})
            
            if not timestamp_str or not image_path:
                print(f"  ⚠️  Skipping record {i}: missing timestamp or image_path")
                errors += 1
                continue
            
            # Convert timestamp
            try:
                timestamp_dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except:
                # Try alternative format
                timestamp_dt = datetime.fromisoformat(timestamp_str)
            
            # Get image info
            image_filename = os.path.basename(image_path)
            image_size = None
            if os.path.exists(image_path):
                image_size = os.path.getsize(image_path)
            
            # Insert capture
            capture_id = insert_capture(
                timestamp=timestamp_dt,
                image_path=image_path,
                image_filename=image_filename,
                image_size_bytes=image_size
            )
            
            # Insert analysis (if exists)
            if analysis:
                insert_sky_analysis(capture_id, analysis)
                mark_analysis_complete(capture_id)
            
            migrated += 1
            
            if i % 10 == 0:
                print(f"  Migrated {i}/{len(history)} records...")
        
        except Exception as e:
            print(f"  ✗ Error migrating record {i}: {e}")
            errors += 1
    
    # Summary
    print("\n" + "="*60)
    print("Migration Complete!")
    print("="*60)
    print(f"  Migrated: {migrated} records")
    if errors > 0:
        print(f"  Errors: {errors} records")
    print()
    
    # Ask about backing up old file
    response = input("Backup old JSON file? (yes/no): ")
    if response.lower() == 'yes':
        backup_name = f"{json_file}.backup"
        os.rename(json_file, backup_name)
        print(f"✓ Backed up to: {backup_name}")
    else:
        print("  Old JSON file kept as-is")
    
    print("\n✓ You can now use the SQLite database!")
    print("  The server will automatically use SQLite from now on.\n")


def check_migration_needed():
    """
    Check if migration is needed
    Returns True if JSON file exists but database doesn't have data
    """
    from database_operations import get_capture_count
    
    json_exists = os.path.exists('analysis_data.json')
    
    try:
        db_count = get_capture_count()
    except:
        db_count = 0
    
    return json_exists and db_count == 0


if __name__ == '__main__':
    """Run migration"""
    
    # Check if migration is needed
    if check_migration_needed():
        print("\n⚠️  JSON data file found, but database is empty")
        print("   Migration recommended!\n")
        
        response = input("Run migration now? (yes/no): ")
        if response.lower() == 'yes':
            migrate_json_to_sqlite()
        else:
            print("Migration cancelled")
            print("\nYou can run this script later with:")
            print("  python migrate_json_to_sqlite.py")
    else:
        print("\nNo migration needed")
        print("  Either no JSON file exists, or database already has data")
        print("\nIf you want to force migration, run:")
        print("  python")
        print("  >>> from migrate_json_to_sqlite import migrate_json_to_sqlite")
        print("  >>> migrate_json_to_sqlite()")

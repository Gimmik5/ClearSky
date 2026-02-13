# Database Quick Start Guide

## What Changed: JSON → SQLite

**Before (JSON):**
```
analysis_data.json  ← All data in one file
```

**Now (SQLite):**
```
database/
  └── sky_predictor.db  ← Professional database
images/
  └── YYYY/MM/DD/
      └── *.jpg  ← Images stored separately
```

**Why SQLite is better:**
- ✅ Structured data with relationships
- ✅ Fast queries (can filter by date, score, etc.)
- ✅ Scalable (millions of records)
- ✅ Easy to backup (one file)
- ✅ Ready for ML predictions
- ✅ Can export to CSV anytime

---

## Using the New System

### First Time Setup

**The database is created automatically when you start the server!**

```bash
cd python_v1_modular
python main.py
```

You'll see:
```
Initializing database...
✓ Created table: captures
✓ Created table: sky_analysis
Database ready to use!
```

That's it! The database is now ready.

---

### If You Have Old JSON Data

**Run the migration script:**

```bash
python migrate_json_to_sqlite.py
```

This will:
1. Load your old `analysis_data.json`
2. Import all data into SQLite
3. Backup the JSON file
4. Everything preserved!

---

## Viewing Your Data

### Option 1: Web Interface (Easiest)

Just open: `http://localhost:5000/stats`

You'll see:
- Total captures
- Average scores
- Date ranges
- Statistics

### Option 2: DB Browser (Visual)

**Download:** https://sqlitebrowser.org/ (free)

1. Open DB Browser
2. File → Open Database
3. Select `database/sky_predictor.db`
4. Browse tables visually!

**You can:**
- See all captures
- Filter by date/score
- Run custom queries
- Export to CSV

### Option 3: Python Code

```python
from database_operations import *

# Get statistics
stats = get_statistics()
print(f"Total: {stats['total_captures']}")
print(f"Average score: {stats['avg_clear_sky_score']}")

# Get recent captures
recent = get_recent_captures_with_analysis(10)
for capture in recent:
    print(f"{capture['timestamp']}: {capture['clear_sky_score']}%")

# Get captures with high scores
clear_days = get_captures_by_score_range(70, 100)
print(f"Found {len(clear_days)} clear captures")

# Export everything to CSV
export_to_csv('my_data.csv')
print("Data exported!")
```

---

## Common Operations

### Check Database Info

```bash
python database_schema.py
```

Shows:
```
DATABASE INFORMATION
Location: /path/to/database/sky_predictor.db
Size: 12.34 MB

Tables:
  - captures: 1234 rows
  - sky_analysis: 1234 rows
```

### Export Data to CSV

```python
from data_manager_sqlite import data_manager

# Export all data
data_manager.export_csv('backup.csv')

# Or use API endpoint
# Visit: http://localhost:5000/export/csv
```

### Query by Date Range

```python
from database_operations import get_captures_by_date_range

# Get last week
captures = get_captures_by_date_range('2026-02-01', '2026-02-08')

for cap in captures:
    print(f"{cap['timestamp']}: {cap['clear_sky_score']}%")
```

### Get Daily Statistics

```python
from database_operations import get_daily_statistics

# Last 7 days
daily = get_daily_statistics(days=7)

for day in daily:
    print(f"{day['date']}: {day['capture_count']} captures, "
          f"avg score {day['avg_score']:.1f}%")
```

---

## Database Schema

### captures table
```
capture_id (primary key)
timestamp
image_path
image_filename
image_size_bytes
upload_success
analysis_complete
created_at
```

### sky_analysis table
```
analysis_id (primary key)
capture_id (links to captures)
clear_sky_score
sky_condition
brightness_average
brightness_score
color_red, color_green, color_blue
blue_dominant, is_gray
blue_coverage_percent
gray_coverage_percent
white_coverage_percent
analyzed_at
```

---

## Backup Strategy

### Manual Backup

```bash
# Simply copy the database file
cp database/sky_predictor.db backup/sky_predictor_2026_02_05.db
```

### Automated Backup (Linux/Mac)

Create `backup_db.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
cp database/sky_predictor.db backups/sky_predictor_$DATE.db
echo "Backed up to backups/sky_predictor_$DATE.db"
```

Run daily with cron:
```bash
0 2 * * * /path/to/backup_db.sh
```

### Export to CSV (Alternative)

```python
from data_manager_sqlite import data_manager

# Daily export
import datetime
date = datetime.datetime.now().strftime("%Y%m%d")
data_manager.export_csv(f'backups/data_{date}.csv')
```

---

## Cleaning Up Old Data

### Delete Old Captures

```python
from database_operations import delete_old_captures, vacuum_database

# Keep last 90 days
deleted = delete_old_captures(days_to_keep=90)
print(f"Deleted {deleted} old captures")

# Reclaim disk space
vacuum_database()
print("Database optimized")
```

---

## Advanced Queries

### Find Clearest Days

```python
import sqlite3
from database_schema import get_database_path

conn = sqlite3.connect(get_database_path())
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        DATE(c.timestamp) as day,
        AVG(sa.clear_sky_score) as avg_score,
        COUNT(*) as captures
    FROM captures c
    JOIN sky_analysis sa ON c.capture_id = sa.capture_id
    GROUP BY DATE(c.timestamp)
    HAVING avg_score >= 80
    ORDER BY avg_score DESC
    LIMIT 10
""")

print("Top 10 Clearest Days:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]:.1f}% ({row[2]} captures)")

conn.close()
```

### Brightness Trends Over Time

```python
cursor.execute("""
    SELECT 
        DATE(c.timestamp) as day,
        AVG(sa.brightness_average) as avg_brightness
    FROM captures c
    JOIN sky_analysis sa ON c.capture_id = sa.capture_id
    WHERE c.timestamp >= datetime('now', '-7 days')
    GROUP BY DATE(c.timestamp)
    ORDER BY day
""")

print("Weekly Brightness Trend:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]:.1f}")
```

---

## Troubleshooting

### Database locked error

**Cause:** Another program has database open

**Solution:**
1. Close DB Browser if open
2. Make sure only one server instance running
3. Restart server

### Database file not found

**Solution:**
```python
from database_schema import create_database
create_database()
```

### Want to start fresh

```python
from database_schema import reset_database
reset_database()  # WARNING: Deletes all data!
```

### Migration failed

If JSON migration had errors:

```python
# Check what made it in
from database_operations import get_capture_count
print(f"Imported: {get_capture_count()} captures")

# Try again (won't create duplicates due to unique timestamp)
from migrate_json_to_sqlite import migrate_json_to_sqlite
migrate_json_to_sqlite()
```

---

## Performance Tips

### For Large Datasets (10,000+ captures)

**1. Use date filters:**
```python
# Don't load all history at once
recent = get_captures_last_n_hours(24)  # Just last day
```

**2. Use limits:**
```python
# Limit results
recent = get_recent_captures_with_analysis(limit=50)
```

**3. Export periodically:**
```python
# Export and archive old data
data_manager.export_csv('archive_2026_01.csv')
delete_old_captures(days_to_keep=30)
vacuum_database()
```

---

## What's Next?

### After You Have Data

**30+ days of data unlocks:**
- Statistical analysis
- Trend detection
- Simple predictions

**90+ days unlocks:**
- Machine learning models
- Seasonal patterns
- Weather correlations

**See these guides:**
- `PREDICTION_FEATURES.md` - What features to track
- `DATABASE_DESIGN.md` - Full schema details
- `IMPLEMENTATION_ROADMAP.md` - ML prediction roadmap

---

## Quick Reference

**Create database:**
```python
from database_schema import create_database
create_database()
```

**Get statistics:**
```python
from database_operations import get_statistics
stats = get_statistics()
```

**Export to CSV:**
```python
from data_manager_sqlite import data_manager
data_manager.export_csv('export.csv')
```

**View in browser:**
```
http://localhost:5000/stats
```

**Backup database:**
```bash
cp database/sky_predictor.db backup/
```

---

**That's it! The database makes everything better.** 🎉

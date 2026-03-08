"""
Image Viewer Module - NEW DESIGN
Gallery shows date folders → Click date → See images for that day

DESIGN:
- /gallery → Show list of dates with summary stats
- /gallery/<date> → Show all images for that specific date
- /viewer/<timestamp> → Show individual image
"""
from database_operations import get_distinct_dates_with_stats, get_captures_for_date
from datetime import datetime
from collections import defaultdict
from template_base import (
    wrap_page, create_header, NAV_BAR,
    FOLDER_STYLES, IMAGE_GRID_STYLES, STAT_STYLES
)


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def format_timestamp(ts):
    """Format timestamp to human-readable"""
    if not ts:
        return ''
    if str(ts).startswith('NORTS_'):
        return f"NORTS ({ts.replace('NORTS_', '')}ms)"
    try:
        if isinstance(ts, str):
            dt = datetime.strptime(ts, '%Y%m%d_%H%M%S')
        else:
            dt = ts
        return dt.strftime('%b %d, %Y at %I:%M %p')
    except (ValueError, TypeError):
        return str(ts)


def score_to_color(score):
    """Map score to color"""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return '#9e9e9e'
    if s >= 75:
        return '#4caf50'
    if s >= 50:
        return '#8bc34a'
    if s >= 30:
        return '#ffb300'
    return '#f44336'


# ================================================================
# DATA FUNCTIONS
# ================================================================

def get_date_folders(data_manager):
    """
    Get list of all dates with summary statistics
    
    FIXED: Uses SQL to get distinct dates directly from database
    No longer limited by get_history() default limit
    
    Returns list of dicts:
        date_key: YYYYMMDD
        formatted_date: "March 04, 2026"
        day_of_week: "Wednesday"
        count: number of images
        avg_score: average clear sky score
        best_score: highest score
        worst_score: lowest score
    """
    # Get all distinct dates with stats from database (efficient SQL query)
    date_stats = get_distinct_dates_with_stats()
    
    if not date_stats:
        return []
    
    # Format for display
    folders = []
    for row in date_stats:
        date_str = row.get('date')  # YYYY-MM-DD from database
        
        if not date_str:
            continue
        
        # Convert YYYY-MM-DD to YYYYMMDD for consistency
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_key = date_obj.strftime("%Y%m%d")  # YYYYMMDD
            formatted_date = date_obj.strftime("%B %d, %Y")
            day_of_week = date_obj.strftime("%A")
        except:
            continue
        
        folders.append({
            'date_key': date_key,
            'formatted_date': formatted_date,
            'day_of_week': day_of_week,
            'count': row.get('count', 0),
            'avg_score': row.get('avg_score', 0) or 0,
            'best_score': row.get('max_score', 0) or 0,
            'worst_score': row.get('min_score', 0) or 0
        })
    
    return folders


def get_day_images(data_manager, date_key):
    """
    Get all images for a specific date with statistics
    
    FIXED: Uses SQL to query specific date directly
    No longer limited by get_history() default limit
    
    Args:
        date_key: YYYYMMDD format (e.g., "20260304")
    
    Returns dict:
        found: boolean
        date_key: YYYYMMDD
        formatted_date: "March 04, 2026"
        day_of_week: "Wednesday"
        count: number of images
        avg_score: average score
        avg_brightness: average brightness
        avg_blue: average blue coverage
        best_time: time of best image
        images: list of image dicts
    """
    # Convert YYYYMMDD to YYYY-MM-DD for SQL query
    try:
        date_obj = datetime.strptime(date_key, "%Y%m%d")
        sql_date = date_obj.strftime("%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y")
        day_of_week = date_obj.strftime("%A")
    except:
        return {'found': False}
    
    # Get all captures for this date from database (efficient SQL query)
    captures = get_captures_for_date(sql_date)
    
    if not captures:
        return {'found': False}
    
    # Process captures
    day_images = []
    scores = []
    brightnesses = []
    blues = []
    
    for cap in captures:
        # Extract timestamp
        timestamp = cap.get('timestamp')
        
        # Format timestamp for web (needs to be YYYYMMDD_HHMMSS)
        if isinstance(timestamp, str):
            # Database might return ISO format
            try:
                if ' ' in timestamp:  # "2026-03-04 14:30:22"
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    timestamp_formatted = dt.strftime("%Y%m%d_%H%M%S")
                    time_str = dt.strftime("%I:%M %p")
                else:  # Already formatted
                    timestamp_formatted = timestamp
                    dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                    time_str = dt.strftime("%I:%M %p")
            except:
                timestamp_formatted = timestamp
                time_str = timestamp[9:] if len(timestamp) > 9 else timestamp
        else:
            timestamp_formatted = str(timestamp)
            time_str = str(timestamp)
        
        score = cap.get('clear_sky_score', 0) or 0
        brightness = cap.get('brightness_average', 0) or 0
        blue = cap.get('blue_coverage_percent', 0) or 0
        
        scores.append(score)
        brightnesses.append(brightness)
        blues.append(blue)
        
        day_images.append({
            'timestamp': timestamp_formatted,
            'time': time_str,
            'score': score,
            'brightness': brightness,
            'blue': blue,
            'condition': cap.get('sky_condition', 'Unknown'),
            'from_sd': False
        })
    
    # Calculate statistics
    avg_score = sum(scores) / len(scores) if scores else 0
    avg_brightness = sum(brightnesses) / len(brightnesses) if brightnesses else 0
    avg_blue = sum(blues) / len(blues) if blues else 0
    
    # Find best time
    best_img = max(day_images, key=lambda x: x['score']) if day_images else None
    best_time = best_img['time'] if best_img else "N/A"
    
    return {
        'found': True,
        'date_key': date_key,
        'formatted_date': formatted_date,
        'day_of_week': day_of_week,
        'count': len(day_images),
        'avg_score': round(avg_score, 1),
        'avg_brightness': round(avg_brightness, 1),
        'avg_blue': round(avg_blue, 1),
        'best_time': best_time,
        'images': sorted(day_images, key=lambda x: x['timestamp'], reverse=True)
    }

def get_viewer_context(data_manager, timestamp: str):
    """Get context for individual image viewer"""
    history = data_manager.get_history()
    ts_list = [c.get('timestamp', '') for c in history]

    target = None
    for cap in history:
        if cap.get('timestamp') == timestamp:
            target = cap
            break

    if not target:
        return {
            'found': False,
            'error': 'Capture not found',
            'timestamp': timestamp,
            'prev_ts': None,
            'next_ts': None,
        }

    idx = ts_list.index(timestamp)
    prev_ts = ts_list[idx + 1] if idx + 1 < len(ts_list) else None
    next_ts = ts_list[idx - 1] if idx - 1 >= 0 else None

    analysis = target.get('analysis', {})
    brightness_data = analysis.get('brightness', {})
    sky_features_data = analysis.get('sky_features', {})
    
    if isinstance(brightness_data, dict):
        brightness_avg = brightness_data.get('average')
    else:
        brightness_avg = brightness_data
    
    if isinstance(sky_features_data, dict):
        blue_coverage = sky_features_data.get('blue_coverage')
    else:
        blue_coverage = sky_features_data

    return {
        'found': True,
        'timestamp': timestamp,
        'clear_sky_score': analysis.get('clear_sky_score', 0),
        'summary': analysis.get('summary', 'Unknown'),
        'brightness_avg': brightness_avg,
        'blue_coverage': blue_coverage,
        'from_sd': analysis.get('from_sd', False),
        'prev_ts': prev_ts,
        'next_ts': next_ts,
    }


# ================================================================
# GALLERY INDEX TEMPLATE - Shows date folders
# ================================================================

def create_gallery_index(folders):
    """Create gallery index showing date folders"""
    
    if not folders:
        empty_content = f"""
        <div class="container">
            {create_header("🖼 Gallery", "Browse images by date")}
            {NAV_BAR}
            <div class="card">
                <div class="empty-state">
                    <h2>No Images Yet</h2>
                    <p>Images will appear here once the ESP32 starts sending data.</p>
                </div>
            </div>
        </div>
        """
        return wrap_page("Gallery - Sky Predictor", empty_content, FOLDER_STYLES)
    
    # Build folder cards
    folder_cards = ""
    for folder in folders:
        avg_color = score_to_color(folder['avg_score'])
        
        folder_cards += f"""
        <a href="/gallery/{folder['date_key']}" class="folder-card">
            <div class="folder-header">
                <div class="folder-icon">📅</div>
                <div class="folder-info">
                    <h3>{folder['formatted_date']}</h3>
                    <p>{folder['day_of_week']}</p>
                </div>
            </div>
            <div class="folder-stats">
                <div class="folder-stat">
                    <div class="folder-stat-value">{folder['count']}</div>
                    <div class="folder-stat-label">Images</div>
                </div>
                <div class="folder-stat">
                    <div class="folder-stat-value" style="color: {avg_color}">
                        {folder['avg_score']:.0f}%
                    </div>
                    <div class="folder-stat-label">Avg Score</div>
                </div>
            </div>
        </a>
        """
    
    content = f"""
    <div class="container">
        {create_header("🖼 Gallery", "Browse images by date")}
        {NAV_BAR}
        <div class="card">
            <h2 style="margin-bottom: 20px;">Select a Date</h2>
            <div class="folder-grid">
                {folder_cards}
            </div>
        </div>
    </div>
    """
    
    return wrap_page("Gallery - Sky Predictor", content, FOLDER_STYLES)


# ================================================================
# GALLERY DAY TEMPLATE - Shows images for one date
# ================================================================

def create_gallery_day(day_data):
    """Create gallery day view showing all images for a date"""
    
    if not day_data.get('found'):
        error_content = f"""
        <div class="container">
            {create_header("🖼 Gallery", "Date not found")}
            {NAV_BAR}
            <div class="card">
                <div class="empty-state">
                    <h2>Date Not Found</h2>
                    <p><a href="/gallery">← Back to Gallery</a></p>
                </div>
            </div>
        </div>
        """
        return wrap_page("Gallery - Sky Predictor", error_content)
    
    # Build stats section
    avg_color = score_to_color(day_data['avg_score'])
    stats_html = f"""
    <div class="stat-grid">
        <div class="stat-box">
            <div class="stat-value">{day_data['count']}</div>
            <div class="stat-label">Total Images</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" style="color: {avg_color}">{day_data['avg_score']:.0f}%</div>
            <div class="stat-label">Avg Clear Sky</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{day_data['avg_brightness']:.0f}</div>
            <div class="stat-label">Avg Brightness</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{day_data['avg_blue']:.0f}%</div>
            <div class="stat-label">Avg Blue Coverage</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{day_data['best_time']}</div>
            <div class="stat-label">Best Time</div>
        </div>
    </div>
    """
    
    # Build image grid
    image_cards = ""
    for img in day_data['images']:
        score_color = score_to_color(img['score'])
        sd_badge = '<span class="offline-badge">SD</span>' if img['from_sd'] else ''
        
        image_cards += f"""
        <a href="/viewer/{img['timestamp']}" class="image-card">
            <img src="/image/{img['timestamp']}" 
                 alt="{img['timestamp']}"
                 loading="lazy"
                 onerror="this.src='/image/file/sky_{img['timestamp']}.jpg';">
            <div class="image-info">
                <div class="image-time">{img['time']} {sd_badge}</div>
                <div class="image-score">Score: {img['score']:.0f}%</div>
                <span class="score-badge" style="background: {score_color}">
                    {img['condition']}
                </span>
            </div>
        </a>
        """
    
    content = f"""
    <div class="container">
        {create_header(f"📅 {day_data['formatted_date']}", day_data['day_of_week'])}
        {NAV_BAR}
        
        <div class="card">
            <p style="margin-bottom: 20px;">
                <a href="/gallery" style="color: #667eea; text-decoration: none;">
                    ← Back to Gallery
                </a>
            </p>
            
            <h2 style="margin-bottom: 15px;">Daily Statistics</h2>
            {stats_html}
            
            <h2 style="margin: 30px 0 15px 0;">All Images ({day_data['count']})</h2>
            <div class="image-grid">
                {image_cards}
            </div>
        </div>
    </div>
    """
    
    extra_styles = STAT_STYLES + IMAGE_GRID_STYLES
    return wrap_page(f"{day_data['formatted_date']} - Gallery", content, extra_styles)


# ================================================================
# VIEWER TEMPLATE
# ================================================================

VIEWER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Image Viewer - Sky Predictor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: #1a1a1a;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .viewer-header {
            background: #2a2a2a;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .viewer-title {
            color: white;
            font-size: 1.2em;
        }
        .viewer-nav {
            display: flex;
            gap: 10px;
        }
        .nav-button {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            transition: background 0.2s;
        }
        .nav-button:hover {
            background: #5568d3;
        }
        .nav-button:disabled {
            background: #444;
            cursor: not-allowed;
        }
        .viewer-main {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .viewer-image {
            max-width: 100%;
            max-height: calc(100vh - 200px);
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }
        .viewer-info {
            background: #2a2a2a;
            padding: 20px 30px;
            color: white;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .info-item {
            text-align: center;
        }
        .info-label {
            font-size: 0.85em;
            color: #999;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .info-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        .offline-badge {
            background: #ff9800;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            margin-left: 8px;
        }
    </style>
</head>
<body>
    {% if found %}
    <div class="viewer-header">
        <div class="viewer-title">
            📷 {{ timestamp | format_ts }}
            {% if from_sd %}
            <span class="offline-badge">SD</span>
            {% endif %}
        </div>
        <div class="viewer-nav">
            <a href="/gallery" class="nav-button">← Back to Gallery</a>
            {% if prev_ts %}
                <a href="/viewer/{{ prev_ts }}" class="nav-button">← Previous</a>
            {% else %}
                <button class="nav-button" disabled>← Previous</button>
            {% endif %}
            {% if next_ts %}
                <a href="/viewer/{{ next_ts }}" class="nav-button">Next →</a>
            {% else %}
                <button class="nav-button" disabled>Next →</button>
            {% endif %}
        </div>
    </div>
    
    <div class="viewer-main">
        <img src="/image/{{ timestamp }}" 
             alt="{{ timestamp }}"
             class="viewer-image"
             onerror="this.src='/image/file/sky_{{ timestamp }}.jpg';">
    </div>
    
    <div class="viewer-info">
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Clear Sky Score</div>
                <div class="info-value" style="color: {{ clear_sky_score | score_color }}">
                    {{ "%.0f"|format(clear_sky_score) }}%
                </div>
            </div>
            <div class="info-item">
                <div class="info-label">Condition</div>
                <div class="info-value" style="font-size: 1.1em; color: white;">
                    {{ summary }}
                </div>
            </div>
            {% if brightness_avg %}
            <div class="info-item">
                <div class="info-label">Brightness</div>
                <div class="info-value">
                    {{ "%.1f"|format(brightness_avg) }}
                </div>
            </div>
            {% endif %}
            {% if blue_coverage %}
            <div class="info-item">
                <div class="info-label">Blue Coverage</div>
                <div class="info-value">
                    {{ "%.0f"|format(blue_coverage) }}%
                </div>
            </div>
            {% endif %}
        </div>
    </div>
    {% else %}
    <div class="viewer-header">
        <div class="viewer-title">⚠️ Error</div>
        <div class="viewer-nav">
            <a href="/gallery" class="nav-button">← Back to Gallery</a>
        </div>
    </div>
    <div class="viewer-main" style="color: white; text-align: center;">
        <div>
            <h2>{{ error }}</h2>
            <p style="margin-top: 20px;">Timestamp: {{ timestamp }}</p>
        </div>
    </div>
    {% endif %}
</body>
</html>
'''

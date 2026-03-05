"""
Image Viewer Module - V1.1 CORRECTED
Gallery with daily folder organization - FINAL FIX

FIXES:
- Resolves 'multiple values for keyword argument page' error
- Returns all needed parameters in one dict
- Compatible with v1.1 routes structure
"""

from datetime import datetime
from collections import defaultdict


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def format_timestamp(ts):
    """Format timestamp string to human-readable"""
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
    """Map clear-sky score to a color"""
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


def get_paginated_captures(data_manager, page: int, per_page: int, sort: str):
    """
    FIXED: Return captures organized by DAY with pagination
    Returns ALL parameters needed by template (no conflicts)
    
    Returns dict:
        days           - list of day objects
        total          - total days
        total_captures - total images
        page           - current page
        per_page       - items per page
        sort           - sort order
        total_pages    - total pages
        has_prev       - boolean
        has_next       - boolean
    """
    history = data_manager.get_history()
    
    if not history:
        return {
            'days': [],
            'total': 0,
            'total_captures': 0,
            'page': page,
            'per_page': per_page,
            'sort': sort,
            'total_pages': 1,
            'has_prev': False,
            'has_next': False
        }
    
    # Sort
    if sort == 'asc':
        history = list(reversed(history))
    
    # Group by day
    days_dict = defaultdict(list)
    
    for cap in history:
        timestamp = cap.get('timestamp', '')
        if timestamp and len(timestamp) >= 8:
            date_key = timestamp[:8]  # YYYYMMDD
            
            analysis = cap.get('analysis', {})
            days_dict[date_key].append({
                'timestamp': timestamp,
                'image_path': cap.get('image_path', ''),
                'score': analysis.get('clear_sky_score', 0),
                'condition': analysis.get('summary', 'Unknown'),
                'from_sd': analysis.get('from_sd', False),
            })
    
    # Convert to sorted list
    days_list = []
    for date_key in sorted(days_dict.keys(), reverse=(sort=='desc')):
        captures = days_dict[date_key]
        
        # Calculate stats
        scores = [c['score'] for c in captures if c['score'] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Format date
        try:
            date_obj = datetime.strptime(date_key, "%Y%m%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
            day_of_week = date_obj.strftime("%A")
        except:
            formatted_date = date_key
            day_of_week = ""
        
        days_list.append({
            'date': date_key,
            'formatted_date': formatted_date,
            'day_of_week': day_of_week,
            'count': len(captures),
            'captures': captures,
            'avg_score': round(avg_score, 1)
        })
    
    # Paginate days
    total_days = len(days_list)
    total_pages = max(1, (total_days + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        'days': days_list[start_idx:end_idx],
        'total': total_days,
        'total_captures': len(history),
        'page': page,           # Include in return dict
        'per_page': per_page,   # Include in return dict
        'sort': sort,           # Include in return dict
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }


def get_viewer_context(data_manager, timestamp: str):
    """Build context for individual viewer page"""
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
    
    # Extract nested values
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
        'image_path': target.get('image_path', ''),
        'clear_sky_score': analysis.get('clear_sky_score', 0),
        'summary': analysis.get('summary', 'Unknown'),
        'brightness_avg': brightness_avg,
        'blue_coverage': blue_coverage,
        'from_sd': analysis.get('from_sd', False),
        'prev_ts': prev_ts,
        'next_ts': next_ts,
    }


# ---------------------------------------------------------------------------
# GALLERY TEMPLATE - DAILY FOLDERS
# ---------------------------------------------------------------------------

GALLERY_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Image Gallery - Sky Predictor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.2em;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p { font-size: 0.95em; opacity: 0.9; }
        .nav-bar {
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }
        .nav-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid rgba(255,255,255,0.4);
            padding: 8px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 0.95em;
            text-decoration: none;
            transition: background 0.2s;
        }
        .nav-btn:hover { background: rgba(255,255,255,0.35); }
        
        /* DAILY SECTIONS */
        .day-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .day-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }
        .day-title h2 {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 5px;
        }
        .day-title p {
            color: #666;
            font-size: 0.95em;
        }
        .day-stats {
            display: flex;
            gap: 20px;
        }
        .day-stat {
            text-align: center;
        }
        .day-stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }
        .day-stat-label {
            font-size: 0.85em;
            color: #999;
            text-transform: uppercase;
        }
        
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }
        .gallery-card {
            background: #f5f5f5;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .gallery-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        .gallery-card img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }
        .card-body {
            padding: 12px;
        }
        .ts {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 8px;
        }
        .condition-label {
            font-size: 0.9em;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        .mini-score-bar {
            width: 100%;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 6px;
        }
        .mini-score-fill {
            height: 100%;
            transition: width 0.3s;
        }
        .score-text {
            font-size: 0.8em;
            color: #667eea;
            font-weight: 600;
        }
        .offline-badge {
            background: #ff9800;
            color: white;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.7em;
            margin-left: 5px;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        .page-btn {
            padding: 10px 18px;
            background: white;
            border-radius: 8px;
            text-decoration: none;
            color: #667eea;
            font-weight: 600;
            transition: background 0.2s;
        }
        .page-btn:hover {
            background: #f0f0f0;
        }
        .page-btn.active {
            background: #667eea;
            color: white;
        }
        
        .empty-state {
            text-align: center;
            color: white;
            padding: 60px 20px;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🖼 Image Gallery</h1>
        <p>{{ total_captures }} image(s) organized by day</p>
    </div>

    <div class="nav-bar">
        <a href="/" class="nav-btn">🏠 Live View</a>
        <a href="/gallery" class="nav-btn">🖼 Gallery</a>
        <a href="/daily" class="nav-btn">📅 Daily View</a>
        <a href="/stats" class="nav-btn">📊 Statistics</a>
        <a href="/files" class="nav-btn">📁 File Manager</a>
        <a href="/export/csv" class="nav-btn">⬇ Export CSV</a>
    </div>

    {% if days %}
        {% for day in days %}
        <div class="day-section">
            <div class="day-header">
                <div class="day-title">
                    <h2>{{ day.formatted_date }}</h2>
                    <p>{{ day.day_of_week }}</p>
                </div>
                <div class="day-stats">
                    <div class="day-stat">
                        <div class="day-stat-value">{{ day.count }}</div>
                        <div class="day-stat-label">Images</div>
                    </div>
                    <div class="day-stat">
                        <div class="day-stat-value" style="color: {{ day.avg_score|score_color }}">
                            {{ "%.0f"|format(day.avg_score) }}%
                        </div>
                        <div class="day-stat-label">Avg Score</div>
                    </div>
                </div>
            </div>
            
            <div class="gallery-grid">
                {% for cap in day.captures %}
                <a class="gallery-card" href="/viewer/{{ cap.timestamp }}">
                    <img src="/image/{{ cap.timestamp }}"
                         alt="{{ cap.timestamp }}"
                         loading="lazy"
                         onerror="this.src='/image/file/sky_{{ cap.timestamp }}.jpg';">
                    <div class="card-body">
                        <div class="ts">
                            {{ cap.timestamp | format_ts }}
                            {% if cap.from_sd %}
                            <span class="offline-badge">SD</span>
                            {% endif %}
                        </div>
                        <div class="condition-label">{{ cap.condition }}</div>
                        <div class="mini-score-bar">
                            <div class="mini-score-fill"
                                 style="width:{{ cap.score }}%;
                                        background:{{ cap.score | score_color }};"></div>
                        </div>
                        <div class="score-text">Clear Sky: {{ "%.0f"|format(cap.score) }}%</div>
                    </div>
                </a>
                {% endfor %}
            </div>
        </div>
        {% endfor %}

        {% if total_pages > 1 %}
        <div class="pagination">
            {% if has_prev %}
            <a href="?page={{ page - 1 }}&sort={{ sort }}&per_page={{ per_page }}"
               class="page-btn">← Prev</a>
            {% endif %}
            
            <span class="page-btn active">Page {{ page }} of {{ total_pages }}</span>
            
            {% if has_next %}
            <a href="?page={{ page + 1 }}&sort={{ sort }}&per_page={{ per_page }}"
               class="page-btn">Next →</a>
            {% endif %}
        </div>
        {% endif %}
    {% else %}
        <div class="empty-state">
            <p>No images captured yet.</p>
            <p style="margin-top:10px;font-size:0.9em;">
                Images will appear here once the ESP32 starts sending data.
            </p>
        </div>
    {% endif %}
</div>
</body>
</html>
'''


# ---------------------------------------------------------------------------
# VIEWER TEMPLATE
# ---------------------------------------------------------------------------

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

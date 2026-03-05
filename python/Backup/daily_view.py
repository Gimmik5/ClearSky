"""
Daily View Module - V1.1 FINAL
Images organized by day with statistics
"""

from datetime import datetime
from collections import defaultdict


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


def get_daily_view_data(data_manager, days_back=30):
    """Get captures organized by day with statistics"""
    history = data_manager.get_history(limit=days_back * 144)
    
    if not history:
        return []
    
    # Group by date
    days_dict = defaultdict(list)
    
    for capture in history:
        timestamp_str = capture.get('timestamp')
        if not timestamp_str:
            continue
        
        # Parse timestamp
        try:
            if isinstance(timestamp_str, str):
                if timestamp_str.startswith('NORTS_'):
                    dt = datetime.now()
                else:
                    dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            else:
                dt = timestamp_str
        except:
            continue
        
        date_key = dt.strftime("%Y-%m-%d")
        
        # Extract analysis
        analysis = capture.get('analysis', {})
        brightness_data = analysis.get('brightness', {})
        features_data = analysis.get('sky_features', {}) or analysis.get('features', {})
        
        # Handle nested or direct values
        if isinstance(brightness_data, dict):
            brightness_avg = brightness_data.get('average', 0) or 0
        else:
            brightness_avg = brightness_data or 0
        
        if isinstance(features_data, dict):
            blue_coverage = features_data.get('blue_coverage', 0) or 0
        else:
            blue_coverage = features_data or 0
        
        score = analysis.get('clear_sky_score', 0) or 0
        
        days_dict[date_key].append({
            'timestamp': timestamp_str,
            'datetime': dt,
            'time': dt.strftime("%H:%M:%S"),
            'score': score,
            'brightness': brightness_avg,
            'blue': blue_coverage,
            'condition': get_condition_text(score),
            'from_sd': analysis.get('from_sd', False),
            'image_path': capture.get('image_path')
        })
    
    # Build daily summaries
    days_list = []
    
    for date_key in sorted(days_dict.keys(), reverse=True):
        images = days_dict[date_key]
        
        # Calculate statistics
        scores = [img['score'] for img in images if img['score'] is not None]
        brightnesses = [img['brightness'] for img in images if img['brightness'] is not None]
        blues = [img['blue'] for img in images if img['blue'] is not None]
        
        avg_score = sum(scores) / len(scores) if scores else 0
        avg_brightness = sum(brightnesses) / len(brightnesses) if brightnesses else 0
        avg_blue = sum(blues) / len(blues) if blues else 0
        
        # Find best time
        best_image = max(images, key=lambda x: x['score'] if x['score'] else 0)
        
        # Format date
        try:
            date_obj = datetime.strptime(date_key, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%A, %B %d, %Y")
        except:
            formatted_date = date_key
        
        days_list.append({
            'date': formatted_date,
            'date_key': date_key,
            'count': len(images),
            'avg_score': round(avg_score, 1),
            'avg_brightness': round(avg_brightness, 1),
            'avg_blue': round(avg_blue, 1),
            'best_time': best_image['time'],
            'images': sorted(images, key=lambda x: x['datetime'], reverse=True)
        })
    
    return days_list


def get_condition_text(score):
    """Get condition text from score"""
    try:
        score = float(score) if score is not None else 0
    except:
        score = 0
    
    if score >= 80:
        return "Clear"
    elif score >= 60:
        return "Mostly Clear"
    elif score >= 40:
        return "Partly Cloudy"
    elif score >= 20:
        return "Mostly Cloudy"
    else:
        return "Overcast"


# ===== DAILY VIEW TEMPLATE =====

DAILY_VIEW_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Daily View - Sky Predictor</title>
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
        
        .day-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .day-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        .day-date {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
        .day-count {
            font-size: 0.9em;
            color: #666;
        }
        
        .day-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .stat-box {
            text-align: center;
        }
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }
        
        .images-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }
        .image-card {
            background: #f8f9fa;
            border-radius: 10px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .image-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        .image-card img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }
        .image-info {
            padding: 10px;
        }
        .image-time {
            font-size: 0.9em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .image-score {
            font-size: 0.85em;
            color: #666;
        }
        .score-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
            margin-top: 5px;
        }
        .sd-badge {
            background: #ff9800;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.7em;
            color: white;
            margin-left: 5px;
        }
        
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        
        .collapse-btn {
            background: none;
            border: none;
            color: #667eea;
            cursor: pointer;
            font-size: 1.2em;
            padding: 5px 10px;
        }
        .collapsed .images-grid { display: none; }
        .collapsed .day-stats { display: none; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📅 Daily View</h1>
        <p>Images organized by capture date</p>
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
        <div class="day-card" id="day-{{ loop.index }}">
            <div class="day-header">
                <div>
                    <div class="day-date">{{ day.date }}</div>
                    <div class="day-count">{{ day.count }} image(s)</div>
                </div>
                <button class="collapse-btn" onclick="toggleDay({{ loop.index }})">▼</button>
            </div>
            
            <div class="day-stats">
                <div class="stat-box">
                    <div class="stat-value" style="color: {{ day.avg_score | score_color }}">
                        {{ "%.0f" | format(day.avg_score) }}
                    </div>
                    <div class="stat-label">Avg Clear Sky Score</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{{ "%.0f" | format(day.avg_brightness) }}</div>
                    <div class="stat-label">Avg Brightness</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{{ "%.0f" | format(day.avg_blue) }}%</div>
                    <div class="stat-label">Avg Blue Coverage</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{{ day.best_time }}</div>
                    <div class="stat-label">Best Time</div>
                </div>
            </div>
            
            <div class="images-grid">
                {% for img in day.images %}
                <a href="/viewer/{{ img.timestamp }}" class="image-card">
                    <img src="/image/{{ img.timestamp }}" 
                         alt="{{ img.timestamp }}"
                         loading="lazy"
                         onerror="this.src='/image/file/sky_{{ img.timestamp }}.jpg';">
                    <div class="image-info">
                        <div class="image-time">
                            {{ img.time }}
                            {% if img.from_sd %}
                            <span class="sd-badge">SD</span>
                            {% endif %}
                        </div>
                        <div class="image-score">
                            Sky Score: {{ "%.0f" | format(img.score) }}
                        </div>
                        <span class="score-badge" style="background: {{ img.score | score_color }}">
                            {{ img.condition }}
                        </span>
                    </div>
                </a>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="day-card">
            <div class="no-data">
                <h2>No Data Available</h2>
                <p>Start capturing images to see daily statistics</p>
            </div>
        </div>
    {% endif %}
</div>

<script>
function toggleDay(index) {
    const card = document.getElementById('day-' + index);
    const btn = card.querySelector('.collapse-btn');
    
    if (card.classList.contains('collapsed')) {
        card.classList.remove('collapsed');
        btn.textContent = '▼';
    } else {
        card.classList.add('collapsed');
        btn.textContent = '▶';
    }
}
</script>
</body>
</html>
'''

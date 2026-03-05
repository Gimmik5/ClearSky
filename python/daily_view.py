"""
Daily View Module - REFACTORED
Uses template_base to minimize HTML duplication
"""

from datetime import datetime
from collections import defaultdict
from template_base import wrap_page, create_header, NAV_BAR, STAT_STYLES, IMAGE_GRID_STYLES


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
    """Get captures organized by day"""
    history = data_manager.get_history(limit=days_back * 144)
    
    if not history:
        return []
    
    days_dict = defaultdict(list)
    
    for capture in history:
        timestamp_str = capture.get('timestamp')
        if not timestamp_str:
            continue
        
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
        
        analysis = capture.get('analysis', {})
        brightness_data = analysis.get('brightness', {})
        features_data = analysis.get('sky_features', {}) or analysis.get('features', {})
        
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
            'from_sd': analysis.get('from_sd', False)
        })
    
    # Build summaries
    days_list = []
    for date_key in sorted(days_dict.keys(), reverse=True):
        images = days_dict[date_key]
        
        scores = [img['score'] for img in images if img['score']]
        brightnesses = [img['brightness'] for img in images if img['brightness']]
        blues = [img['blue'] for img in images if img['blue']]
        
        avg_score = sum(scores) / len(scores) if scores else 0
        avg_brightness = sum(brightnesses) / len(brightnesses) if brightnesses else 0
        avg_blue = sum(blues) / len(blues) if blues else 0
        
        best_img = max(images, key=lambda x: x['score'])
        
        try:
            date_obj = datetime.strptime(date_key, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%A, %B %d, %Y")
        except:
            formatted_date = date_key
        
        days_list.append({
            'date': formatted_date,
            'count': len(images),
            'avg_score': round(avg_score, 1),
            'avg_brightness': round(avg_brightness, 1),
            'avg_blue': round(avg_blue, 1),
            'best_time': best_img['time'],
            'images': sorted(images, key=lambda x: x['datetime'], reverse=True)
        })
    
    return days_list


def get_condition_text(score):
    """Get condition from score"""
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


def create_daily_view_page(days):
    """Create daily view page HTML"""
    
    if not days:
        content = f"""
        <div class="container">
            {create_header("📅 Daily View", "Images organized by date")}
            {NAV_BAR}
            <div class="card">
                <div class="empty-state">
                    <h2>No Data Available</h2>
                    <p>Start capturing images to see daily statistics</p>
                </div>
            </div>
        </div>
        """
        return wrap_page("Daily View - Sky Predictor", content)
    
    # Build day cards
    day_cards = ""
    for idx, day in enumerate(days, 1):
        avg_color = score_to_color(day['avg_score'])
        
        # Build image grid for this day
        images_html = ""
        for img in day['images']:
            score_color = score_to_color(img['score'])
            sd_badge = '<span class="offline-badge">SD</span>' if img['from_sd'] else ''
            
            images_html += f"""
            <a href="/viewer/{img['timestamp']}" class="image-card">
                <img src="/image/{img['timestamp']}" loading="lazy" 
                     onerror="this.src='/image/file/sky_{img['timestamp']}.jpg';">
                <div class="image-info">
                    <div class="image-time">{img['time']} {sd_badge}</div>
                    <div class="image-score">Score: {img['score']:.0f}%</div>
                    <span class="score-badge" style="background:{score_color}">{img['condition']}</span>
                </div>
            </a>
            """
        
        day_cards += f"""
        <div class="card" id="day-{idx}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:15px;border-bottom:2px solid #f0f0f0;">
                <div>
                    <h2>{day['date']}</h2>
                    <p style="color:#666;">{day['count']} image(s)</p>
                </div>
                <button onclick="toggleDay({idx})" style="background:none;border:none;color:#667eea;cursor:pointer;font-size:1.2em;">▼</button>
            </div>
            
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-value" style="color:{avg_color}">{day['avg_score']:.0f}</div>
                    <div class="stat-label">Avg Clear Sky</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{day['avg_brightness']:.0f}</div>
                    <div class="stat-label">Avg Brightness</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{day['avg_blue']:.0f}%</div>
                    <div class="stat-label">Avg Blue</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{day['best_time']}</div>
                    <div class="stat-label">Best Time</div>
                </div>
            </div>
            
            <div class="image-grid" style="margin-top:20px;">
                {images_html}
            </div>
        </div>
        """
    
    content = f"""
    <div class="container">
        {create_header("📅 Daily View", "Images organized by capture date")}
        {NAV_BAR}
        {day_cards}
    </div>
    """
    
    extra_styles = STAT_STYLES + IMAGE_GRID_STYLES + """
        .collapsed .image-grid, .collapsed .stat-grid { display: none; }
    """
    
    extra_scripts = """
        function toggleDay(idx) {
            const card = document.getElementById('day-' + idx);
            const btn = card.querySelector('button');
            if (card.classList.contains('collapsed')) {
                card.classList.remove('collapsed');
                btn.textContent = '▼';
            } else {
                card.classList.add('collapsed');
                btn.textContent = '▶';
            }
        }
    """
    
    return wrap_page("Daily View - Sky Predictor", content, extra_styles, extra_scripts)


# For backwards compatibility with existing routes
DAILY_VIEW_TEMPLATE = None  # Not used anymore, we use create_daily_view_page() instead

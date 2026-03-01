"""
Image Viewer Module (V1.1)

Provides two browser views:
  /gallery          – Responsive grid of all captured images with
                      thumbnails, timestamps, and sky scores.
  /viewer/<timestamp> – Full-size individual image viewer with complete
                        analysis breakdown and prev/next navigation.

Both pages match the existing purple-gradient visual style used by the
main dashboard (web_templates.py).
"""

# ---------------------------------------------------------------------------
# GALLERY PAGE TEMPLATE
# ---------------------------------------------------------------------------

GALLERY_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sky Predictor - Gallery</title>
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
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 {
            font-size: 2.2em; margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p { font-size: 1em; opacity: 0.85; }
        .nav-bar {
            display: flex; gap: 12px; justify-content: center;
            flex-wrap: wrap; margin-bottom: 24px;
        }
        .nav-btn {
            background: rgba(255,255,255,0.2);
            color: white; border: 2px solid rgba(255,255,255,0.4);
            padding: 8px 20px; border-radius: 25px; cursor: pointer;
            font-size: 0.95em; text-decoration: none;
            transition: background 0.2s;
        }
        .nav-btn:hover { background: rgba(255,255,255,0.35); }
        .filter-bar {
            background: rgba(255,255,255,0.15);
            border-radius: 12px; padding: 14px 20px;
            margin-bottom: 24px; display: flex;
            align-items: center; gap: 16px; flex-wrap: wrap;
        }
        .filter-bar label { color: white; font-size: 0.9em; }
        .filter-bar select, .filter-bar input {
            padding: 6px 12px; border-radius: 8px; border: none;
            font-size: 0.9em; background: white;
        }
        .stats-strip {
            display: flex; gap: 14px; margin-bottom: 24px; flex-wrap: wrap;
        }
        .stat-pill {
            background: rgba(255,255,255,0.2);
            color: white; border-radius: 20px;
            padding: 6px 16px; font-size: 0.9em;
        }
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 16px;
        }
        .gallery-card {
            background: white; border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            transition: transform 0.18s, box-shadow 0.18s;
            cursor: pointer; text-decoration: none; color: inherit;
            display: block;
        }
        .gallery-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.25);
        }
        .gallery-card img {
            width: 100%; height: 150px;
            object-fit: cover; display: block;
        }
        .gallery-card .card-body { padding: 12px; }
        .gallery-card .ts {
            font-size: 0.78em; color: #666; margin-bottom: 6px;
        }
        .gallery-card .condition-label {
            font-size: 1em; font-weight: 600; margin-bottom: 6px;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .mini-score-bar {
            width: 100%; height: 8px; background: #e0e0e0;
            border-radius: 4px; overflow: hidden; margin-bottom: 4px;
        }
        .mini-score-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
        .score-text { font-size: 0.8em; color: #555; }
        .offline-badge {
            display: inline-block; font-size: 0.7em;
            background: #ff9800; color: white;
            border-radius: 4px; padding: 1px 5px; margin-left: 4px;
        }
        .empty-state {
            grid-column: 1 / -1; text-align: center;
            color: white; padding: 60px 20px; font-size: 1.1em; opacity: 0.8;
        }
        .pagination {
            display: flex; justify-content: center; gap: 8px;
            margin-top: 30px; flex-wrap: wrap;
        }
        .page-btn {
            background: rgba(255,255,255,0.2); color: white;
            border: 2px solid rgba(255,255,255,0.3);
            padding: 7px 14px; border-radius: 8px;
            cursor: pointer; font-size: 0.9em; text-decoration: none;
        }
        .page-btn.active { background: white; color: #764ba2; font-weight: bold; }
        .page-btn:hover:not(.active) { background: rgba(255,255,255,0.35); }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📷 Image Gallery</h1>
        <p>All captured sky images – click any to view full analysis</p>
    </div>

    <div class="nav-bar">
        <a href="/" class="nav-btn">🏠 Live View</a>
        <a href="/stats" class="nav-btn">📊 Statistics</a>
        <a href="/gallery" class="nav-btn">🖼 Gallery</a>
        <a href="/export/csv" class="nav-btn">⬇ Export CSV</a>
    </div>

    <div class="stats-strip">
        <span class="stat-pill">📸 {{ total_captures }} total captures</span>
        <span class="stat-pill">📄 Page {{ page }} of {{ total_pages }}</span>
        {% if avg_score is not none %}
        <span class="stat-pill">☀ Avg score: {{ "%.0f"|format(avg_score) }}%</span>
        {% endif %}
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
        <label>Sort:</label>
        <select id="sortSelect" onchange="applyFilters()">
            <option value="desc" {% if sort == 'desc' %}selected{% endif %}>Newest first</option>
            <option value="asc"  {% if sort == 'asc'  %}selected{% endif %}>Oldest first</option>
        </select>
        <label>Show:</label>
        <select id="limitSelect" onchange="applyFilters()">
            <option value="24"  {% if per_page == 24  %}selected{% endif %}>24 per page</option>
            <option value="48"  {% if per_page == 48  %}selected{% endif %}>48 per page</option>
            <option value="96"  {% if per_page == 96  %}selected{% endif %}>96 per page</option>
        </select>
    </div>

    <div class="gallery-grid" id="galleryGrid">
        {% if captures %}
            {% for cap in captures %}
            <a class="gallery-card" href="/viewer/{{ cap.timestamp }}">
                <img src="/image/{{ cap.timestamp }}"
                     alt="{{ cap.timestamp }}"
                     onerror="this.src='/static/placeholder.jpg'; this.onerror=null;">
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
        {% else %}
            <div class="empty-state">
                <p>No images captured yet.</p>
                <p style="margin-top:10px;font-size:0.9em;">
                    Images will appear here once the ESP32 starts sending data.
                </p>
            </div>
        {% endif %}
    </div>

    <!-- Pagination -->
    {% if total_pages > 1 %}
    <div class="pagination">
        {% if page > 1 %}
        <a href="{{ url_for('gallery', page=page-1, sort=sort, per_page=per_page) }}"
           class="page-btn">← Prev</a>
        {% endif %}
        {% for p in range(1, total_pages + 1) %}
        <a href="{{ url_for('gallery', page=p, sort=sort, per_page=per_page) }}"
           class="page-btn {% if p == page %}active{% endif %}">{{ p }}</a>
        {% endfor %}
        {% if page < total_pages %}
        <a href="{{ url_for('gallery', page=page+1, sort=sort, per_page=per_page) }}"
           class="page-btn">Next →</a>
        {% endif %}
    </div>
    {% endif %}
</div>

<script>
function applyFilters() {
    const sort    = document.getElementById('sortSelect').value;
    const perPage = document.getElementById('limitSelect').value;
    window.location.href = `/gallery?page=1&sort=${sort}&per_page=${perPage}`;
}
</script>
</body>
</html>
'''


# ---------------------------------------------------------------------------
# INDIVIDUAL VIEWER PAGE TEMPLATE
# ---------------------------------------------------------------------------

VIEWER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sky Predictor – {{ timestamp | format_ts }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 24px; }
        .header h1 { font-size: 1.8em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p  { font-size: 0.95em; opacity: 0.85; margin-top: 6px; }

        .nav-bar {
            display: flex; gap: 10px; justify-content: center;
            flex-wrap: wrap; margin-bottom: 22px;
        }
        .nav-btn {
            background: rgba(255,255,255,0.2); color: white;
            border: 2px solid rgba(255,255,255,0.4);
            padding: 7px 18px; border-radius: 25px; cursor: pointer;
            font-size: 0.9em; text-decoration: none; transition: background 0.2s;
        }
        .nav-btn:hover  { background: rgba(255,255,255,0.35); }
        .nav-btn.prev-next {
            background: rgba(255,255,255,0.3); font-weight: 600;
        }

        .layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 760px) { .layout { grid-template-columns: 1fr; } }

        .card {
            background: white; border-radius: 15px; padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .image-card { display: flex; flex-direction: column; gap: 12px; }
        .image-card img {
            width: 100%; border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .image-meta { font-size: 0.85em; color: #555; line-height: 1.6; }
        .image-meta strong { color: #333; }
        .download-btn {
            display: inline-block; background: #667eea; color: white;
            padding: 8px 18px; border-radius: 8px; text-decoration: none;
            font-size: 0.9em; text-align: center; margin-top: 6px;
        }
        .download-btn:hover { background: #5568d4; }

        .analysis-card h2 {
            font-size: 1.2em; color: #333; margin-bottom: 14px;
            border-bottom: 2px solid #f0f0f0; padding-bottom: 8px;
        }
        .condition-block {
            font-size: 1.5em; font-weight: 700; text-align: center;
            padding: 14px; border-radius: 10px; margin-bottom: 16px;
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        }

        /* Score bar */
        .score-row { margin-bottom: 14px; }
        .score-label {
            display: flex; justify-content: space-between;
            font-size: 0.9em; color: #555; margin-bottom: 4px;
        }
        .score-bar {
            width: 100%; height: 22px; background: #e0e0e0;
            border-radius: 11px; overflow: hidden;
        }
        .score-fill { height: 100%; border-radius: 11px; transition: width 0.5s; }

        /* Detail grid */
        .detail-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
            margin-top: 12px;
        }
        .detail-item {
            background: #f8f9fa; border-radius: 8px; padding: 10px;
        }
        .detail-item .d-label { font-size: 0.75em; color: #888; margin-bottom: 3px; }
        .detail-item .d-value { font-size: 1em; font-weight: 600; color: #333; }

        /* Color swatches */
        .color-section { margin-top: 14px; }
        .color-section h3 {
            font-size: 0.9em; color: #666; margin-bottom: 8px;
        }
        .color-swatches { display: flex; gap: 6px; flex-wrap: wrap; }
        .swatch {
            width: 36px; height: 36px; border-radius: 8px;
            border: 2px solid rgba(0,0,0,0.1);
            position: relative;
        }
        .swatch-tip {
            position: absolute; bottom: -22px; left: 50%;
            transform: translateX(-50%); font-size: 0.65em;
            white-space: nowrap; color: #555;
        }

        .sd-badge {
            display: inline-block; background: #ff9800; color: white;
            font-size: 0.75em; padding: 2px 8px; border-radius: 10px; margin-left: 6px;
        }
        .not-found {
            color: white; text-align: center; padding: 60px 20px; font-size: 1.1em;
        }
    </style>
</head>
<body>
<div class="container">

    <div class="header">
        <h1>Sky Capture Viewer</h1>
        <p>
            {{ timestamp | format_ts }}
            {% if from_sd %}<span class="sd-badge">📁 Restored from SD</span>{% endif %}
        </p>
    </div>

    <div class="nav-bar">
        <a href="/" class="nav-btn">🏠 Live</a>
        <a href="/gallery" class="nav-btn">🖼 Gallery</a>
        <a href="/stats" class="nav-btn">📊 Stats</a>
        {% if prev_ts %}
        <a href="/viewer/{{ prev_ts }}" class="nav-btn prev-next">← Previous</a>
        {% endif %}
        {% if next_ts %}
        <a href="/viewer/{{ next_ts }}" class="nav-btn prev-next">Next →</a>
        {% endif %}
    </div>

    {% if not found %}
    <div class="not-found">
        <p>⚠ Capture not found: <strong>{{ timestamp }}</strong></p>
        <p style="margin-top:12px;font-size:0.9em;">
            <a href="/gallery" style="color:white;">← Return to gallery</a>
        </p>
    </div>
    {% else %}

    <div class="layout">
        <!-- Left: Image -->
        <div class="card image-card">
            <img src="/image/{{ timestamp }}" alt="{{ timestamp }}"
                 onerror="this.alt='Image file not found on server';">
            <div class="image-meta">
                <div><strong>Timestamp:</strong> {{ timestamp | format_ts }}</div>
                <div><strong>File:</strong> {{ image_path or 'unknown' }}</div>
                {% if width and height %}
                <div><strong>Resolution:</strong> {{ width }} × {{ height }}px</div>
                {% endif %}
            </div>
            <a href="/image/{{ timestamp }}" download="{{ timestamp }}.jpg"
               class="download-btn">⬇ Download JPEG</a>
        </div>

        <!-- Right: Analysis -->
        <div class="card analysis-card">
            <h2>Analysis Results</h2>

            {% if condition %}
            <div class="condition-block">{{ condition }}</div>
            {% endif %}

            <!-- Clear-sky score bar -->
            {% if score is not none %}
            <div class="score-row">
                <div class="score-label">
                    <span>☀ Clear Sky Score</span>
                    <span><strong>{{ "%.0f"|format(score) }}%</strong></span>
                </div>
                <div class="score-bar">
                    <div class="score-fill"
                         style="width:{{ score }}%;
                                background:{{ score | score_color }};"></div>
                </div>
            </div>
            {% endif %}

            <!-- Detail grid -->
            <div class="detail-grid">
                {% if brightness is not none %}
                <div class="detail-item">
                    <div class="d-label">Brightness</div>
                    <div class="d-value">{{ "%.1f"|format(brightness) }}</div>
                </div>
                {% endif %}
                {% if blue_ratio is not none %}
                <div class="detail-item">
                    <div class="d-label">Blue Ratio</div>
                    <div class="d-value">{{ "%.1f"|format(blue_ratio * 100) }}%</div>
                </div>
                {% endif %}
                {% if grey_ratio is not none %}
                <div class="detail-item">
                    <div class="d-label">Grey / Cloud Ratio</div>
                    <div class="d-value">{{ "%.1f"|format(grey_ratio * 100) }}%</div>
                </div>
                {% endif %}
                {% if saturation is not none %}
                <div class="detail-item">
                    <div class="d-label">Saturation</div>
                    <div class="d-value">{{ "%.1f"|format(saturation) }}</div>
                </div>
                {% endif %}
                {% if contrast is not none %}
                <div class="detail-item">
                    <div class="d-label">Contrast</div>
                    <div class="d-value">{{ "%.1f"|format(contrast) }}</div>
                </div>
                {% endif %}
                {% if sky_coverage is not none %}
                <div class="detail-item">
                    <div class="d-label">Sky Coverage</div>
                    <div class="d-value">{{ "%.1f"|format(sky_coverage) }}%</div>
                </div>
                {% endif %}
            </div>

            <!-- Dominant colours -->
            {% if dominant_colors %}
            <div class="color-section">
                <h3>Dominant Colours</h3>
                <div class="color-swatches">
                    {% for color in dominant_colors %}
                    <div class="swatch"
                         style="background: rgb({{ color[0] }},{{ color[1] }},{{ color[2] }});"
                         title="RGB({{ color[0] }},{{ color[1] }},{{ color[2] }})">
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

        </div>
    </div>
    {% endif %}

</div>
</body>
</html>
'''


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def format_timestamp(ts: str) -> str:
    """Convert YYYYMMDD_HHMMSS to a readable string."""
    try:
        date_part, time_part = ts.split('_')
        y, m, d = date_part[:4], date_part[4:6], date_part[6:8]
        hh, mm, ss = time_part[:2], time_part[2:4], time_part[4:6]
        return f"{d}/{m}/{y}  {hh}:{mm}:{ss}"
    except Exception:
        return ts


def score_to_color(score: float) -> str:
    """Return a CSS colour that maps linearly from red (0%) to green (100%)."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return '#9e9e9e'
    if s >= 75:
        return '#4caf50'   # Green
    if s >= 50:
        return '#8bc34a'   # Light green
    if s >= 30:
        return '#ffb300'   # Amber
    return '#f44336'       # Red


def get_paginated_captures(data_manager, page: int, per_page: int, sort: str):
    """
    Return a slice of the capture history plus pagination metadata.

    Returns a dict:
      captures      – list of dicts for this page
      total_captures – total number of captures in the database
      total_pages   – total number of pages
      avg_score     – average clear-sky score across all captures (or None)
    """
    history = data_manager.get_history()    # Full list, newest first from DB

    if sort == 'asc':
        history = list(reversed(history))

    total = len(history)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end   = start + per_page
    slice_ = history[start:end]

    avg_score = None
    if history:
        scores = [
            c.get('analysis', {}).get('clear_sky_score', 0)
            for c in history
            if c.get('analysis')
        ]
        if scores:
            avg_score = sum(scores) / len(scores)

    # Flatten each capture for easy template access
    captures = []
    for cap in slice_:
        analysis = cap.get('analysis', {})
        captures.append({
            'timestamp': cap.get('timestamp', ''),
            'image_path': cap.get('image_path', ''),
            'score':     analysis.get('clear_sky_score', 0),
            'condition': analysis.get('condition', 'Unknown'),
            'from_sd':   cap.get('from_sd', False),
        })

    return {
        'captures':       captures,
        'total_captures': total,
        'total_pages':    total_pages,
        'avg_score':      avg_score,
    }


def get_viewer_context(data_manager, timestamp: str):
    """
    Build the template context dict for the individual viewer page.
    Also resolves the previous and next timestamps for navigation.
    """
    history = data_manager.get_history()   # Newest first
    # Build a flat list of timestamps for nav
    ts_list = [c.get('timestamp', '') for c in history]

    target = None
    for cap in history:
        if cap.get('timestamp') == timestamp:
            target = cap
            break

    if not target:
        return {
            'found':     False,
            'timestamp': timestamp,
            'prev_ts':   None,
            'next_ts':   None,
        }

    # Navigation: in the "newest first" list, prev = index+1, next = index-1
    idx     = ts_list.index(timestamp)
    prev_ts = ts_list[idx + 1] if idx + 1 < len(ts_list) else None
    next_ts = ts_list[idx - 1] if idx - 1 >= 0              else None

    analysis = target.get('analysis', {})
    dom_colors = analysis.get('dominant_colors', [])

    # dominant_colors can be stored as list of [R,G,B] lists or tuples
    safe_colors = []
    for c in (dom_colors or [])[:6]:
        try:
            safe_colors.append((int(c[0]), int(c[1]), int(c[2])))
        except (IndexError, TypeError, ValueError):
            pass

    return {
        'found':           True,
        'timestamp':       timestamp,
        'image_path':      target.get('image_path', ''),
        'from_sd':         target.get('from_sd', False),
        'condition':       analysis.get('condition', 'Unknown'),
        'score':           analysis.get('clear_sky_score'),
        'brightness':      analysis.get('brightness'),
        'blue_ratio':      analysis.get('blue_ratio'),
        'grey_ratio':      analysis.get('grey_ratio'),
        'saturation':      analysis.get('saturation'),
        'contrast':        analysis.get('contrast'),
        'sky_coverage':    analysis.get('sky_coverage_percent'),
        'dominant_colors': safe_colors,
        'width':           analysis.get('width'),
        'height':          analysis.get('height'),
        'prev_ts':         prev_ts,
        'next_ts':         next_ts,
    }

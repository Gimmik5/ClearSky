"""
Template Base System
Reusable HTML components to minimize duplication

Usage:
    from template_base import wrap_page, create_header, NAV_BAR, FOLDER_STYLES
"""

# ================================================================
# BASE STYLES
# ================================================================

BASE_STYLES = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 20px;
    }
    .container {
        max-width: 1400px;
        margin: 0 auto;
    }
    .header {
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .header h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .header p {
        font-size: 1.1em;
        opacity: 0.9;
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
        border: 2px solid rgba(255,255,255,0.5);
        padding: 8px 22px;
        border-radius: 25px;
        cursor: pointer;
        font-size: 0.95em;
        text-decoration: none;
        transition: background 0.2s;
    }
    .nav-btn:hover {
        background: rgba(255,255,255,0.35);
    }
    .card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
"""

# ================================================================
# NAVIGATION BAR
# ================================================================

NAV_BAR = """
    <div class="nav-bar">
        <a href="/" class="nav-btn">🏠 Live View</a>
        <a href="/gallery" class="nav-btn">🖼 Gallery</a>
        <a href="/stats" class="nav-btn">📊 Statistics</a>
        <a href="/files" class="nav-btn">📁 File Manager</a>
        <a href="/export/csv" class="nav-btn">⬇ Export CSV</a>
    </div>
"""

# ================================================================
# HELPER FUNCTIONS
# ================================================================

def create_header(title, subtitle=""):
    """Create page header"""
    subtitle_html = f'<p>{subtitle}</p>' if subtitle else ''
    return f"""
    <div class="header">
        <h1>{title}</h1>
        {subtitle_html}
    </div>
    """

def wrap_page(title, content, extra_styles="", extra_scripts=""):
    """Wrap content in complete HTML page"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        {BASE_STYLES}
        {extra_styles}
    </style>
</head>
<body>
    {content}
    <script>
        {extra_scripts}
    </script>
</body>
</html>"""

# ================================================================
# REUSABLE STYLE BLOCKS
# ================================================================

FOLDER_STYLES = """
    .folder-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
    }
    .folder-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        transition: transform 0.2s, box-shadow 0.2s;
        text-decoration: none;
        color: inherit;
        display: block;
        cursor: pointer;
    }
    .folder-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    }
    .folder-header {
        display: flex;
        align-items: center;
        margin-bottom: 18px;
        padding-bottom: 18px;
        border-bottom: 2px solid #e0e0e0;
    }
    .folder-icon {
        font-size: 2.8em;
        margin-right: 15px;
    }
    .folder-info h3 {
        font-size: 1.4em;
        color: #333;
        margin-bottom: 5px;
    }
    .folder-info p {
        font-size: 0.9em;
        color: #666;
    }
    .folder-stats {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .folder-stat {
        text-align: center;
        padding: 12px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    .folder-stat-value {
        font-size: 1.6em;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 3px;
    }
    .folder-stat-label {
        font-size: 0.75em;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
"""

IMAGE_GRID_STYLES = """
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
    }
    .image-card {
        background: #f5f5f5;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        text-decoration: none;
        color: inherit;
        display: block;
    }
    .image-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .image-card img {
        width: 100%;
        height: 150px;
        object-fit: cover;
    }
    .image-info {
        padding: 12px;
    }
    .image-time {
        font-size: 0.85em;
        color: #666;
        margin-bottom: 8px;
    }
    .image-score {
        font-size: 0.8em;
        color: #667eea;
        font-weight: 600;
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
    .offline-badge {
        background: #ff9800;
        color: white;
        padding: 2px 6px;
        border-radius: 8px;
        font-size: 0.7em;
        margin-left: 5px;
    }
"""

STAT_STYLES = """
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 15px;
        margin: 20px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 12px;
    }
    .stat-box {
        text-align: center;
    }
    .stat-value {
        font-size: 2em;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 5px;
    }
    .stat-label {
        font-size: 0.85em;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
"""

LOADING_STYLES = """
    .loading {
        text-align: center;
        padding: 60px 20px;
        color: #666;
    }
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #999;
    }
    .empty-state h2 {
        margin-bottom: 15px;
        color: #666;
    }
"""

# Export all
__all__ = [
    'BASE_STYLES', 'NAV_BAR', 'create_header', 'wrap_page',
    'FOLDER_STYLES', 'IMAGE_GRID_STYLES', 'STAT_STYLES', 'LOADING_STYLES'
]

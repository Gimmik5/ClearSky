"""
Template Base Module
Reusable HTML components to avoid duplication across templates

Usage:
    from template_base import create_page, NAV_BAR, COMMON_STYLES
"""

# ================================================================
# COMMON CSS STYLES
# ================================================================

COMMON_STYLES = '''
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
'''

# ================================================================
# NAVIGATION BAR
# ================================================================

NAV_BAR = '''
    <div class="nav-bar">
        <a href="/" class="nav-btn">🏠 Live View</a>
        <a href="/gallery" class="nav-btn">🖼 Gallery</a>
        <a href="/daily" class="nav-btn">📅 Daily View</a>
        <a href="/stats" class="nav-btn">📊 Statistics</a>
        <a href="/files" class="nav-btn">📁 File Manager</a>
        <a href="/export/csv" class="nav-btn">⬇ Export CSV</a>
    </div>
'''

# ================================================================
# HEADER COMPONENT
# ================================================================

def create_header(title, subtitle):
    """Create page header"""
    return f'''
    <div class="header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    '''

# ================================================================
# PAGE TEMPLATE FUNCTION
# ================================================================

def create_page(title, content, extra_styles='', extra_scripts=''):
    """
    Create complete HTML page with common elements
    
    Args:
        title: Page title
        content: Page content (with header, nav already included if needed)
        extra_styles: Additional CSS styles
        extra_scripts: Additional JavaScript
    
    Returns:
        str: Complete HTML page
    """
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        {COMMON_STYLES}
        {extra_styles}
    </style>
</head>
<body>
    {content}
    <script>
        {extra_scripts}
    </script>
</body>
</html>
'''

# ================================================================
# USAGE EXAMPLES
# ================================================================

"""
EXAMPLE 1: Simple page with header and nav

from template_base import create_page, create_header, NAV_BAR

page_content = '''
    <div class="container">
        ''' + create_header("🏠 Live View", "Real-time sky analysis") + '''
        ''' + NAV_BAR + '''
        
        <div class="card">
            <p>Your page content here</p>
        </div>
    </div>
'''

html = create_page("Live View - Sky Predictor", page_content)

# ----------------------------------------------------------------

EXAMPLE 2: Custom styles and scripts

extra_css = '''
    .custom-class {
        color: red;
    }
'''

extra_js = '''
    function myFunction() {
        console.log('Custom script');
    }
'''

html = create_page(
    title="Custom Page",
    content=page_content,
    extra_styles=extra_css,
    extra_scripts=extra_js
)

# ----------------------------------------------------------------

EXAMPLE 3: Refactored template

# OLD (duplicated HTML):
LIVE_VIEW_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>...</title>
    <style>
        * { margin: 0; ... }
        body { ... }
        .header { ... }
        .nav-bar { ... }
    </style>
</head>
<body>
    <div class="header">...</div>
    <div class="nav-bar">...</div>
    ...
</body>
</html>
'''

# NEW (using template_base):
from template_base import create_page, create_header, NAV_BAR

extra_styles = '''
    /* Only page-specific styles here */
    .score-bar { ... }
'''

page_content = '''
    <div class="container">
        ''' + create_header("🏠 Live View", "Real-time sky analysis") + '''
        ''' + NAV_BAR + '''
        
        <div class="card" id="content">
            <!-- Page-specific content -->
        </div>
    </div>
'''

LIVE_VIEW_TEMPLATE = create_page(
    title="Sky Predictor - Live View",
    content=page_content,
    extra_styles=extra_styles
)
"""

# ================================================================
# REFACTORED TEMPLATE CREATOR FUNCTIONS
# ================================================================

def create_live_view_template():
    """Create Live View template using base components"""
    
    extra_styles = '''
    .score-bar {
        width: 100%;
        height: 40px;
        background: #e0e0e0;
        border-radius: 20px;
        overflow: hidden;
    }
    .score-fill {
        height: 100%;
        background: linear-gradient(90deg, #ff6b6b 0%, #ffd93d 50%, #6bcf7f 100%);
        transition: width 0.5s ease;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 15px;
        color: white;
        font-weight: bold;
        font-size: 1.2em;
    }
    .loading {
        text-align: center;
        padding: 60px;
        color: #666;
    }
    '''
    
    extra_scripts = '''
    function updateData() {
        fetch('/api/latest')
            .then(response => response.json())
            .then(data => {
                // Update page content
            });
    }
    updateData();
    setInterval(updateData, 5000);
    '''
    
    page_content = '''
    <div class="container">
        ''' + create_header("🌤️ Clear Sky Predictor", "Real-time sky analysis from ESP32-CAM") + '''
        ''' + NAV_BAR + '''
        
        <div class="card">
            <div id="content" class="loading">
                <p>Waiting for first image from ESP32</p>
            </div>
        </div>
    </div>
    '''
    
    return create_page(
        title="Sky Predictor - Live View",
        content=page_content,
        extra_styles=extra_styles,
        extra_scripts=extra_scripts
    )


def create_stats_template():
    """Create Statistics template using base components"""
    
    extra_styles = '''
    .stat-row {
        display: flex;
        justify-content: space-between;
        padding: 15px 0;
        border-bottom: 1px solid #e0e0e0;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { font-weight: 600; color: #333; }
    .stat-value { color: #667eea; font-size: 1.2em; }
    '''
    
    extra_scripts = '''
    fetch('/api/statistics')
        .then(response => response.json())
        .then(data => {
            let html = '<h2>Analysis Statistics</h2>';
            for (const [key, value] of Object.entries(data)) {
                const label = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                html += `
                    <div class="stat-row">
                        <span class="stat-label">${label}</span>
                        <span class="stat-value">${value}</span>
                    </div>
                `;
            }
            document.getElementById('stats').innerHTML = html;
        });
    '''
    
    page_content = '''
    <div class="container">
        ''' + create_header("📊 Statistics", "Overall system performance metrics") + '''
        ''' + NAV_BAR + '''
        
        <div class="card" id="stats">
            <h2>Loading statistics...</h2>
        </div>
    </div>
    '''
    
    return create_page(
        title="Sky Predictor - Statistics",
        content=page_content,
        extra_styles=extra_styles,
        extra_scripts=extra_scripts
    )


# ================================================================
# EXPORT ALL COMPONENTS
# ================================================================

__all__ = [
    'COMMON_STYLES',
    'NAV_BAR',
    'create_header',
    'create_page',
    'create_live_view_template',
    'create_stats_template'
]

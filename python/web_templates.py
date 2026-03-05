"""
Web Templates Module - REFACTORED
Minimal HTML using template_base components
"""

from template_base import wrap_page, create_header, NAV_BAR, LOADING_STYLES


# ================================================================
# LIVE VIEW TEMPLATE
# ================================================================

extra_styles_live = """
    .score-bar {
        width: 100%;
        height: 40px;
        background: #e0e0e0;
        border-radius: 20px;
        overflow: hidden;
        margin: 15px 0;
    }
    .score-fill {
        height: 100%;
        background: linear-gradient(90deg, #ff6b6b 0%, #ffd93d 50%, #6bcf7f 100%);
        transition: width 0.5s;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 15px;
        color: white;
        font-weight: bold;
        font-size: 1.2em;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    .stat-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stat-value {
        font-size: 2.2em;
        font-weight: bold;
        color: #667eea;
        margin: 10px 0;
    }
    .stat-label {
        color: #666;
        font-size: 0.9em;
        text-transform: uppercase;
    }
    .condition {
        font-size: 1.8em;
        padding: 20px;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        text-align: center;
        margin: 15px 0;
        font-weight: 600;
    }
""" + LOADING_STYLES

extra_scripts_live = """
    function updateData() {
        fetch('/api/latest')
            .then(r => r.json())
            .then(data => {
                if (!data.timestamp) return;
                
                const a = data.analysis || {};
                const b = a.brightness || {};
                const f = a.sky_features || a.features || {};
                
                document.getElementById('content').innerHTML = `
                    <img src="/image/latest?t=${Date.now()}" style="max-width:100%;border-radius:10px;">
                    <div class="condition">${a.sky_condition || a.summary || 'Analyzing...'}</div>
                    <h3>Clear Sky Score</h3>
                    <div class="score-bar">
                        <div class="score-fill" style="width:${a.clear_sky_score||0}%">${a.clear_sky_score||0}%</div>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-label">Brightness</div>
                            <div class="stat-value">${b.average?.toFixed(1)||'---'}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Blue Coverage</div>
                            <div class="stat-value">${f.blue_coverage?.toFixed(0)||'---'}%</div>
                        </div>
                    </div>
                    <div style="text-align:center;margin-top:20px;color:#999;font-size:0.9em;">
                        ${new Date().toLocaleTimeString()}
                    </div>
                `;
            });
    }
    updateData();
    setInterval(updateData, 5000);
"""

content_live = f"""
<div class="container">
    {create_header("🌤️ Clear Sky Predictor", "Real-time sky analysis from ESP32-CAM")}
    {NAV_BAR}
    <div class="card">
        <div id="content" class="loading">Waiting for first image...</div>
    </div>
</div>
"""

HTML_TEMPLATE = wrap_page("Sky Predictor - Live View", content_live, extra_styles_live, extra_scripts_live)


# ================================================================
# STATISTICS PAGE TEMPLATE
# ================================================================

extra_styles_stats = """
    .stat-row {
        display: flex;
        justify-content: space-between;
        padding: 15px 0;
        border-bottom: 1px solid #e0e0e0;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { font-weight: 600; color: #333; }
    .stat-value { color: #667eea; font-size: 1.2em; }
""" + LOADING_STYLES

extra_scripts_stats = """
    fetch('/api/statistics')
        .then(r => r.json())
        .then(data => {
            let html = '<h2>Analysis Statistics</h2>';
            for (const [key, value] of Object.entries(data)) {
                const label = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                html += `<div class="stat-row"><span class="stat-label">${label}</span>
                         <span class="stat-value">${value}</span></div>`;
            }
            document.getElementById('stats').innerHTML = html;
        });
"""

content_stats = f"""
<div class="container">
    {create_header("📊 Statistics", "Overall system performance")}
    {NAV_BAR}
    <div class="card" id="stats">
        <div class="loading">Loading...</div>
    </div>
</div>
"""

STATS_PAGE_TEMPLATE = wrap_page("Statistics - Sky Predictor", content_stats, extra_styles_stats, extra_scripts_stats)

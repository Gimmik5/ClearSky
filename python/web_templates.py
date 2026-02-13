"""
Web Template Module

Contains HTML templates for the web interface.
"""

from python_config import AUTO_REFRESH_INTERVAL, SHOW_DETAILED_STATS, SHOW_COVERAGE_STATS


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sky Predictor - Live View</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
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
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .image-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .image-container img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
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
        .score-section {
            margin: 20px 0;
        }
        .score-section h3 {
            margin-bottom: 10px;
            color: #333;
        }
        .score-bar {
            width: 100%;
            height: 40px;
            background: #e0e0e0;
            border-radius: 20px;
            overflow: hidden;
            position: relative;
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
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #dee2e6;
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
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
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .stat-description {
            color: #999;
            font-size: 0.85em;
            margin-top: 5px;
        }
        .timestamp {
            text-align: center;
            color: #666;
            margin-top: 20px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .loading {
            text-align: center;
            padding: 60px;
            color: #666;
        }
        .loading::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
        .stats-summary {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .stats-summary h4 {
            margin-bottom: 10px;
            color: #333;
        }
        .stats-summary .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }
        .stats-summary .stat-row:last-child {
            border-bottom: none;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌤️ Clear Sky Predictor</h1>
            <p>Real-time sky analysis from ESP32-CAM</p>
        </div>
        
        <div class="card">
            <div id="content" class="loading">
                <p>Waiting for first image from ESP32</p>
            </div>
        </div>
    </div>
    
    <script>
        const AUTO_REFRESH = ''' + str(AUTO_REFRESH_INTERVAL) + ''';
        const SHOW_DETAILED = ''' + str(SHOW_DETAILED_STATS).lower() + ''';
        const SHOW_COVERAGE = ''' + str(SHOW_COVERAGE_STATS).lower() + ''';
        
        function updateData() {
            fetch('/api/latest')
                .then(response => response.json())
                .then(data => {
                    if (!data.timestamp) {
                        return;
                    }
                    
                    const content = document.getElementById('content');
                    const analysis = data.analysis || {};
                    const brightness = analysis.brightness || {};
                    const color = analysis.color || {};
                    const features = analysis.features || {};
                    
                    let html = `
                        <div class="image-container">
                            <img src="/image/latest?t=${Date.now()}" alt="Latest capture">
                        </div>
                        
                        <div class="condition">
                            ${analysis.sky_condition || 'Analyzing...'}
                        </div>
                        
                        <div class="score-section">
                            <h3>Clear Sky Score</h3>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${analysis.clear_sky_score || 0}%">
                                    ${analysis.clear_sky_score || 0}%
                                </div>
                            </div>
                        </div>
                        
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-label">Brightness</div>
                                <div class="stat-value">${brightness.average?.toFixed(1) || '---'}</div>
                                <div class="stat-description">0-255 scale</div>
                            </div>
                    `;
                    
                    if (SHOW_COVERAGE && features.blue_coverage !== undefined) {
                        html += `
                            <div class="stat-card">
                                <div class="stat-label">Blue Sky</div>
                                <div class="stat-value">${features.blue_coverage?.toFixed(1) || '---'}%</div>
                                <div class="stat-description">Coverage</div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-label">Clouds</div>
                                <div class="stat-value">${features.gray_coverage?.toFixed(1) || '---'}%</div>
                                <div class="stat-description">Gray coverage</div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-label">Bright/White</div>
                                <div class="stat-value">${features.white_coverage?.toFixed(1) || '---'}%</div>
                                <div class="stat-description">White coverage</div>
                            </div>
                        `;
                    }
                    
                    if (SHOW_DETAILED && color.red !== undefined) {
                        html += `
                            <div class="stat-card">
                                <div class="stat-label">Color Variance</div>
                                <div class="stat-value">${color.color_variance?.toFixed(1) || '---'}</div>
                                <div class="stat-description">Lower = uniform</div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-label">RGB Values</div>
                                <div class="stat-value" style="font-size: 1.2em;">
                                    <span style="color: #e74c3c;">R:${color.red?.toFixed(0)}</span><br>
                                    <span style="color: #27ae60;">G:${color.green?.toFixed(0)}</span><br>
                                    <span style="color: #3498db;">B:${color.blue?.toFixed(0)}</span>
                                </div>
                            </div>
                        `;
                    }
                    
                    html += `
                        </div>
                        
                        <div class="timestamp">
                            Last updated: ${new Date().toLocaleString()}
                        </div>
                    `;
                    
                    content.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('content').innerHTML = `
                        <div class="error">
                            ⚠️ Error loading data: ${error.message}
                        </div>
                    `;
                });
        }
        
        // Update immediately
        updateData();
        
        // Auto-refresh
        setInterval(updateData, AUTO_REFRESH);
    </script>
</body>
</html>
'''


STATS_PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sky Predictor - Statistics</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* Reuse styles from main template */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .stat-row:last-child { border-bottom: none; }
        .stat-label { font-weight: 600; color: #333; }
        .stat-value { color: #667eea; font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Statistics</h1>
            <p><a href="/" style="color: white;">← Back to Live View</a></p>
        </div>
        
        <div class="card" id="stats">
            <h2>Loading statistics...</h2>
        </div>
    </div>
    
    <script>
        fetch('/api/statistics')
            .then(response => response.json())
            .then(data => {
                let html = '<h2>Analysis Statistics</h2>';
                for (const [key, value] of Object.entries(data)) {
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    html += `
                        <div class="stat-row">
                            <span class="stat-label">${label}</span>
                            <span class="stat-value">${value}</span>
                        </div>
                    `;
                }
                document.getElementById('stats').innerHTML = html;
            });
    </script>
</body>
</html>
'''

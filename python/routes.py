"""
Flask Routes Module - V1.1 PULL Mode with Daily View

All endpoints including gallery, daily view, file manager, and viewer
"""
from data_manager_sqlite import data_manager
from flask import request, render_template_string, jsonify, send_file
from datetime import datetime
import os
import traceback

from python_config import (
    ENABLE_BRIGHTNESS_ANALYSIS, ENABLE_COLOR_ANALYSIS, ENABLE_SKY_FEATURES,
    AUTO_REFRESH_INTERVAL, BRIGHTNESS_VERY_BRIGHT, BRIGHTNESS_BRIGHT,
    BRIGHTNESS_MODERATE, BRIGHTNESS_DIM, IMAGE_DIR
)

from web_templates import HTML_TEMPLATE, STATS_PAGE_TEMPLATE

# Import viewer components (with fallback if missing)
try:
    from image_viewer import (
        VIEWER_TEMPLATE, format_timestamp, score_to_color,
        get_date_folders, get_day_images, get_viewer_context,
        create_gallery_index, create_gallery_day
    )
    HAS_IMAGE_VIEWER = True
except ImportError:
    print("⚠ Warning: image_viewer.py not found - viewer/gallery disabled")
    print("   Copy from: outputs/python_v11_pull/image_viewer.py")
    HAS_IMAGE_VIEWER = False

# Import daily view (with fallback if missing)
try:
    from daily_view import DAILY_VIEW_TEMPLATE, get_daily_view_data
    HAS_DAILY_VIEW = True
except ImportError:
    print("⚠ Warning: daily_view.py not found - daily view disabled")
    print("   Copy from: outputs/python_v11_pull/daily_view.py")
    HAS_DAILY_VIEW = False


def register_routes(app):
    """Register all Flask routes to the app"""
    
    # ----------------------------------------------------------------
    # Register Jinja2 template filters
    # ----------------------------------------------------------------
    if HAS_IMAGE_VIEWER:
        @app.template_filter('format_ts')
        def _format_ts(ts):
            return format_timestamp(ts)

        @app.template_filter('score_color')
        def _score_color(score):
            return score_to_color(score)
    
    
    # ================================================================
    # MAIN PAGES
    # ================================================================
    
    @app.route('/')
    def index():
        """Main web interface"""
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/stats')
    def stats_page():
        """Statistics page"""
        return render_template_string(STATS_PAGE_TEMPLATE)
    
    @app.route('/gallery')
    def gallery_index():
        """Gallery index - shows list of dates"""
        if not HAS_IMAGE_VIEWER:
            return "Gallery unavailable - image_viewer.py missing", 500
        
        try:
            folders = get_date_folders(data_manager)
            return create_gallery_index(folders)
        except Exception as e:
            print(f"Error in gallery index: {e}")
            traceback.print_exc()
            return f"Gallery error: {e}", 500
    
    @app.route('/gallery/<date_key>')
    def gallery_day(date_key):
        """Gallery day view - shows all images for a specific date"""
        if not HAS_IMAGE_VIEWER:
            return "Gallery unavailable - image_viewer.py missing", 500
        
        try:
            day_data = get_day_images(data_manager, date_key)
            return create_gallery_day(day_data)
        except Exception as e:
            print(f"Error in gallery day view: {e}")
            traceback.print_exc()
            return f"Gallery day error: {e}", 500
    
    @app.route('/viewer/<timestamp>')
    def viewer(timestamp):
        """Full-screen viewer for a single capture"""
        if not HAS_IMAGE_VIEWER:
            return "Viewer unavailable - image_viewer.py missing", 500
        
        try:
            ctx = get_viewer_context(data_manager, timestamp)
            
            if ctx.get('error'):
                return f"Viewer error: {ctx['error']}", 404
            
            return render_template_string(VIEWER_TEMPLATE, **ctx)
        except Exception as e:
            print(f"Error in viewer for timestamp {timestamp}: {e}")
            traceback.print_exc()
            return f"Viewer error: {e}<br><br>Traceback:<br><pre>{traceback.format_exc()}</pre>", 500
    
    @app.route('/daily')
    def daily_view():
        """Daily view - images organized by day with statistics"""
        if not HAS_DAILY_VIEW:
            return "Daily view unavailable - daily_view.py missing", 500
        
        try:
            days_back = request.args.get('days', 30, type=int)
            days_data = get_daily_view_data(data_manager, days_back)
            
            return render_template_string(
                DAILY_VIEW_TEMPLATE,
                days=days_data
            )
        except Exception as e:
            print(f"Error in daily view: {e}")
            traceback.print_exc()
            return f"Daily view error: {e}", 500
    
    @app.route('/files')
    def file_manager():
        """File manager - browse all captured images on disk"""
        return render_template_string(FILE_MANAGER_TEMPLATE)
    
    # ================================================================
    # API ENDPOINTS
    # ================================================================
    
    @app.route('/api/latest')
    def get_latest():
        """Latest capture data"""
        try:
            latest = data_manager.get_latest()
            
            if not latest or not latest.get("timestamp"):
                return jsonify({
                    "timestamp": None,
                    "image_path": None,
                    "analysis": {}
                })
            
            return jsonify({
                "timestamp": latest.get("timestamp"),
                "image_path": latest.get("image_path"),
                "analysis": latest.get("analysis", {})
            })
        except Exception as e:
            print(f"Error in /api/latest: {e}")
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/history')
    def get_history():
        """Historical data"""
        try:
            limit = request.args.get('limit', type=int)
            history = data_manager.get_history(limit)
            return jsonify(history)
        except Exception as e:
            print(f"Error in /api/history: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/statistics')
    def get_statistics():
        """Statistics summary"""
        try:
            stats = data_manager.get_statistics()
            return jsonify(stats)
        except Exception as e:
            print(f"Error in /api/statistics: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/files/list')
    def list_files():
        """List all files in captured_images directory"""
        try:
            if not os.path.exists(IMAGE_DIR):
                return jsonify({"files": [], "total": 0})
            
            files = []
            total_size = 0
            
            for filename in sorted(os.listdir(IMAGE_DIR), reverse=True):
                if filename.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                    filepath = os.path.join(IMAGE_DIR, filename)
                    stat = os.stat(filepath)
                    
                    # Extract timestamp from filename (sky_YYYYMMDD_HHMMSS.jpg or sky_NORTS_*.jpg)
                    timestamp = filename.replace('sky_', '').replace('.jpg', '').replace('.JPG', '')
                    
                    files.append({
                        'filename': filename,
                        'timestamp': timestamp,
                        'size': stat.st_size,
                        'size_mb': round(stat.st_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                    total_size += stat.st_size
            
            return jsonify({
                'files': files,
                'total': len(files),
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            })
        
        except Exception as e:
            print(f"Error listing files: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/files/delete/<filename>', methods=['DELETE'])
    def delete_file(filename):
        """Delete a specific file"""
        try:
            # Security check
            if '/' in filename or '\\' in filename or '..' in filename:
                return jsonify({"error": "Invalid filename"}), 400
            
            filepath = os.path.join(IMAGE_DIR, filename)
            
            if not os.path.exists(filepath):
                return jsonify({"error": "File not found"}), 404
            
            os.remove(filepath)
            return jsonify({"success": True, "deleted": filename})
        
        except Exception as e:
            print(f"Error deleting file: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/config')
    def get_config():
        """Current configuration"""
        try:
            return jsonify({
                "brightness_analysis": ENABLE_BRIGHTNESS_ANALYSIS,
                "color_analysis": ENABLE_COLOR_ANALYSIS,
                "sky_features": ENABLE_SKY_FEATURES,
                "auto_refresh_interval": AUTO_REFRESH_INTERVAL,
                "thresholds": {
                    "very_bright": BRIGHTNESS_VERY_BRIGHT,
                    "bright": BRIGHTNESS_BRIGHT,
                    "moderate": BRIGHTNESS_MODERATE,
                    "dim": BRIGHTNESS_DIM
                }
            })
        except Exception as e:
            print(f"Error in /api/config: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/test')
    def test_endpoint():
        """Test endpoint"""
        return jsonify({
            "status": "ok",
            "message": "Server is running (V1.1 Pull Mode with Daily View)",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "gallery": HAS_IMAGE_VIEWER,
                "viewer": HAS_IMAGE_VIEWER,
                "daily_view": HAS_DAILY_VIEW
            }
        })
    
    # ================================================================
    # IMAGE SERVING
    # ================================================================
    
    @app.route('/image/latest')
    def get_latest_image():
        """Serve the latest captured image"""
        try:
            latest = data_manager.get_latest()
            image_path = latest.get("image_path")
            
            if image_path and os.path.exists(image_path):
                return send_file(image_path, mimetype='image/jpeg')
            
            return "No image available", 404
        except Exception as e:
            print(f"Error in /image/latest: {e}")
            return str(e), 500
    
    @app.route('/image/<timestamp>')
    def get_image_by_timestamp(timestamp):
        """
        Serve image by timestamp
        
        Supports multiple naming conventions:
        - Database image_path
        - Standard format: sky_YYYYMMDD_HHMMSS.jpg
        - NORTS format: sky_NORTS_*.jpg
        """
        try:
            # Try to get image_path from database
            from data_manager_sqlite import data_manager
            
            all_captures = data_manager.get_history(limit=None)
            for capture in all_captures:
                if capture.get('timestamp') == timestamp:
                    image_path = capture.get('image_path')
                    if image_path and os.path.exists(image_path):
                        return send_file(image_path, mimetype='image/jpeg')
                    break
            
            # Fallback: Try standard filename format
            possible_names = [
                f"sky_{timestamp}.jpg",
                f"sky_{timestamp}.JPG",
                f"{timestamp}.jpg",
                timestamp
            ]
            
            for filename in possible_names:
                filepath = os.path.join(IMAGE_DIR, filename)
                if os.path.exists(filepath):
                    return send_file(filepath, mimetype='image/jpeg')
            
            # If still not found, return 404
            return "Image not found", 404
            
        except Exception as e:
            print(f"Error serving image {timestamp}: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}", 500
    
    @app.route('/image/file/<filename>')
    def get_image_by_filename(filename):
        """Serve image by filename"""
        try:
            # Security check
            if '/' in filename or '\\' in filename or '..' in filename:
                return "Invalid filename", 400
            
            filepath = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(filepath):
                return send_file(filepath, mimetype='image/jpeg')
            
            return "File not found", 404
        except Exception as e:
            print(f"Error serving file: {e}")
            return str(e), 500
    
    # ================================================================
    # EXPORT
    # ================================================================
    
    @app.route('/export/csv')
    def export_csv():
        """Export data to CSV"""
        try:
            filename = f"sky_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = data_manager.export_csv(filename)
            
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True)
            else:
                return "Export failed", 500
        except Exception as e:
            print(f"Error in /export/csv: {e}")
            traceback.print_exc()
            return str(e), 500


# ================================================================
# FILE MANAGER TEMPLATE
# ================================================================

FILE_MANAGER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>File Manager - Sky Predictor</title>
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
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .stats-bar {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .stat-item {
            flex: 1;
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
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d4;
        }
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .file-table {
            width: 100%;
            border-collapse: collapse;
        }
        .file-table th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-size: 0.9em;
            color: #666;
        }
        .file-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 0.9em;
        }
        .file-table tbody tr:hover {
            background: #f8f9fa;
        }
        
        .file-thumb {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 8px;
            cursor: pointer;
        }
        .file-thumb:hover {
            opacity: 0.8;
        }
        
        .file-actions {
            display: flex;
            gap: 8px;
        }
        .action-btn {
            padding: 4px 10px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85em;
        }
        .action-btn:hover {
            background: #f0f0f0;
        }
        .action-btn.delete {
            color: #e74c3c;
            border-color: #e74c3c;
        }
        .action-btn.delete:hover {
            background: #ffebee;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            max-width: 90%;
            max-height: 90%;
        }
        .modal-close {
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5em;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📁 File Manager</h1>
        <p>Browse and manage captured images</p>
    </div>

    <div class="nav-bar">
        <a href="/" class="nav-btn">🏠 Live View</a>
        <a href="/gallery" class="nav-btn">🖼 Gallery</a>
        <a href="/stats" class="nav-btn">📊 Statistics</a>
        <a href="/files" class="nav-btn">📁 File Manager</a>
        <a href="/export/csv" class="nav-btn">⬇ Export CSV</a>
    </div>

    <div class="card">
        <div class="stats-bar" id="statsBar">
            <div class="stat-item">
                <div class="stat-value" id="totalFiles">-</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="totalSize">-</div>
                <div class="stat-label">Total Size (MB)</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="selectedCount">0</div>
                <div class="stat-label">Selected</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn btn-primary" onclick="selectAll()">Select All</button>
            <button class="btn btn-primary" onclick="selectNone()">Select None</button>
            <button class="btn btn-danger" onclick="deleteSelected()">Delete Selected</button>
            <button class="btn btn-primary" onclick="loadFiles()">🔄 Refresh</button>
        </div>

        <div id="fileList" class="loading">
            Loading files...
        </div>
    </div>
</div>

<div id="modal" class="modal" onclick="closeModal()">
    <button class="modal-close" onclick="closeModal()">×</button>
    <img id="modalImage" class="modal-content" onclick="event.stopPropagation()">
</div>

<script>
let allFiles = [];
let selectedFiles = new Set();

function loadFiles() {
    fetch('/api/files/list')
        .then(r => r.json())
        .then(data => {
            allFiles = data.files || [];
            selectedFiles.clear();
            
            document.getElementById('totalFiles').textContent = data.total || 0;
            document.getElementById('totalSize').textContent = data.total_size_mb || 0;
            document.getElementById('selectedCount').textContent = 0;
            
            renderFiles();
        })
        .catch(err => {
            document.getElementById('fileList').innerHTML = 
                '<p style="color:red;">Error loading files: ' + err + '</p>';
        });
}

function renderFiles() {
    const container = document.getElementById('fileList');
    
    if (allFiles.length === 0) {
        container.innerHTML = '<p style="text-align:center;padding:40px;color:#999;">No images found</p>';
        return;
    }
    
    let html = '<table class="file-table"><thead><tr>';
    html += '<th><input type="checkbox" onclick="toggleAll(this)"></th>';
    html += '<th>Thumbnail</th>';
    html += '<th>Filename</th>';
    html += '<th>Timestamp</th>';
    html += '<th>Size</th>';
    html += '<th>Modified</th>';
    html += '<th>Actions</th>';
    html += '</tr></thead><tbody>';
    
    allFiles.forEach(file => {
        const checked = selectedFiles.has(file.filename) ? 'checked' : '';
        html += `<tr>
            <td><input type="checkbox" ${checked} onchange="toggleFile('${file.filename}', this.checked)"></td>
            <td><img src="/image/file/${file.filename}" class="file-thumb" 
                     onclick="showModal('/image/file/${file.filename}')"></td>
            <td>${file.filename}</td>
            <td>${file.timestamp}</td>
            <td>${file.size_mb} MB</td>
            <td>${file.modified}</td>
            <td class="file-actions">
                <button class="action-btn" onclick="window.open('/image/file/${file.filename}')">View</button>
                <button class="action-btn delete" onclick="deleteFile('${file.filename}')">Delete</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function toggleFile(filename, checked) {
    if (checked) {
        selectedFiles.add(filename);
    } else {
        selectedFiles.delete(filename);
    }
    document.getElementById('selectedCount').textContent = selectedFiles.size;
}

function toggleAll(checkbox) {
    if (checkbox.checked) {
        selectAll();
    } else {
        selectNone();
    }
}

function selectAll() {
    selectedFiles = new Set(allFiles.map(f => f.filename));
    renderFiles();
    document.getElementById('selectedCount').textContent = selectedFiles.size;
}

function selectNone() {
    selectedFiles.clear();
    renderFiles();
    document.getElementById('selectedCount').textContent = 0;
}

function deleteFile(filename) {
    if (!confirm(`Delete ${filename}?`)) return;
    
    fetch(`/api/files/delete/${filename}`, { method: 'DELETE' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                loadFiles();
            } else {
                alert('Delete failed: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(err => alert('Error: ' + err));
}

function deleteSelected() {
    if (selectedFiles.size === 0) {
        alert('No files selected');
        return;
    }
    
    if (!confirm(`Delete ${selectedFiles.size} file(s)?`)) return;
    
    let deleted = 0;
    selectedFiles.forEach(filename => {
        fetch(`/api/files/delete/${filename}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(data => {
                if (data.success) deleted++;
                if (deleted === selectedFiles.size) loadFiles();
            });
    });
}

function showModal(src) {
    document.getElementById('modalImage').src = src;
    document.getElementById('modal').classList.add('active');
}

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

// Load on page load
loadFiles();
</script>
</body>
</html>
'''

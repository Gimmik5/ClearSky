"""
Flask Routes Module - FIXED VERSION
All HTTP endpoints for the server
"""

from flask import request, render_template_string, jsonify, send_file
import cv2
import numpy as np
from datetime import datetime
import os
import traceback

# Import config first
from python_config import (
    MAX_IMAGE_SIZE_MB, ENABLE_LOGGING, LOG_LEVEL,
    ENABLE_BRIGHTNESS_ANALYSIS, ENABLE_COLOR_ANALYSIS, ENABLE_SKY_FEATURES,
    AUTO_REFRESH_INTERVAL, BRIGHTNESS_VERY_BRIGHT, BRIGHTNESS_BRIGHT,
    BRIGHTNESS_MODERATE, BRIGHTNESS_DIM
)

# Import templates
from web_templates import HTML_TEMPLATE, STATS_PAGE_TEMPLATE


def register_routes(app):
    """Register all Flask routes to the app"""
    
    # Import here to avoid circular dependencies
    from analysis_core import analyze_image, get_analysis_summary
    from data_manager_sqlite import data_manager  # NEW: Using SQLite version
    from image_storage import save_image
    
    @app.route('/upload', methods=['POST'])
    def upload_image():
        """Receive image from ESP32 and analyze it"""
        try:
            # Debug logging
            print(f"\n{'='*60}")
            print(f"Upload request from {request.remote_addr}")
            print(f"Content-Type: {request.content_type}")
            print(f"Content-Length: {request.content_length}")
            print(f"{'='*60}\n")
            
            # Get image data - read exact Content-Length to prevent hanging
            content_length = request.content_length
            if content_length is None or content_length == 0:
                error_msg = "Missing or zero Content-Length header"
                print(f"ERROR: {error_msg}")
                return error_msg, 400
            
            print(f"Reading {content_length} bytes from stream...")
            image_data = request.stream.read(content_length)
            print(f"Successfully read {len(image_data)} bytes")
            
            # Check if data exists
            if not image_data or len(image_data) == 0:
                error_msg = "No image data received in request body"
                print(f"ERROR: {error_msg}")
                return error_msg, 400
            
            print(f"Received {len(image_data)} bytes")
            
            # Validate image size
            if len(image_data) > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                return f"Image too large (max {MAX_IMAGE_SIZE_MB}MB)", 413
            
            # Convert to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                print(f"ERROR: cv2.imdecode failed - invalid JPEG data")
                return "Invalid image", 400
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save image
            image_path = save_image(image, timestamp)
            
            # Perform analysis
            analysis_results = analyze_image(image)
            
            # Update data manager
            data_manager.update_latest(timestamp, image_path, analysis_results)
            data_manager.save_data()
            
            # Log to console
            if ENABLE_LOGGING:
                print(f"\n[{timestamp}] Image received and analyzed")
                print(get_analysis_summary(analysis_results))
                print()
            
            # Return analysis results to ESP32
            response = f"""
âœ“ Image analyzed successfully
{get_analysis_summary(analysis_results)}
"""
            
            return response, 200
            
        except Exception as e:
            error_msg = f"Error processing image: {str(e)}"
            print(error_msg)
            
            if ENABLE_LOGGING and LOG_LEVEL == "DEBUG":
                traceback.print_exc()
            
            return error_msg, 500
    
    
    @app.route('/')
    def index():
        """Main web interface"""
        return render_template_string(HTML_TEMPLATE)
    
    
    @app.route('/stats')
    def stats_page():
        """Statistics page"""
        return render_template_string(STATS_PAGE_TEMPLATE)
    
    
    @app.route('/api/latest')
    def get_latest():
        """API endpoint for latest data"""
        try:
            latest = data_manager.get_latest()
            
            # Handle case where no data exists yet
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
        """API endpoint for historical data"""
        try:
            limit = request.args.get('limit', type=int)
            history = data_manager.get_history(limit)
            return jsonify(history)
        except Exception as e:
            print(f"Error in /api/history: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/api/statistics')
    def get_statistics():
        """API endpoint for statistics"""
        try:
            stats = data_manager.get_statistics()
            return jsonify(stats)
        except Exception as e:
            print(f"Error in /api/statistics: {e}")
            return jsonify({"error": str(e)}), 500
    
    
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
    
    
    @app.route('/export/csv')
    def export_csv():
        """Export data to CSV"""
        try:
            filename = f"sky_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            data_manager.export_csv(filename)
            return send_file(filename, as_attachment=True)
        except Exception as e:
            print(f"Error in /export/csv: {e}")
            return str(e), 500
    
    
    @app.route('/api/config')
    def get_config():
        """Get current configuration"""
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
        """Test endpoint to verify server is working"""
        return jsonify({
            "status": "ok",
            "message": "Server is running",
            "timestamp": datetime.now().isoformat()
        })

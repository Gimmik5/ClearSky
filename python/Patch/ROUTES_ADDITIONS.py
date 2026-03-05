# ROUTES.PY - REQUIRED CHANGES
# Add these new routes and modify existing gallery route

"""
STEP 1: Update imports at the top of routes.py
Find the image_viewer imports section and UPDATE IT:
"""

# OLD imports:
from image_viewer import (
    GALLERY_TEMPLATE, VIEWER_TEMPLATE,
    format_timestamp, score_to_color,
    get_paginated_captures, get_viewer_context
)

# NEW imports (REPLACE the above with this):
from image_viewer import (
    VIEWER_TEMPLATE, format_timestamp, score_to_color,
    get_date_folders, get_day_images, get_viewer_context,
    create_gallery_index, create_gallery_day
)


"""
STEP 2: REPLACE the existing @app.route('/gallery') function
Find the gallery route (around line 80-105) and REPLACE IT ENTIRELY:
"""

# DELETE the old gallery route and REPLACE with these TWO routes:

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


"""
STEP 3: The viewer route stays the same (no changes needed)
The @app.route('/viewer/<timestamp>') function does NOT need to change.
"""


"""
==============================================================================
SUMMARY OF CHANGES:
==============================================================================

1. IMPORTS: Updated to use new functions from image_viewer.py
2. GALLERY ROUTE: Replaced single /gallery route with TWO routes:
   - /gallery → shows date folders
   - /gallery/<date> → shows images for that date
3. VIEWER ROUTE: No changes (stays the same)

==============================================================================
COMPLETE CODE SNIPPET TO ADD/REPLACE:
==============================================================================
"""

# Copy this entire section into your routes.py:

"""
    # ================================================================
    # GALLERY ROUTES - Date folders and day views
    # ================================================================
    
    @app.route('/gallery')
    def gallery_index():
        '''Gallery index - shows list of dates as folders'''
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
        '''Gallery day view - shows all images for a specific date'''
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
        '''Full-screen viewer for a single capture'''
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
            return f"Viewer error: {e}", 500
"""


"""
==============================================================================
TESTING AFTER DEPLOYMENT:
==============================================================================

1. Test gallery index:
   http://localhost:5000/gallery
   Should show: List of date folders with stats

2. Test gallery day:
   http://localhost:5000/gallery/20260304
   Should show: All images for that date with summary stats at top

3. Test viewer:
   http://localhost:5000/viewer/20260304_143022
   Should show: Full-screen image with stats

==============================================================================
"""

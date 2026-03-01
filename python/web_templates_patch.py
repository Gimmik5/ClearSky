# web_templates.py — Gallery Nav Bar Patch
#
# Two changes to make:
#
# ─────────────────────────────────────────────────────────────────────
# CHANGE 1 — Add nav bar CSS
#
# Find this line (around line 179 in web_templates.py):
#         .error {
#             background: #ffebee;
#
# Paste the following CSS BEFORE that .error block:
# ─────────────────────────────────────────────────────────────────────

CSS_TO_ADD = """
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
"""

# ─────────────────────────────────────────────────────────────────────
# CHANGE 2 — Add the nav bar HTML
#
# Find this exact block in the HTML section of web_templates.py
# (around line 183–188):
#
#         <div class="header">
#             <h1>🌤️ Clear Sky Predictor</h1>
#             <p>Real-time sky analysis from ESP32-CAM</p>
#         </div>
#
# Replace it with:
# ─────────────────────────────────────────────────────────────────────

HTML_HEADER_REPLACEMENT = """
        <div class="header">
            <h1>🌤️ Clear Sky Predictor</h1>
            <p>Real-time sky analysis from ESP32-CAM</p>
        </div>

        <div class="nav-bar">
            <a href="/" class="nav-btn">🏠 Live View</a>
            <a href="/gallery" class="nav-btn">🖼 Gallery</a>
            <a href="/stats" class="nav-btn">📊 Statistics</a>
            <a href="/export/csv" class="nav-btn">⬇ Export CSV</a>
        </div>
"""

# ─────────────────────────────────────────────────────────────────────
# That's it — no other changes needed in web_templates.py.
# The /gallery and /viewer routes are already wired up in routes.py.
# ─────────────────────────────────────────────────────────────────────

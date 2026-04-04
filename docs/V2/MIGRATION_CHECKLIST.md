# ClearSky V2.0 - File Migration Checklist

## 📋 Migration Overview

This checklist maps every file from V1.x to its V2.0 location and tracks migration status.

---

## 🗂️ File Migration Map

### Configuration Files

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `python_config.py` | `config/settings.py` | ⬜ Not Started | Split into multiple config files |
| N/A | `config/database_config.py` | ⬜ Not Started | Extract DB settings from python_config.py |
| N/A | `config/hardware_config.py` | ⬜ Not Started | Extract ESP32 settings from python_config.py |
| N/A | `config/analysis_config.py` | ⬜ Not Started | Extract analysis thresholds |

**Migration Steps for Config:**
```python
# 1. Create config/settings.py with base settings
# 2. Add .env support using python-dotenv
# 3. Create specialized config modules
# 4. Update all imports: python_config → config.settings
# 5. Test import compatibility
```

---

### Database Layer

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `database_schema.py` | `data/schema.py` | ⬜ Not Started | Move as-is, update imports |
| `database_operations.py` | `data/operations.py` | ⬜ Not Started | Move as-is, update imports |
| `data_manager.py` | `data/manager.py` (deprecated) | ⬜ Not Started | Phase out for data_manager_sqlite |
| `data_manager_sqlite.py` | `data/manager.py` | ⬜ Not Started | Main data manager |
| `migrate_json_to_sqlite.py` | `data/migrations/migrate_json_to_sqlite.py` | ⬜ Not Started | Move to migrations folder |
| `image_storage.py` | `data/storage/image_storage.py` | ⬜ Not Started | Move to storage subfolder |
| N/A | `data/models.py` | ⬜ Not Started | NEW: Create SQLAlchemy ORM models |

**Migration Steps for Database:**
```python
# 1. Move files to data/ directory
# 2. Update imports in all files
# 3. Create data/__init__.py with convenience imports
# 4. Test database operations independently
# 5. Consider adding SQLAlchemy ORM layer
```

---

### Analysis Layer

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `analysis_core.py` | `analysis/core.py` | ⬜ Not Started | Core analysis logic |
| `brightness_analysis.py` | `analysis/brightness.py` | ⬜ Not Started | Brightness-specific analysis |
| `color_analysis.py` | `analysis/color.py` | ⬜ Not Started | Color-specific analysis |
| `sky_features.py` | `analysis/sky_features.py` | ⬜ Not Started | Sky feature detection |
| N/A | `analysis/ml/inference.py` | ⬜ Not Started | NEW: ML inference pipeline (future) |

**Migration Steps for Analysis:**
```python
# 1. Move files to analysis/ directory
# 2. Update imports
# 3. Create unified AnalysisPipeline class in core.py
# 4. Test each analysis module independently
# 5. Add unit tests for each module
```

---

### Hardware Layer

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `esp32_poller.py` | `hardware/poller.py` | ⬜ Not Started | Main ESP32 polling logic |
| N/A | `hardware/connection.py` | ⬜ Not Started | NEW: Extract connection management |
| N/A | `hardware/protocol.py` | ⬜ Not Started | NEW: Define communication protocol |

**Migration Steps for Hardware:**
```python
# 1. Move esp32_poller.py to hardware/poller.py
# 2. Extract connection logic to connection.py
# 3. Define protocol interface in protocol.py
# 4. Update imports in main.py
# 5. Add retry and error handling
```

---

### Web Layer

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `web_server.py` | `web/app.py` | ⬜ Not Started | Flask app factory |
| `routes.py` (lines 1-200) | `web/routes/main_routes.py` | ⬜ Not Started | Home, stats pages |
| `routes.py` (lines 201-400) | `web/routes/api_routes.py` | ⬜ Not Started | JSON API endpoints |
| `routes.py` (lines 401-600) | `web/routes/gallery_routes.py` | ⬜ Not Started | Gallery views |
| `routes.py` (lines 601-end) | `web/routes/viewer_routes.py` | ⬜ Not Started | Image viewer |
| `web_templates.py` | `web/templates/*.html` | ⬜ Not Started | Convert to template files |
| `template_base.py` | `web/templates/base.html` | ⬜ Not Started | Base template |
| `image_viewer.py` | `web/components/image_viewer.py` | ⬜ Not Started | Viewer component |
| `daily_view.py` | `web/components/daily_view.py` | ⬜ Not Started | Daily view component |

**Migration Steps for Web:**
```python
# 1. Split routes.py into 4 separate route modules
# 2. Convert inline templates to .html files
# 3. Create base.html with template inheritance
# 4. Extract CSS to web/static/css/
# 5. Extract JavaScript to web/static/js/
# 6. Move components to web/components/
# 7. Create Flask blueprints for each route group
# 8. Update app.py to register all blueprints
```

---

### Utilities

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `server_utils.py` | `utils/server_utils.py` | ⬜ Not Started | Banner, startup messages |
| `graceful_shutdown.py` | `utils/shutdown.py` | ⬜ Not Started | Signal handling |
| `queue_diagnostic.py` | `utils/diagnostics.py` | ⬜ Not Started | Diagnostic tools |
| N/A | `utils/logger.py` | ⬜ Not Started | NEW: Centralized logging |

**Migration Steps for Utilities:**
```python
# 1. Move files to utils/ directory
# 2. Rename graceful_shutdown.py to shutdown.py
# 3. Rename queue_diagnostic.py to diagnostics.py
# 4. Create logger.py for centralized logging
# 5. Update all imports
```

---

### Scripts

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `server_init.py` | `scripts/init_database.py` | ⬜ Not Started | Database initialization |
| `queue_diagnostic.py` | `scripts/diagnostic_queue.py` | ⬜ Not Started | Queue diagnostics |
| N/A | `scripts/export_data.py` | ⬜ Not Started | NEW: Data export utilities |

---

### Main Entry Point

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `main.py` | `main.py` | ⬜ Not Started | Update imports only |
| `main_verbose.py` | DELETE | ⬜ Not Started | Remove, use logging instead |

**Migration Steps for Main:**
```python
# 1. Update all imports to new locations
# 2. Test that main.py still runs
# 3. Delete main_verbose.py (use logging levels instead)
```

---

### Tests

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `test_imports.py` | `tests/test_imports.py` | ⬜ Not Started | Move to tests/ |
| N/A | `tests/test_analysis/*.py` | ⬜ Not Started | NEW: Create analysis tests |
| N/A | `tests/test_data/*.py` | ⬜ Not Started | NEW: Create data tests |
| N/A | `tests/test_hardware/*.py` | ⬜ Not Started | NEW: Create hardware tests |
| N/A | `tests/test_web/*.py` | ⬜ Not Started | NEW: Create web tests |

---

### Documentation

| V1 File | V2 Location | Status | Notes |
|---------|-------------|--------|-------|
| `MODULARIZATION_GUIDE.md` | `docs/ARCHITECTURE.md` | ⬜ Not Started | Expand and update |
| `TroubleshootingSteps.txt` | `docs/TROUBLESHOOTING.md` | ⬜ Not Started | Convert to markdown |
| N/A | `docs/API.md` | ⬜ Not Started | NEW: Document API endpoints |
| N/A | `docs/DEPLOYMENT.md` | ⬜ Not Started | NEW: Deployment guide |

---

## 🎯 Migration Priority Order

### Phase 1: Foundation (Do First)
- [ ] Create folder structure (run setup_v2_structure.sh)
- [ ] Set up Git branch
- [ ] Create .env file from .env.example
- [ ] Install new dependencies

### Phase 2: Configuration
- [ ] Migrate `python_config.py` → `config/settings.py`
- [ ] Add .env support
- [ ] Create specialized config modules
- [ ] Update imports in all files
- [ ] Test configuration loading

### Phase 3: Data Layer
- [ ] Migrate database modules to `data/`
- [ ] Move storage modules to `data/storage/`
- [ ] Move migrations to `data/migrations/`
- [ ] Update all database imports
- [ ] Test database operations

### Phase 4: Analysis Layer
- [ ] Migrate analysis modules to `analysis/`
- [ ] Create unified pipeline in `core.py`
- [ ] Update analysis imports
- [ ] Test each analysis module
- [ ] Add unit tests

### Phase 5: Hardware Layer
- [ ] Migrate `esp32_poller.py` → `hardware/poller.py`
- [ ] Extract connection logic
- [ ] Update hardware imports
- [ ] Test ESP32 polling
- [ ] Add error handling

### Phase 6: Web Layer (Most Complex)
- [ ] Create Flask app factory in `web/app.py`
- [ ] Split `routes.py` into blueprints
- [ ] Convert templates to files
- [ ] Extract CSS and JavaScript
- [ ] Move components to `web/components/`
- [ ] Test all routes
- [ ] Update frontend

### Phase 7: Utilities
- [ ] Migrate utility modules to `utils/`
- [ ] Create centralized logger
- [ ] Update utility imports
- [ ] Test utilities

### Phase 8: Main & Scripts
- [ ] Update `main.py` imports
- [ ] Move initialization to `scripts/`
- [ ] Test main entry point
- [ ] Remove deprecated files

### Phase 9: Testing & Documentation
- [ ] Add unit tests for all modules
- [ ] Add integration tests
- [ ] Update documentation
- [ ] Create deployment guide
- [ ] Final testing

---

## ✅ Completion Checklist

### Code Migration
- [ ] All files moved to new locations
- [ ] All imports updated
- [ ] No broken imports
- [ ] All modules importable
- [ ] Application runs successfully

### Testing
- [ ] Unit tests for config
- [ ] Unit tests for data layer
- [ ] Unit tests for analysis
- [ ] Unit tests for hardware
- [ ] Unit tests for web routes
- [ ] Integration tests
- [ ] All tests passing

### Documentation
- [ ] API documentation complete
- [ ] Architecture documented
- [ ] Deployment guide written
- [ ] Troubleshooting guide updated
- [ ] README updated
- [ ] Code comments added

### Quality Assurance
- [ ] Code formatted with Black
- [ ] Linting passed (flake8)
- [ ] Type hints added (mypy)
- [ ] No security vulnerabilities
- [ ] Performance acceptable
- [ ] Memory usage acceptable

### Deployment
- [ ] Production config created
- [ ] Environment variables documented
- [ ] Docker support added (optional)
- [ ] CI/CD pipeline configured (optional)
- [ ] Backup strategy documented

---

## 📊 Progress Tracking

| Module | Files | Status | % Complete | Notes |
|--------|-------|--------|------------|-------|
| Config | 4 | ⬜ Not Started | 0% | - |
| Data | 7 | ⬜ Not Started | 0% | - |
| Analysis | 5 | ⬜ Not Started | 0% | - |
| Hardware | 3 | ⬜ Not Started | 0% | - |
| Web | 9 | ⬜ Not Started | 0% | - |
| Utils | 4 | ⬜ Not Started | 0% | - |
| Scripts | 3 | ⬜ Not Started | 0% | - |
| Tests | 10 | ⬜ Not Started | 0% | - |
| Docs | 5 | ⬜ Not Started | 0% | - |
| **TOTAL** | **50** | ⬜ Not Started | **0%** | - |

**Legend:**
- ⬜ Not Started
- 🟡 In Progress
- ✅ Complete
- ❌ Blocked

---

## 🚨 Common Pitfalls to Avoid

1. **Don't migrate everything at once**
   - Migrate module by module
   - Test after each migration
   - Commit frequently

2. **Don't forget to update imports**
   - Every moved file needs import updates
   - Check for circular imports
   - Use absolute imports

3. **Don't skip testing**
   - Test each module independently
   - Test integration after each phase
   - Keep old code until new code is tested

4. **Don't ignore backwards compatibility**
   - Keep old entry points working temporarily
   - Add deprecation warnings
   - Give yourself time to migrate

5. **Don't forget documentation**
   - Update as you go
   - Document breaking changes
   - Keep a migration log

---

## 📝 Migration Log Template

Use this template to track your daily progress:

```
## Migration Log - [DATE]

### Completed Today
- [ ] Item 1
- [ ] Item 2

### Issues Encountered
- Issue 1: Description and resolution
- Issue 2: Description and resolution

### Next Steps
- [ ] Next task 1
- [ ] Next task 2

### Notes
- Any additional notes or observations
```

---

## 🎓 Resources

- [Python Import System](https://docs.python.org/3/reference/import.html)
- [Flask Blueprints](https://flask.palletsprojects.com/en/2.3.x/blueprints/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/14/orm/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)

---

**Good luck with your migration! Take it step by step, and don't hesitate to pause and refactor if you discover a better approach.**

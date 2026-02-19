# Main.py Refactoring - Modularization Guide

## Overview
The original `main.py` has been refactored to separate concerns into dedicated modules, making the code more maintainable, testable, and reusable.

## New Module Structure

### 1. **esp32_poller.py**
**Purpose**: Handles all ESP32 communication and image polling logic

**Key Features**:
- `ESP32Poller` class - encapsulates all polling behavior
- `check_esp32_reachable()` - verifies ESP32 connectivity
- `fetch_and_process_image()` - retrieves, decodes, and analyzes images
- `print_stats()` - displays polling statistics
- `run()` - main polling loop

**Benefits**:
- Easier to test individual polling operations
- Can instantiate multiple pollers if needed
- Cleaner error handling and state management
- Stats tracking is more organized

### 2. **graceful_shutdown.py**
**Purpose**: Handles signal handling and graceful server shutdown

**Key Features**:
- `register_signal_handlers()` - sets up Ctrl+C handler
- `signal_handler()` - responds to SIGINT signals
- `print_shutdown_message()` - displays shutdown confirmation

**Benefits**:
- Signal handling logic is isolated
- Easy to add additional signal handlers (e.g., SIGTERM)
- Can be reused in other applications
- Cleaner separation of concerns

### 3. **server_init.py**
**Purpose**: Manages server initialization and database setup

**Key Features**:
- `initialize_database()` - creates database schema
- `check_and_notify_migration()` - handles data migration prompts
- `initialize_server()` - orchestrates all init steps

**Benefits**:
- Database setup is isolated and testable
- Easy to add additional initialization steps
- Clear separation from server startup

### 4. **web_server.py**
**Purpose**: Handles Flask app creation and Waitress server configuration

**Key Features**:
- `create_flask_app()` - sets up Flask with CORS and routes
- `start_web_server()` - starts Waitress with proper config

**Benefits**:
- Flask configuration is centralized
- Easy to adjust server settings (threads, timeouts, etc.)
- Web server logic is independent from polling

### 5. **main.py (Refactored)**
**Purpose**: Clean orchestrator that brings all modules together

**Changes**:
- Reduced from ~180 lines to ~55 lines
- Much clearer flow and dependencies
- Easy to understand the overall architecture
- Simple entry point

## Usage

The refactored version works exactly like the original:

```bash
python main.py
```

## Migration Path

To use the refactored version:

1. Replace the old `main.py` with the new one
2. Add the four new modules to your project:
   - `esp32_poller.py`
   - `graceful_shutdown.py`
   - `server_init.py`
   - `web_server.py`

3. No changes needed to other files - all imports and configurations remain the same

## Testing Individual Components

With this modular structure, you can now test components independently:

```python
# Test ESP32 poller without running the server
from esp32_poller import ESP32Poller

poller = ESP32Poller("192.168.1.104", 80, 10, 15)
poller.check_esp32_reachable()
success = poller.fetch_and_process_image()

# Test Flask app without starting the server
from web_server import create_flask_app

app = create_flask_app()
with app.test_client() as client:
    response = client.get('/api/latest')
    assert response.status_code == 200
```

## Future Enhancements

This modular structure makes it easy to add:
- Multiple ESP32 devices (instantiate multiple `ESP32Poller` objects)
- Alternative polling strategies (subclass `ESP32Poller`)
- Async polling (convert `run()` to async)
- Healthchecks and monitoring (add methods to poller)
- Configuration file support (load into modules)

## Benefits Summary

✓ **Separation of Concerns** - Each module has a single responsibility
✓ **Testability** - Components can be tested independently
✓ **Reusability** - Modules can be used in other projects
✓ **Maintainability** - Changes are localized to relevant modules
✓ **Readability** - Main entry point is clear and concise
✓ **Scalability** - Easy to add features or new devices

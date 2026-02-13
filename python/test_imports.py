"""
Test script to verify all modules import correctly
Run this before starting the server to check for import errors
"""

print("Testing Python module imports...")
print("-" * 50)

try:
    print("1. Importing python_config...", end=" ")
    import python_config
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("2. Importing web_templates...", end=" ")
    import web_templates
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("3. Importing server_utils...", end=" ")
    import server_utils
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("4. Importing brightness_analysis...", end=" ")
    import brightness_analysis
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("5. Importing color_analysis...", end=" ")
    import color_analysis
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("6. Importing sky_features...", end=" ")
    import sky_features
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("7. Importing analysis_core...", end=" ")
    import analysis_core
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("8. Importing image_storage...", end=" ")
    import image_storage
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("9. Importing database_schema...", end=" ")
    import database_schema
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("10. Importing database_operations...", end=" ")
    import database_operations
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("11. Importing data_manager_sqlite...", end=" ")
    import data_manager_sqlite
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("12. Importing migrate_json_to_sqlite...", end=" ")
    import migrate_json_to_sqlite
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("13. Importing routes...", end=" ")
    import routes
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

try:
    print("14. Importing main...", end=" ")
    import main
    print("✓")
except Exception as e:
    print(f"✗ FAILED: {e}")
    exit(1)

print("-" * 50)
print("✓ All imports successful!")
print("\nDatabase modules included:")
print("  - database_schema.py")
print("  - database_operations.py") 
print("  - data_manager_sqlite.py")
print("  - migrate_json_to_sqlite.py")
print("\nYou can now run: python main.py")

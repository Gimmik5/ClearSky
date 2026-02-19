"""
Server Initialization Module
Handles database setup and data migration checks
"""

from database_schema import create_database
from migrate_json_to_sqlite import check_migration_needed


def initialize_database():
    """Initialize the database schema"""
    print("Initializing database...")
    create_database()


def check_and_notify_migration():
    """Check if data migration is needed and notify user"""
    if check_migration_needed():
        print("\nWarning: Old JSON data detected!")
        print("   Run 'python migrate_json_to_sqlite.py' to migrate\n")


def initialize_server():
    """Run all server initialization steps"""
    initialize_database()
    check_and_notify_migration()

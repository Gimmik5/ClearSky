"""
Server Initialization Module
Handles database setup and data migration checks
"""

from database_schema import create_database


def initialize_database():
    """Initialize the database schema"""
    print("Initializing database...")
    create_database()


def initialize_server():
    """Run all server initialization steps"""
    initialize_database()

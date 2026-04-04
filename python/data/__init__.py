"""
data/__init__.py
Exposes the data manager as the main public API for this package.
"""
from data.manager import data_manager
from data.schema import create_database

__all__ = ['data_manager', 'create_database']
"""
Smart Mart — Configuration Module (MySQL)
===========================================
Centralized application settings.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'smartmart-dev-key-2026')

    # MySQL Connection
    DB_HOST     = os.environ.get('DB_HOST', 'localhost')
    DB_PORT     = int(os.environ.get('DB_PORT', 3306))
    DB_USER     = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
    DB_NAME     = os.environ.get('DB_NAME', 'smartmart')

    # Schema file location
    SCHEMA_FILE = os.path.join(BASE_DIR, 'database', 'schema.sql')


class ProductionConfig(Config):
    """Production overrides."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing overrides."""
    TESTING = True
    DB_NAME = 'smartmart_test'

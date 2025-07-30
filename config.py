import os
from datetime import timedelta

class Config:
    """Application configuration class"""
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or '24f2003480'
    
    # Database configuration - SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///parking_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Admin default credentials (change in production)
    ADMIN_USERNAME = 'aakash'
    ADMIN_PASSWORD = '24f2003480'
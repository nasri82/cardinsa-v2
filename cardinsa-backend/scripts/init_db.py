# scripts/init_db.py
"""
Database initialization script
Run with: python scripts/init_db.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.config.database import Base
from app.config.settings import get_settings
from app.models import *  # Import all models

def create_database():
    """Create all database tables"""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_database()
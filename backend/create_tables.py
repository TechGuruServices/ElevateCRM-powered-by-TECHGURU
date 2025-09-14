#!/usr/bin/env python3
"""
Database migration script for SQLite
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models import *
from app.core.database import Base

def create_tables():
    """Create all tables using SQLAlchemy"""
    try:
        # Use sync URL for table creation
        url = settings.DATABASE_URL_SYNC
        print(f"Creating database with URL: {url}")
        
        engine = create_engine(url, echo=True)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            print(f"Created tables: {tables}")
            
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)

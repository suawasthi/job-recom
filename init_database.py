#!/usr/bin/env python3
"""
Database initialization script
This script creates all the required database tables
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import create_tables, engine
from app.models import user, job, resume  # Import all models to register them

def init_database():
    """Initialize the database by creating all tables"""
    print("🚀 Initializing database...")
    
    try:
        # Create all tables
        create_tables()
        print("✅ Database tables created successfully!")
        
        # Test the connection
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            print(f"📋 Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🗄️  AI Job Platform Database Initialization")
    print("=" * 50)
    
    success = init_database()
    
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("You can now start the server with: python run.py")
    else:
        print("\n💥 Database initialization failed!")
        sys.exit(1)

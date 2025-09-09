#!/usr/bin/env python3
"""
Initialize ML Preferences Database

This script creates the necessary database tables for the ML preferences system.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from models.database import create_tables, engine
from models.ml_models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_ml_database():
    """Initialize ML preferences database tables"""
    try:
        logger.info("Creating ML preferences database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("ML preferences database tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        ml_tables = [table for table in tables if table.startswith('user_ml') or table.startswith('user_weight') or table.startswith('user_feedback')]
        
        logger.info(f"Created ML tables: {ml_tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating ML database tables: {e}")
        return False

if __name__ == "__main__":
    success = init_ml_database()
    if success:
        print("ML preferences database initialized successfully!")
    else:
        print("Failed to initialize ML preferences database!")
        sys.exit(1)


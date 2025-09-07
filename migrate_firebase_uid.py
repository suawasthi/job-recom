#!/usr/bin/env python3
"""
Migration script to add firebase_uid column to users table
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import engine
from sqlalchemy import text

def migrate_firebase_uid():
    """Add firebase_uid column to users table"""
    print("🚀 Starting Firebase UID migration...")
    
    try:
        with engine.connect() as connection:
            # Check if firebase_uid column already exists
            result = connection.execute(text("PRAGMA table_info(users);"))
            columns = [row[1] for row in result]
            
            if 'firebase_uid' in columns:
                print("✅ firebase_uid column already exists!")
                return True
            
            # Add firebase_uid column (without UNIQUE constraint initially)
            print("📝 Adding firebase_uid column to users table...")
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN firebase_uid VARCHAR;
            """))
            
            # Create index for firebase_uid
            print("📝 Creating index for firebase_uid...")
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_firebase_uid 
                ON users (firebase_uid);
            """))
            
            connection.commit()
            print("✅ Firebase UID migration completed successfully!")
            
            # Verify the migration
            result = connection.execute(text("PRAGMA table_info(users);"))
            columns = [row[1] for row in result]
            print(f"📋 Current columns in users table: {', '.join(columns)}")
            
    except Exception as e:
        print(f"❌ Error during Firebase UID migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🗄️  Firebase UID Migration")
    print("=" * 50)
    
    success = migrate_firebase_uid()
    
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)

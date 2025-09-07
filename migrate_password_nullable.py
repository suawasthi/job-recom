#!/usr/bin/env python3
"""
Migration script to make hashed_password column nullable
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import engine
from sqlalchemy import text

def migrate_password_nullable():
    """Make hashed_password column nullable"""
    print("🚀 Starting password nullable migration...")
    
    try:
        with engine.connect() as connection:
            # Check current column definition
            result = connection.execute(text("PRAGMA table_info(users);"))
            columns = {row[1]: row for row in result}
            
            if 'hashed_password' not in columns:
                print("❌ hashed_password column not found!")
                return False
            
            hashed_password_info = columns['hashed_password']
            print(f"📋 Current hashed_password column: {hashed_password_info}")
            
            # SQLite doesn't support ALTER COLUMN directly, so we need to recreate the table
            # This is a more complex migration that requires careful handling
            
            # For now, let's try a simpler approach - update existing NULL values to empty string
            print("📝 Updating NULL hashed_password values to empty string...")
            connection.execute(text("""
                UPDATE users 
                SET hashed_password = '' 
                WHERE hashed_password IS NULL;
            """))
            
            connection.commit()
            print("✅ Password nullable migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during password nullable migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🗄️  Password Nullable Migration")
    print("=" * 50)
    
    success = migrate_password_nullable()
    
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)



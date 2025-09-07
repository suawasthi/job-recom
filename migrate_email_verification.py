#!/usr/bin/env python3
"""
Migration script to add email_verified column to existing users
Run this script after updating the User model
"""

import sqlite3
import os
from pathlib import Path

def migrate_email_verification():
    """Add email_verified column to users table"""
    
    # Get the database path
    db_path = Path(__file__).parent / "test.db"
    
    if not db_path.exists():
        print("Database file not found. Creating new database...")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if email_verified column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'email_verified' not in columns:
            print("Adding email_verified column to users table...")
            
            # Add the email_verified column with default value False
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN email_verified BOOLEAN DEFAULT FALSE
            """)
            
            # Update existing users to have email_verified = False
            cursor.execute("""
                UPDATE users 
                SET email_verified = FALSE 
                WHERE email_verified IS NULL
            """)
            
            conn.commit()
            print("✅ Successfully added email_verified column to users table")
        else:
            print("✅ email_verified column already exists in users table")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Total users in database: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE email_verified = TRUE")
        verified_count = cursor.fetchone()[0]
        print(f"📧 Verified users: {verified_count}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Migration error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting email verification migration...")
    migrate_email_verification()
    print("✅ Migration completed!")

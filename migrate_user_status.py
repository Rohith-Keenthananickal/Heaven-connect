#!/usr/bin/env python3
"""
Database Migration Script: Update User Status from Boolean to Enum

This script migrates the existing user status field from boolean to enum.
Run this script after updating your code to ensure database compatibility.
"""

import asyncio
import asyncmy
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "heaven_connect")


async def migrate_user_status():
    """Migrate user status field from boolean to enum"""
    
    # Database connection
    connection = None
    
    try:
        print("🔄 Starting User Status Migration...")
        print(f"📊 Database: {DB_NAME} on {DB_HOST}:{DB_PORT}")
        
        # Connect to database
        connection = await asyncmy.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        print("✅ Connected to database successfully")
        
        # Check if users table exists
        async with connection.cursor() as cursor:
            await cursor.execute("SHOW TABLES LIKE 'users'")
            result = await cursor.fetchone()
            
            if not result:
                print("❌ Users table not found. Please ensure the table exists.")
                return
        
        # Check current column type
        async with connection.cursor() as cursor:
            await cursor.execute("DESCRIBE users")
            columns = await cursor.fetchall()
            
            status_column = None
            for column in columns:
                if column[0] == 'status':
                    status_column = column
                    break
            
            if not status_column:
                print("❌ Status column not found in users table.")
                return
            
            current_type = status_column[1]
            print(f"📋 Current status column type: {current_type}")
            
            if 'enum' in current_type.lower():
                print("✅ Status column is already an enum. No migration needed.")
                return
        
        # Backup existing data
        print("💾 Backing up existing user data...")
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT id, status FROM users")
            users = await cursor.fetchall()
            
            print(f"📊 Found {len(users)} users to migrate")
            
            # Count current status values
            active_count = sum(1 for user in users if user[1] == 1)
            inactive_count = sum(1 for user in users if user[1] == 0)
            
            print(f"📈 Current status distribution:")
            print(f"   - Active (1): {active_count} users")
            print(f"   - Inactive (0): {inactive_count} users")
        
        # Create temporary column
        print("🔧 Creating temporary status column...")
        async with connection.cursor() as cursor:
            await cursor.execute("ALTER TABLE users ADD COLUMN status_new ENUM('ACTIVE', 'BLOCKED', 'DELETED') DEFAULT 'ACTIVE'")
            print("✅ Temporary column created")
        
        # Migrate data
        print("🔄 Migrating user status data...")
        async with connection.cursor() as cursor:
            # Update existing boolean values to enum
            await cursor.execute("UPDATE users SET status_new = 'ACTIVE' WHERE status = 1")
            await cursor.execute("UPDATE users SET status_new = 'BLOCKED' WHERE status = 0")
            
            # Verify migration
            await cursor.execute("SELECT COUNT(*) FROM users WHERE status_new = 'ACTIVE'")
            active_count_new = await cursor.fetchone()
            
            await cursor.execute("SELECT COUNT(*) FROM users WHERE status_new = 'BLOCKED'")
            blocked_count_new = await cursor.fetchone()
            
            print(f"✅ Migration completed:")
            print(f"   - ACTIVE: {active_count_new[0]} users")
            print(f"   - BLOCKED: {blocked_count_new[0]} users")
        
        # Drop old column and rename new column
        print("🔧 Updating table structure...")
        async with connection.cursor() as cursor:
            await cursor.execute("ALTER TABLE users DROP COLUMN status")
            await cursor.execute("ALTER TABLE users CHANGE status_new status ENUM('ACTIVE', 'BLOCKED', 'DELETED') NOT NULL DEFAULT 'ACTIVE'")
            print("✅ Table structure updated")
        
        # Verify final structure
        async with connection.cursor() as cursor:
            await cursor.execute("DESCRIBE users")
            columns = await cursor.fetchall()
            
            for column in columns:
                if column[0] == 'status':
                    print(f"✅ Final status column type: {column[1]}")
                    break
        
        print("🎉 User Status Migration Completed Successfully!")
        print("\n📋 Summary of changes:")
        print("   - Changed status field from BOOLEAN to ENUM('ACTIVE', 'BLOCKED', 'DELETED')")
        print("   - Migrated existing data: true → ACTIVE, false → BLOCKED")
        print("   - Set default value to 'ACTIVE'")
        print("   - Made the field NOT NULL")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print("🔧 Please check the error and try again.")
        
        # If migration failed, try to clean up
        if connection:
            try:
                async with connection.cursor() as cursor:
                    # Check if temporary column exists and remove it
                    await cursor.execute("SHOW COLUMNS FROM users LIKE 'status_new'")
                    if await cursor.fetchone():
                        print("🧹 Cleaning up temporary column...")
                        await cursor.execute("ALTER TABLE users DROP COLUMN status_new")
                        print("✅ Cleanup completed")
            except Exception as cleanup_error:
                print(f"⚠️  Cleanup failed: {str(cleanup_error)}")
        
    finally:
        if connection:
            await connection.close()
            print("🔌 Database connection closed")


async def rollback_migration():
    """Rollback the migration if needed"""
    
    connection = None
    
    try:
        print("🔄 Rolling back User Status Migration...")
        
        connection = await asyncmy.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        print("✅ Connected to database successfully")
        
        # Check current column type
        async with connection.cursor() as cursor:
            await cursor.execute("DESCRIBE users")
            columns = await cursor.fetchall()
            
            status_column = None
            for column in columns:
                if column[0] == 'status':
                    status_column = column
                    break
            
            if not status_column:
                print("❌ Status column not found.")
                return
            
            current_type = status_column[1]
            print(f"📋 Current status column type: {current_type}")
            
            if 'enum' not in current_type.lower():
                print("✅ Status column is not an enum. No rollback needed.")
                return
        
        # Create temporary boolean column
        print("🔧 Creating temporary boolean status column...")
        async with connection.cursor() as cursor:
            await cursor.execute("ALTER TABLE users ADD COLUMN status_old BOOLEAN DEFAULT TRUE")
            print("✅ Temporary column created")
        
        # Migrate data back
        print("🔄 Rolling back user status data...")
        async with connection.cursor() as cursor:
            await cursor.execute("UPDATE users SET status_old = TRUE WHERE status = 'ACTIVE'")
            await cursor.execute("UPDATE users SET status_old = FALSE WHERE status IN ('BLOCKED', 'DELETED')")
        
        # Drop enum column and rename boolean column
        print("🔧 Restoring table structure...")
        async with connection.cursor() as cursor:
            await cursor.execute("ALTER TABLE users DROP COLUMN status")
            await cursor.execute("ALTER TABLE users CHANGE status_old status BOOLEAN DEFAULT TRUE")
            print("✅ Table structure restored")
        
        print("✅ Rollback completed successfully!")
        
    except Exception as e:
        print(f"❌ Rollback failed: {str(e)}")
        
    finally:
        if connection:
            await connection.close()
            print("🔌 Database connection closed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        print("🔄 Running rollback...")
        asyncio.run(rollback_migration())
    else:
        print("🚀 Running migration...")
        asyncio.run(migrate_user_status())
        
        print("\n📖 Usage:")
        print("   python migrate_user_status.py          # Run migration")
        print("   python migrate_user_status.py --rollback  # Rollback migration")

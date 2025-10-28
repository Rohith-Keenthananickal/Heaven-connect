"""
Script to run a specific migration manually
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def add_verification_fields():
    """Add email_verified and phone_verified fields to users table"""
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if columns already exist
        try:
            result = connection.execute(text("SHOW COLUMNS FROM users LIKE 'email_verified'"))
            email_verified_exists = result.rowcount > 0
            
            result = connection.execute(text("SHOW COLUMNS FROM users LIKE 'phone_verified'"))
            phone_verified_exists = result.rowcount > 0
            
            # Add missing columns
            if not email_verified_exists:
                print("Adding email_verified column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT false"))
                connection.execute(text("CREATE INDEX idx_users_email_verified ON users (email_verified)"))
                print("SUCCESS: Added email_verified column and index")
            else:
                print("WARNING: email_verified column already exists")
                
            if not phone_verified_exists:
                print("Adding phone_verified column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN phone_verified BOOLEAN NOT NULL DEFAULT false"))
                connection.execute(text("CREATE INDEX idx_users_phone_verified ON users (phone_verified)"))
                print("SUCCESS: Added phone_verified column and index")
            else:
                print("WARNING: phone_verified column already exists")
                
            # Commit changes
            connection.commit()
            print("SUCCESS: Migration completed successfully!")
            
        except Exception as e:
            print(f"ERROR: Failed running migration: {e}")
            connection.rollback()
            return False
            
    return True

if __name__ == "__main__":
    success = add_verification_fields()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)

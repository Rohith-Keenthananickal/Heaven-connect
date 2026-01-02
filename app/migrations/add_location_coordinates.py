"""
Database migration script to add latitude and longitude columns to location table.

This script adds:
- latitude column (FLOAT, nullable)
- longitude column (FLOAT, nullable)

Run this to enable ATP auto-allocation functionality.
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/heaven_connect")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def add_location_coordinates():
    """Add latitude and longitude columns to location table."""
    
    with engine.connect() as connection:
        # Check if columns already exist
        inspector = inspect(engine)
        location_columns = [col['name'] for col in inspector.get_columns('location')]
        
        has_latitude = 'latitude' in location_columns
        has_longitude = 'longitude' in location_columns
        
        if has_latitude and has_longitude:
            print("latitude and longitude columns already exist in location table.")
            return
        
        # Add latitude column if it doesn't exist
        if not has_latitude:
            connection.execute(text("""
                ALTER TABLE location 
                ADD COLUMN latitude FLOAT NULL 
                COMMENT 'Latitude coordinate of the property location'
            """))
            print("Added latitude column to location table.")
        
        # Add longitude column if it doesn't exist
        if not has_longitude:
            connection.execute(text("""
                ALTER TABLE location 
                ADD COLUMN longitude FLOAT NULL 
                COMMENT 'Longitude coordinate of the property location'
            """))
            print("Added longitude column to location table.")
        
        connection.commit()
        print("Migration completed successfully!")


def remove_location_coordinates():
    """Remove latitude and longitude columns from location table (use with caution!)."""
    
    with engine.connect() as connection:
        # Check if columns exist
        inspector = inspect(engine)
        location_columns = [col['name'] for col in inspector.get_columns('location')]
        
        if 'latitude' in location_columns:
            connection.execute(text("ALTER TABLE location DROP COLUMN latitude"))
            print("Removed latitude column from location table.")
        
        if 'longitude' in location_columns:
            connection.execute(text("ALTER TABLE location DROP COLUMN longitude"))
            print("Removed longitude column from location table.")
        
        connection.commit()
        print("Rollback completed successfully!")


if __name__ == "__main__":
    print("Adding latitude and longitude columns to location table...")
    add_location_coordinates()
    print("\nMigration completed!")
    print("\nYou can now:")
    print("1. Update existing location records with coordinates")
    print("2. Test the ATP auto-allocation API")


"""
Migration script to add application_number field to area_coordinators table
Run this script to add the application_number field to the area_coordinators table
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


async def add_application_number_field():
    """Add application_number field to area_coordinators table"""
    
    # SQL statement to add application_number field
    add_application_number_sql = """
    ALTER TABLE area_coordinators 
    ADD COLUMN application_number VARCHAR(50) NULL COMMENT 'Application number for the coordinator',
    ADD INDEX idx_application_number (application_number);
    """
    
    try:
        async with engine.begin() as conn:
            # Add the application_number field
            await conn.execute(text(add_application_number_sql))
            print("[SUCCESS] Application number field added to area_coordinators table")
            
            # Verify the changes
            result = await conn.execute(text("""
                DESCRIBE area_coordinators application_number;
            """))
            
            record = result.fetchone()
            if record:
                print(f"[SUCCESS] Field details: {record}")
            else:
                print("[ERROR] Failed to verify field addition")
                
    except Exception as e:
        print(f"[ERROR] Error adding application_number field: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(add_application_number_field())

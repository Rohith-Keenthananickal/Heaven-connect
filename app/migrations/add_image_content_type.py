"""
Migration script to add IMAGE content type to training_contents table
Run this script to add the IMAGE enum value to the content_type column
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


async def add_image_content_type():
    """Add IMAGE content type to the training_contents table"""
    
    # SQL statement to modify the ENUM to include IMAGE
    alter_enum_sql = """
    ALTER TABLE training_contents 
    MODIFY COLUMN content_type ENUM('TEXT', 'VIDEO', 'DOCUMENT', 'QUIZ', 'IMAGE') NOT NULL;
    """
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text(alter_enum_sql))
            print("✅ IMAGE content type added successfully to training_contents table!")
            
    except Exception as e:
        print(f"❌ Error adding IMAGE content type: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(add_image_content_type())

"""
Migration script to make created_by column nullable in training_modules table
Run this script to allow NULL values for created_by column
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


async def make_created_by_nullable():
    """Make created_by column nullable in training_modules table"""
    
    # SQL statement to modify the created_by column to allow NULL
    alter_column_sql = """
    ALTER TABLE training_modules 
    MODIFY COLUMN created_by INT NULL COMMENT 'Admin who created this module';
    """
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text(alter_column_sql))
            print("✅ created_by column made nullable successfully in training_modules table!")
            
    except Exception as e:
        print(f"❌ Error making created_by nullable: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(make_created_by_nullable())

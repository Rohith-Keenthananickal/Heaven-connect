"""
Script to check the schema of the area_coordinators table
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


async def check_table_schema():
    """Check the schema of the area_coordinators table"""
    
    try:
        async with engine.connect() as conn:
            # Check the schema of the area_coordinators table
            result = await conn.execute(text("DESCRIBE area_coordinators"))
            
            print("Area Coordinators Table Schema:")
            print("-" * 80)
            for row in result.fetchall():
                print(row)
            print("-" * 80)
                
    except Exception as e:
        print(f"[ERROR] Error checking schema: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(check_table_schema())

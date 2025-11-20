"""
Migration script to add issue_code field to issues table
Run this script to add the issue_code field to the issues table
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.database import engine


async def add_issue_code_field():
    """Add issue_code field to issues table"""
    
    # SQL statement to add issue_code field
    add_issue_code_sql = """
    ALTER TABLE issues 
    ADD COLUMN issue_code VARCHAR(20) NULL UNIQUE,
    ADD INDEX idx_issue_code (issue_code);
    """
    
    try:
        async with engine.begin() as conn:
            # Check if column already exists
            check_column_sql = """
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'issues'
            AND COLUMN_NAME = 'issue_code';
            """
            
            result = await conn.execute(text(check_column_sql))
            row = result.fetchone()
            
            if row and row[0] > 0:
                print("[INFO] issue_code column already exists in issues table")
                return
            
            # Add the issue_code field
            await conn.execute(text(add_issue_code_sql))
            print("[SUCCESS] issue_code field added to issues table")
            
            # Verify the changes
            verify_sql = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'issues'
            AND COLUMN_NAME = 'issue_code';
            """
            
            result = await conn.execute(text(verify_sql))
            record = result.fetchone()
            if record:
                print(f"[SUCCESS] Field details: {record}")
            else:
                print("[ERROR] Failed to verify field addition")
                
    except Exception as e:
        print(f"[ERROR] Error adding issue_code field: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(add_issue_code_field())


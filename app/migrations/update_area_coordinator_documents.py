"""
Migration script to update AreaCoordinator document fields
- Add pancard_images JSON array field
- Change id_proof_document from string to JSON array
Run this script to update the area_coordinators table schema
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.database import engine


async def update_area_coordinator_documents():
    """Update AreaCoordinator document fields to support arrays"""
    
    # SQL statements to modify the area_coordinators table
    migration_sql = """
    -- Add pancard_images JSON field
    ALTER TABLE area_coordinators 
    ADD COLUMN pancard_images JSON NULL COMMENT 'Array of URLs to PAN card images';
    
    -- Modify id_proof_document to JSON array
    -- First, we need to convert existing string values to JSON arrays
    UPDATE area_coordinators 
    SET id_proof_document = CASE 
        WHEN id_proof_document IS NOT NULL AND id_proof_document != '' 
        THEN JSON_ARRAY(id_proof_document)
        ELSE NULL 
    END;
    
    -- Change the column type to JSON
    ALTER TABLE area_coordinators 
    MODIFY COLUMN id_proof_document JSON NULL COMMENT 'Array of URLs to ID proof documents';
    """
    
    # Verification query
    verification_sql = """
    SELECT 
        id,
        id_proof_document,
        pancard_images,
        pancard_number
    FROM area_coordinators 
    ORDER BY id 
    LIMIT 5
    """
    
    try:
        async with engine.begin() as conn:
            # Execute the migration
            await conn.execute(text(migration_sql))
            print("[OK] AreaCoordinator document fields updated successfully")
            print("   - Added pancard_images JSON array field")
            print("   - Converted id_proof_document to JSON array")
            
            # Verify the changes
            result = await conn.execute(text(verification_sql))
            records = result.fetchall()
            
            if records:
                print("[OK] Sample records after migration:")
                for record in records:
                    print(f"   ID: {record[0]}")
                    print(f"   ID Proof Document: {record[1]}")
                    print(f"   PAN Card Images: {record[2]}")
                    print(f"   PAN Card Number: {record[3]}")
                    print("   ---")
            else:
                print("[INFO] No existing Area Coordinators found")
                
    except Exception as e:
        print(f"[ERROR] Error updating AreaCoordinator document fields: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(update_area_coordinator_documents())

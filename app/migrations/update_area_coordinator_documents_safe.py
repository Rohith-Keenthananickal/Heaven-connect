"""
Safe migration script to update AreaCoordinator document fields
- Add pancard_images JSON array field (if not exists)
- Change id_proof_document from string to JSON array
Run this script to update the area_coordinators table schema
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.database import engine


async def update_area_coordinator_documents_safe():
    """Safely update AreaCoordinator document fields to support arrays"""
    
    try:
        async with engine.begin() as conn:
            # Check if pancard_images column exists
            check_pancard_sql = """
            SELECT COUNT(*) as count 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'area_coordinators' 
            AND COLUMN_NAME = 'pancard_images'
            """
            
            result = await conn.execute(text(check_pancard_sql))
            pancard_exists = result.scalar() > 0
            
            if not pancard_exists:
                # Add pancard_images JSON field
                add_pancard_sql = """
                ALTER TABLE area_coordinators 
                ADD COLUMN pancard_images JSON NULL COMMENT 'Array of URLs to PAN card images'
                """
                await conn.execute(text(add_pancard_sql))
                print("[OK] Added pancard_images JSON array field")
            else:
                print("[INFO] pancard_images column already exists")
            
            # Check current type of id_proof_document
            check_id_proof_sql = """
            SELECT DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'area_coordinators' 
            AND COLUMN_NAME = 'id_proof_document'
            """
            
            result = await conn.execute(text(check_id_proof_sql))
            id_proof_type = result.scalar()
            
            if id_proof_type and id_proof_type.upper() != 'JSON':
                # Convert existing string values to JSON arrays
                convert_id_proof_sql = """
                UPDATE area_coordinators 
                SET id_proof_document = CASE 
                    WHEN id_proof_document IS NOT NULL AND id_proof_document != '' 
                    THEN JSON_ARRAY(id_proof_document)
                    ELSE NULL 
                END
                """
                await conn.execute(text(convert_id_proof_sql))
                print("[OK] Converted existing id_proof_document values to JSON arrays")
                
                # Change the column type to JSON
                modify_id_proof_sql = """
                ALTER TABLE area_coordinators 
                MODIFY COLUMN id_proof_document JSON NULL COMMENT 'Array of URLs to ID proof documents'
                """
                await conn.execute(text(modify_id_proof_sql))
                print("[OK] Changed id_proof_document column type to JSON")
            else:
                print("[INFO] id_proof_document column is already JSON type")
            
            print("[SUCCESS] AreaCoordinator document fields migration completed")
            
            # Verify the changes
            verification_sql = """
            SELECT 
                id,
                id_proof_document,
                pancard_images,
                pancard_number
            FROM area_coordinators 
            ORDER BY id 
            LIMIT 3
            """
            
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
    asyncio.run(update_area_coordinator_documents_safe())

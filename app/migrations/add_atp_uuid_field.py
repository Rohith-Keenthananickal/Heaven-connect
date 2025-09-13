"""
Migration script to add ATP UUID field to area_coordinators table
Run this script to add the ATP UUID field to the area_coordinators table
"""

import asyncio
from sqlalchemy import text
from app.database import engine


async def add_atp_uuid_field():
    """Add ATP UUID field to area_coordinators table"""
    
    # SQL statement to add ATP UUID field
    add_atp_uuid_sql = """
    ALTER TABLE area_coordinators 
    ADD COLUMN atp_uuid VARCHAR(20) NULL COMMENT 'ATP UUID in format ATP-01234',
    ADD UNIQUE INDEX idx_atp_uuid (atp_uuid),
    ADD INDEX idx_atp_uuid_lookup (atp_uuid);
    """
    
    # SQL statement to generate ATP UUIDs for existing records
    generate_atp_uuids_sql = """
    UPDATE area_coordinators 
    SET atp_uuid = CONCAT('ATP-', LPAD(ROW_NUMBER() OVER (ORDER BY id), 5, '0'))
    WHERE atp_uuid IS NULL;
    """
    
    try:
        async with engine.begin() as conn:
            # Add the ATP UUID field
            await conn.execute(text(add_atp_uuid_sql))
            print("✅ ATP UUID field added to area_coordinators table")
            
            # Generate ATP UUIDs for existing records
            await conn.execute(text(generate_atp_uuids_sql))
            print("✅ ATP UUIDs generated for existing Area Coordinators")
            
            # Verify the changes
            result = await conn.execute(text("""
                SELECT id, atp_uuid, region 
                FROM area_coordinators 
                ORDER BY id 
                LIMIT 5
            """))
            
            records = result.fetchall()
            if records:
                print("✅ Sample ATP UUIDs generated:")
                for record in records:
                    print(f"   ID: {record[0]}, ATP UUID: {record[1]}, Region: {record[2]}")
            else:
                print("ℹ️  No existing Area Coordinators found")
                
    except Exception as e:
        print(f"❌ Error adding ATP UUID field: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(add_atp_uuid_field())

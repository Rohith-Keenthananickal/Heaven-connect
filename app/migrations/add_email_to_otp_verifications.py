"""
Migration: Add email field to otp_verifications table
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import get_async_engine

async def upgrade():
    """Add email field to otp_verifications table"""
    engine = get_async_engine()
    
    async with engine.begin() as conn:
        # Add email column to otp_verifications table
        await conn.execute(text("""
            ALTER TABLE otp_verifications 
            ADD COLUMN email VARCHAR(255) NULL,
            ADD INDEX idx_otp_verifications_email (email)
        """))
        
        # Make phone_number nullable since now we can use either phone or email
        await conn.execute(text("""
            ALTER TABLE otp_verifications 
            MODIFY COLUMN phone_number VARCHAR(20) NULL
        """))
        
        print("SUCCESS: Added email field to otp_verifications table")
        print("SUCCESS: Made phone_number nullable")

async def downgrade():
    """Remove email field from otp_verifications table"""
    engine = get_async_engine()
    
    async with engine.begin() as conn:
        # Remove email column
        await conn.execute(text("""
            ALTER TABLE otp_verifications 
            DROP COLUMN email
        """))
        
        # Make phone_number not nullable again
        await conn.execute(text("""
            ALTER TABLE otp_verifications 
            MODIFY COLUMN phone_number VARCHAR(20) NOT NULL
        """))
        
        print("SUCCESS: Removed email field from otp_verifications table")
        print("SUCCESS: Made phone_number not nullable")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())

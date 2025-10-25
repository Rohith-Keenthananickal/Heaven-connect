"""
Migration: Create communication tables
Created: 2024-01-01
Description: Creates email templates and email logs tables for communication module
"""

from sqlalchemy import text
from app.database import get_async_session
from app.models.communication import EmailTemplate, EmailLog
from app.database import Base, engine
import asyncio


async def upgrade():
    """Create communication tables"""
    async with engine.begin() as conn:
        # Create email_templates table
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, tables=[EmailTemplate.__table__]))
        
        # Create email_logs table
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, tables=[EmailLog.__table__]))
        
        print("Communication tables created successfully")


async def downgrade():
    """Drop communication tables"""
    async with engine.begin() as conn:
        # Drop email_logs table first (due to foreign key constraints)
        await conn.execute(text("DROP TABLE IF EXISTS email_logs"))
        
        # Drop email_templates table
        await conn.execute(text("DROP TABLE IF EXISTS email_templates"))
        
        print("Communication tables dropped successfully")


if __name__ == "__main__":
    import asyncio
    asyncio.run(upgrade())



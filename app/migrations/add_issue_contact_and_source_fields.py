"""
Migration: Add email, phone, and source columns to issues table.
Run: python -m app.migrations.add_issue_contact_and_source_fields
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text

from app.database import engine


async def column_exists(conn, column_name: str) -> bool:
    sql = text(
        """
        SELECT COUNT(*) AS cnt
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'issues'
          AND COLUMN_NAME = :col
        """
    )
    result = await conn.execute(sql, {"col": column_name})
    row = result.fetchone()
    return bool(row and row[0] > 0)


async def index_exists(conn, index_name: str) -> bool:
    sql = text(
        """
        SELECT COUNT(*) AS cnt
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'issues'
          AND INDEX_NAME = :idx
        """
    )
    result = await conn.execute(sql, {"idx": index_name})
    row = result.fetchone()
    return bool(row and row[0] > 0)


async def add_issue_contact_and_source_fields() -> None:
    async with engine.begin() as conn:
        if not await column_exists(conn, "email"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE issues
                    ADD COLUMN email VARCHAR(255) NULL,
                    ADD INDEX idx_issues_email (email)
                    """
                )
            )
            print("[SUCCESS] Added issues.email")
        else:
            print("[INFO] issues.email already exists")

        if not await column_exists(conn, "phone"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE issues
                    ADD COLUMN phone VARCHAR(32) NULL,
                    ADD INDEX idx_issues_phone (phone)
                    """
                )
            )
            print("[SUCCESS] Added issues.phone")
        else:
            print("[INFO] issues.phone already exists")

        if not await column_exists(conn, "source"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE issues
                    ADD COLUMN source VARCHAR(50) NOT NULL DEFAULT 'INTERNAL_UI'
                    """
                )
            )
            print("[SUCCESS] Added issues.source")
        else:
            print("[INFO] issues.source already exists")

        if not await index_exists(conn, "idx_issues_source"):
            await conn.execute(
                text("ALTER TABLE issues ADD INDEX idx_issues_source (source)")
            )
            print("[SUCCESS] Added idx_issues_source")
        else:
            print("[INFO] idx_issues_source already exists")


if __name__ == "__main__":
    asyncio.run(add_issue_contact_and_source_fields())

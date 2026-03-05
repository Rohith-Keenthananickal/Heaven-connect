"""Replace facility_masters.is_active with status enum (ACTIVE, BLOCKED, DELETED)

Revision ID: facility_masters_is_active_to_status
Revises: create_facility_masters_table
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa

revision = "facility_masters_is_active_to_status"
down_revision = "create_facility_masters_table"
branch_labels = None
depends_on = None


def upgrade():
    # Add status column (nullable first for backfill)
    op.add_column(
        "facility_masters",
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "BLOCKED", "DELETED", name="facilitymasterstatus"),
            nullable=True,
        ),
    )
    # Backfill: ACTIVE where is_active was true, BLOCKED where false
    op.execute(
        "UPDATE facility_masters SET status = 'ACTIVE' WHERE is_active = 1"
    )
    op.execute(
        "UPDATE facility_masters SET status = 'BLOCKED' WHERE is_active = 0"
    )
    op.alter_column(
        "facility_masters",
        "status",
        existing_type=sa.Enum("ACTIVE", "BLOCKED", "DELETED", name="facilitymasterstatus"),
        nullable=False,
        server_default="ACTIVE",
    )
    op.drop_column("facility_masters", "is_active")


def downgrade():
    op.add_column(
        "facility_masters",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.execute("UPDATE facility_masters SET is_active = 1 WHERE status = 'ACTIVE'")
    op.execute("UPDATE facility_masters SET is_active = 0 WHERE status != 'ACTIVE'")
    op.drop_column("facility_masters", "status")

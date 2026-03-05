"""Add type column (PROPERTY, EXPERIENCE) to segments table

Revision ID: add_segments_type_column
Revises:
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa

revision = "add_segments_type_column"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "segments",
        sa.Column(
            "type",
            sa.Enum("PROPERTY", "EXPERIENCE", name="segmenttype"),
            nullable=False,
            server_default="PROPERTY",
        ),
    )


def downgrade():
    op.drop_column("segments", "type")

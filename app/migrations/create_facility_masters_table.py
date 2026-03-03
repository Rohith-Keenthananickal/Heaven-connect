"""Create facility_masters table for facility master CRUD

Revision ID: create_facility_masters_table
Revises:
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa

revision = "create_facility_masters_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "facility_masters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False, comment="Display name of the facility"),
        sa.Column("description", sa.String(length=1000), nullable=True, comment="Description of the facility"),
        sa.Column("type", sa.Enum("PROPERTY", "ROOM", name="facilitymastertype"), nullable=False, comment="PROPERTY or ROOM"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_facility_masters_name"), "facility_masters", ["name"], unique=False)
    op.create_index(op.f("ix_facility_masters_id"), "facility_masters", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_facility_masters_name"), table_name="facility_masters")
    op.drop_index(op.f("ix_facility_masters_id"), table_name="facility_masters")
    op.drop_table("facility_masters")

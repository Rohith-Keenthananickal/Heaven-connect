"""Add facility_facility_masters junction table for many-to-many relationship

Revision ID: add_facility_facility_masters_junction
Revises: add_facility_master_id_to_facilities
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa


revision = "add_facility_facility_masters_junction"
down_revision = "add_facility_master_id_to_facilities"
branch_labels = None
depends_on = None


def upgrade():
    # Create junction table for many-to-many relationship
    op.create_table(
        "facility_facility_masters",
        sa.Column("facility_id", sa.Integer(), nullable=False),
        sa.Column("facility_master_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["facility_id"],
            ["facilities.id"],
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["facility_master_id"],
            ["facility_masters.id"],
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("facility_id", "facility_master_id"),
        comment="Junction table for many-to-many relationship between facilities and facility masters"
    )
    
    # Create indexes for better query performance
    op.create_index(
        op.f("ix_facility_facility_masters_facility_id"),
        "facility_facility_masters",
        ["facility_id"],
        unique=False
    )
    op.create_index(
        op.f("ix_facility_facility_masters_facility_master_id"),
        "facility_facility_masters",
        ["facility_master_id"],
        unique=False
    )
    
    # Migrate existing data from facility_master_id to junction table
    # This SQL migrates all existing facility_master_id relationships to the new junction table
    op.execute("""
        INSERT INTO facility_facility_masters (facility_id, facility_master_id)
        SELECT id, facility_master_id
        FROM facilities
        WHERE facility_master_id IS NOT NULL
    """)


def downgrade():
    # Drop indexes
    op.drop_index(
        op.f("ix_facility_facility_masters_facility_master_id"),
        table_name="facility_facility_masters"
    )
    op.drop_index(
        op.f("ix_facility_facility_masters_facility_id"),
        table_name="facility_facility_masters"
    )
    
    # Drop junction table
    op.drop_table("facility_facility_masters")

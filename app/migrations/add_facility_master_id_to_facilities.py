"""Add facility_master_id to facilities and make facility_name/description nullable

Revision ID: add_facility_master_id_to_facilities
Revises:
Create Date: 2025-03-13

"""
from alembic import op
import sqlalchemy as sa


revision = "add_facility_master_id_to_facilities"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "facilities",
        sa.Column(
            "facility_master_id",
            sa.Integer(),
            nullable=True,
            comment="Reference to facility master (name, description, type)",
        ),
    )
    op.create_foreign_key(
        "fk_facilities_facility_master_id",
        "facilities",
        "facility_masters",
        ["facility_master_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_facilities_facility_master_id"),
        "facilities",
        ["facility_master_id"],
        unique=False,
    )
    op.alter_column(
        "facilities",
        "facility_name",
        existing_type=sa.String(200),
        nullable=True,
        comment="Deprecated: use facility_master; kept for backward compatibility",
    )


def downgrade():
    op.drop_index(op.f("ix_facilities_facility_master_id"), table_name="facilities")
    op.drop_constraint(
        "fk_facilities_facility_master_id",
        "facilities",
        type_="foreignkey",
    )
    op.drop_column("facilities", "facility_master_id")
    op.alter_column(
        "facilities",
        "facility_name",
        existing_type=sa.String(200),
        nullable=False,
    )

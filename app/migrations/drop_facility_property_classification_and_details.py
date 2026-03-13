"""Drop property_classification and details from facilities table

Revision ID: drop_facility_property_classification_and_details
Revises:
Create Date: 2025-03-13

"""
from alembic import op
import sqlalchemy as sa


revision = "drop_facility_property_classification_and_details"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop check constraint if it exists (from update_facility_optional_property_classification)
    try:
        op.drop_constraint(
            "ck_facilities_property_or_classification",
            "facilities",
            type_="check",
        )
    except Exception:
        pass
    # Drop index then column for property_classification
    try:
        op.drop_index(op.f("ix_facilities_property_classification"), table_name="facilities")
    except Exception:
        pass
    op.drop_column("facilities", "property_classification")
    op.drop_column("facilities", "details")


def downgrade():
    op.add_column(
        "facilities",
        sa.Column(
            "details",
            sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "facilities",
        sa.Column(
            "property_classification",
            sa.Enum("SILVER", "GOLD", "DIAMOND", "UNCLASSIFIED", name="propertyclassification"),
            nullable=True,
        ),
    )
    op.create_index(
        op.f("ix_facilities_property_classification"),
        "facilities",
        ["property_classification"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_facilities_property_or_classification",
        "facilities",
        "property_id IS NOT NULL OR property_classification IS NOT NULL",
    )

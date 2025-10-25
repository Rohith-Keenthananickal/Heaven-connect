"""Add country_code field to users table

Revision ID: add_country_code_field
Revises: add_verification_fields
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_country_code_field'
down_revision = 'add_verification_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add country_code field to users table"""
    try:
        # Add country_code field
        op.add_column('users', sa.Column('country_code', sa.String(5), nullable=True, comment="Country code like +91, +1, etc."))
        print("SUCCESS: Added country_code field")
        
    except Exception as e:
        print(f"ERROR: Failed to add country_code field: {e}")
        raise


def downgrade():
    """Remove country_code field from users table"""
    try:
        # Drop country_code column
        op.drop_column('users', 'country_code')
        print("SUCCESS: Dropped country_code column")
        
    except Exception as e:
        print(f"ERROR: Failed to remove country_code field: {e}")
        raise

"""Add facility name and description fields to Facility model

Revision ID: add_facility_name_description_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_facility_name_description_fields'
down_revision = None  # Update this with the latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Add facility name and description fields to facilities table"""
    # Add new columns
    op.add_column('facilities', sa.Column('facility_name', sa.String(length=200), nullable=False, comment='Name of the facility'))
    op.add_column('facilities', sa.Column('facility_description', sa.String(length=1000), nullable=True, comment='Description of the facility'))
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_facilities_facility_name'), 'facilities', ['facility_name'], unique=False)
    
    # Add a unique constraint on facility_name to prevent duplicates
    op.create_unique_constraint('uq_facilities_name', 'facilities', ['facility_name'])


def downgrade():
    """Remove facility name and description fields from facilities table"""
    # Drop unique constraint
    op.drop_constraint('uq_facilities_name', 'facilities', type_='unique')
    
    # Drop indexes
    op.drop_index(op.f('ix_facilities_facility_name'), table_name='facilities')
    
    # Drop the new columns
    op.drop_column('facilities', 'facility_description')
    op.drop_column('facilities', 'facility_name')

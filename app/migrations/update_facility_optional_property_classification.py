"""Update Facility model to make property_id optional and add property classification

Revision ID: update_facility_optional_property_classification
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_facility_optional_property_classification'
down_revision = None  # Update this with the latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Update Facility model to support common facilities"""
    # Make property_id nullable
    op.alter_column('facilities', 'property_id', nullable=True, comment='Optional property ID for property-specific facilities')
    
    # Add new columns
    op.add_column('facilities', sa.Column('property_classification', sa.Enum('SILVER', 'GOLD', 'DIAMOND', 'UNCLASSIFIED', name='propertyclassification'), nullable=True, comment='Property classification this facility applies to (for common facilities)'))
    op.add_column('facilities', sa.Column('is_common', sa.Boolean(), nullable=False, server_default='false', comment='Whether this is a common facility available to all properties'))
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_facilities_property_classification'), 'facilities', ['property_classification'], unique=False)
    op.create_index(op.f('ix_facilities_is_common'), 'facilities', ['is_common'], unique=False)
    
    # Add a check constraint to ensure either property_id or property_classification is set
    op.create_check_constraint(
        'ck_facilities_property_or_classification',
        'facilities',
        'property_id IS NOT NULL OR property_classification IS NOT NULL'
    )


def downgrade():
    """Revert Facility model changes"""
    # Drop check constraint
    op.drop_constraint('ck_facilities_property_or_classification', 'facilities', type_='check')
    
    # Drop indexes
    op.drop_index(op.f('ix_facilities_is_common'), table_name='facilities')
    op.drop_index(op.f('ix_facilities_property_classification'), table_name='facilities')
    
    # Drop new columns
    op.drop_column('facilities', 'is_common')
    op.drop_column('facilities', 'property_classification')
    
    # Make property_id not nullable again
    op.alter_column('facilities', 'property_id', nullable=False)

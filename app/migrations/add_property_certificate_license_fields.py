"""Add tourism certificate and trade license fields to Property model

Revision ID: add_property_certificate_license_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_property_certificate_license_fields'
down_revision = None  # Update this with the latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Add tourism certificate and trade license fields to properties table"""
    # Add tourism certificate fields
    op.add_column('properties', sa.Column('tourism_certificate_number', sa.String(length=100), nullable=True, comment='Tourism department certificate number'))
    op.add_column('properties', sa.Column('tourism_certificate_issued_by', sa.String(length=200), nullable=True, comment='Authority that issued the tourism certificate'))
    op.add_column('properties', sa.Column('tourism_certificate_photos', sa.JSON(), nullable=True, comment='Array of URLs to tourism certificate photos'))
    
    # Add trade license fields
    op.add_column('properties', sa.Column('trade_license_number', sa.String(length=100), nullable=True))
    op.add_column('properties', sa.Column('trade_license_images', sa.JSON(), nullable=True, comment='Array of URLs to trade license images'))
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_properties_tourism_certificate_number'), 'properties', ['tourism_certificate_number'], unique=False)
    op.create_index(op.f('ix_properties_trade_license_number'), 'properties', ['trade_license_number'], unique=False)


def downgrade():
    """Remove tourism certificate and trade license fields from properties table"""
    # Drop indexes
    op.drop_index(op.f('ix_properties_trade_license_number'), table_name='properties')
    op.drop_index(op.f('ix_properties_tourism_certificate_number'), table_name='properties')
    
    # Drop the new columns
    op.drop_column('properties', 'trade_license_images')
    op.drop_column('properties', 'trade_license_number')
    op.drop_column('properties', 'tourism_certificate_photos')
    op.drop_column('properties', 'tourism_certificate_issued_by')
    op.drop_column('properties', 'tourism_certificate_number')

"""Add property image fields to Property model

Revision ID: add_property_image_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_property_image_fields'
down_revision = None  # Update this with the latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Add property image fields to properties table"""
    # Add new image columns
    op.add_column('properties', sa.Column('cover_image', sa.String(length=500), nullable=True, comment='Main cover image URL for the property'))
    op.add_column('properties', sa.Column('exterior_images', sa.JSON(), nullable=True, comment='Array of URLs to exterior images'))
    op.add_column('properties', sa.Column('bedroom_images', sa.JSON(), nullable=True, comment='Array of URLs to bedroom images'))
    op.add_column('properties', sa.Column('bathroom_images', sa.JSON(), nullable=True, comment='Array of URLs to bathroom images'))
    op.add_column('properties', sa.Column('living_dining_images', sa.JSON(), nullable=True, comment='Array of URLs to living and dining room images'))
    
    # Create index on cover_image for better query performance
    op.create_index(op.f('ix_properties_cover_image'), 'properties', ['cover_image'], unique=False)


def downgrade():
    """Remove property image fields from properties table"""
    # Drop indexes
    op.drop_index(op.f('ix_properties_cover_image'), table_name='properties')
    
    # Drop the new columns
    op.drop_column('properties', 'living_dining_images')
    op.drop_column('properties', 'bathroom_images')
    op.drop_column('properties', 'bedroom_images')
    op.drop_column('properties', 'exterior_images')
    op.drop_column('properties', 'cover_image')

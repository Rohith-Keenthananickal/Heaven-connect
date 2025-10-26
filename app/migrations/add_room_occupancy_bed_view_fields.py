"""Add maximum occupancy, bed type, and view fields to Room model

Revision ID: add_room_occupancy_bed_view_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_room_occupancy_bed_view_fields'
down_revision = None  # Update this with the latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Add maximum occupancy, bed type, and view fields to rooms table"""
    # Add new columns to rooms table
    op.add_column('rooms', sa.Column('max_occupancy', sa.Integer(), nullable=False, server_default='1', comment='Maximum number of guests that can occupy this room'))
    op.add_column('rooms', sa.Column('bed_type', sa.Enum('SINGLE', 'DOUBLE', 'QUEEN', 'KING', 'TWIN', 'FULL', 'CALIFORNIA_KING', 'SOFA_BED', 'BUNK_BED', 'CUSTOM', name='bedtype'), nullable=False, server_default='SINGLE', comment='Type of bed in the room'))
    op.add_column('rooms', sa.Column('view', sa.Enum('GARDEN', 'POOL', 'SEA_FACING', 'MOUNTAIN_VIEW', 'CITY_VIEW', 'STREET_VIEW', 'COURTYARD', 'BALCONY', 'NO_VIEW', 'PARTIAL_VIEW', name='roomview'), nullable=False, server_default='NO_VIEW', comment='View from the room'))
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_rooms_bed_type'), 'rooms', ['bed_type'], unique=False)
    op.create_index(op.f('ix_rooms_view'), 'rooms', ['view'], unique=False)
    op.create_index(op.f('ix_rooms_max_occupancy'), 'rooms', ['max_occupancy'], unique=False)


def downgrade():
    """Remove maximum occupancy, bed type, and view fields from rooms table"""
    # Drop indexes
    op.drop_index(op.f('ix_rooms_max_occupancy'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_view'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_bed_type'), table_name='rooms')
    
    # Drop the new columns
    op.drop_column('rooms', 'view')
    op.drop_column('rooms', 'bed_type')
    op.drop_column('rooms', 'max_occupancy')
    
    # Drop the enum types
    op.execute('DROP TYPE IF EXISTS roomview')
    op.execute('DROP TYPE IF EXISTS bedtype')

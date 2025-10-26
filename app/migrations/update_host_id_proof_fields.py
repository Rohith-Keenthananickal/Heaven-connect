"""Update Host model with ID proof fields

Revision ID: update_host_id_proof_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_host_id_proof_fields'
down_revision = None  # Update this with the latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Add ID proof fields to hosts table"""
    # Add new columns to hosts table
    op.add_column('hosts', sa.Column('id_proof_type', sa.String(length=50), nullable=True, comment='Aadhar, PAN, Driving License, etc.'))
    op.add_column('hosts', sa.Column('id_proof_number', sa.String(length=100), nullable=True))
    op.add_column('hosts', sa.Column('id_proof_images', sa.JSON(), nullable=True, comment='Array of URLs to ID proof images'))
    
    # Create index on id_proof_number for better query performance
    op.create_index(op.f('ix_hosts_id_proof_number'), 'hosts', ['id_proof_number'], unique=False)
    
    # Remove the old license_number column
    op.drop_column('hosts', 'license_number')


def downgrade():
    """Remove ID proof fields from hosts table"""
    # Add back the old license_number column
    op.add_column('hosts', sa.Column('license_number', sa.String(length=100), nullable=True))
    
    # Drop the new columns
    op.drop_index(op.f('ix_hosts_id_proof_number'), table_name='hosts')
    op.drop_column('hosts', 'id_proof_images')
    op.drop_column('hosts', 'id_proof_number')
    op.drop_column('hosts', 'id_proof_type')

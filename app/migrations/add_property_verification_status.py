"""Add verification_status field to properties table

Revision ID: add_property_verification_status
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_property_verification_status'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type for verification_status
    verification_status_enum = postgresql.ENUM('DRAFT', 'PENDING', 'APPROVED', 'REJECTED', name='propertyverificationstatus', create_type=False)
    verification_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Add verification_status column to properties table
    op.add_column('properties', sa.Column('verification_status', sa.Enum('DRAFT', 'PENDING', 'APPROVED', 'REJECTED', name='propertyverificationstatus'), nullable=True, server_default='DRAFT', comment='Verification status: DRAFT, PENDING, APPROVED, REJECTED'))


def downgrade():
    op.drop_column('properties', 'verification_status')
    op.execute('DROP TYPE IF EXISTS propertyverificationstatus')



"""
Migration script to create enquiry table.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from datetime import datetime


# Revision identifiers
revision = 'enquiry_table_001'
down_revision = None
depends_on = None


def upgrade():
    """Create the enquiries table."""
    op.create_table(
        'enquiries',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('host_name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone_number', sa.String(20), nullable=False, index=True),
        sa.Column('alternate_phone_number', sa.String(20), nullable=True),
        sa.Column('dob', sa.Date, nullable=True),
        sa.Column(
            'gender', 
            sa.Enum('MALE', 'FEMALE', 'OTHER', name='gender'), 
            nullable=True
        ),
        sa.Column(
            'id_card_type', 
            sa.Enum('AADHAR', 'PAN', 'DRIVING_LICENSE', 'VOTER_ID', 'PASSPORT', 'OTHER', name='idcardtype'), 
            nullable=True
        ),
        sa.Column('id_card_number', sa.String(100), nullable=True, index=True),
        sa.Column('atp_id', sa.String(20), nullable=True, unique=True, index=True),
        sa.Column(
            'status', 
            sa.Enum('PENDING', 'PROCESSED', 'REJECTED', 'CONVERTED', name='enquirystatus'), 
            nullable=False, 
            default='PENDING',
            server_default='PENDING'
        ),
        sa.Column('remarks', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create indexes for common search fields
    op.create_index('ix_enquiries_email', 'enquiries', ['email'])
    op.create_index('ix_enquiries_status', 'enquiries', ['status'])


def downgrade():
    """Drop the enquiries table."""
    # Drop indexes
    op.drop_index('ix_enquiries_email', table_name='enquiries')
    op.drop_index('ix_enquiries_phone_number', table_name='enquiries')
    op.drop_index('ix_enquiries_id_card_number', table_name='enquiries')
    op.drop_index('ix_enquiries_atp_id', table_name='enquiries')
    op.drop_index('ix_enquiries_status', table_name='enquiries')
    
    # Drop the table
    op.drop_table('enquiries')
    
    # Clean up enum types if database supports it (like PostgreSQL)
    # For MySQL, they are automatically cleaned up with the table
    # If running on PostgreSQL, uncomment these lines:
    # op.execute("DROP TYPE gender;")
    # op.execute("DROP TYPE idcardtype;")
    # op.execute("DROP TYPE enquirystatus;")

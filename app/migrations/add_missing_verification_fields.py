"""Add missing email_verified and phone_verified fields to users table

Revision ID: add_missing_verification_fields
Revises: add_verification_fields
Create Date: 2025-10-28 18:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_missing_verification_fields'
down_revision = 'add_verification_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add email_verified and phone_verified fields to users table if they don't exist"""
    try:
        # First check if columns already exist
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        # Add email_verified if it doesn't exist
        if 'email_verified' not in columns:
            op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
            print("SUCCESS: Added email_verified field")
            
            # Create index for better query performance
            op.create_index('idx_users_email_verified', 'users', ['email_verified'])
            print("SUCCESS: Created index for email_verified")
        else:
            print("INFO: email_verified column already exists")
        
        # Add phone_verified if it doesn't exist
        if 'phone_verified' not in columns:
            op.add_column('users', sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default='false'))
            print("SUCCESS: Added phone_verified field")
            
            # Create index for better query performance
            op.create_index('idx_users_phone_verified', 'users', ['phone_verified'])
            print("SUCCESS: Created index for phone_verified")
        else:
            print("INFO: phone_verified column already exists")
            
    except Exception as e:
        print(f"ERROR: Failed to add verification fields: {e}")
        raise


def downgrade():
    """Remove email_verified and phone_verified fields from users table if needed"""
    # No downgrade needed as this is fixing a missing migration
    pass

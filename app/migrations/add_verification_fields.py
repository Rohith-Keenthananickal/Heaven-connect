"""Add email_verified and phone_verified fields to users table

Revision ID: add_verification_fields
Revises: add_email_to_otp_verifications
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_verification_fields'
down_revision = 'add_email_to_otp_verifications'
branch_labels = None
depends_on = None


def upgrade():
    """Add email_verified and phone_verified fields to users table"""
    try:
        # Add email_verified field
        op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
        print("SUCCESS: Added email_verified field")
        
        # Add phone_verified field  
        op.add_column('users', sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default='false'))
        print("SUCCESS: Added phone_verified field")
        
        # Create indexes for better query performance
        op.create_index('idx_users_email_verified', 'users', ['email_verified'])
        print("SUCCESS: Created index for email_verified")
        
        op.create_index('idx_users_phone_verified', 'users', ['phone_verified'])
        print("SUCCESS: Created index for phone_verified")
        
        # Update existing users to have verified status based on their auth_provider
        # This is a best-effort approach - in production you might want to handle this differently
        connection = op.get_bind()
        connection.execute(
            sa.text("""
                UPDATE users 
                SET email_verified = CASE 
                    WHEN auth_provider = 'EMAIL' AND email IS NOT NULL THEN true 
                    ELSE false 
                END,
                phone_verified = CASE 
                    WHEN auth_provider = 'MOBILE' AND phone_number IS NOT NULL THEN true 
                    ELSE false 
                END
            """)
        )
        print("SUCCESS: Updated existing users verification status")
        
    except Exception as e:
        print(f"ERROR: Failed to add verification fields: {e}")
        raise


def downgrade():
    """Remove email_verified and phone_verified fields from users table"""
    try:
        # Drop indexes first
        op.drop_index('idx_users_phone_verified', table_name='users')
        print("SUCCESS: Dropped phone_verified index")
        
        op.drop_index('idx_users_email_verified', table_name='users')
        print("SUCCESS: Dropped email_verified index")
        
        # Drop columns
        op.drop_column('users', 'phone_verified')
        print("SUCCESS: Dropped phone_verified column")
        
        op.drop_column('users', 'email_verified')
        print("SUCCESS: Dropped email_verified column")
        
    except Exception as e:
        print(f"ERROR: Failed to remove verification fields: {e}")
        raise

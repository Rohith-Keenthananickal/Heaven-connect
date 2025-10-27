"""Create property_approvals table

Revision ID: create_property_approvals
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_property_approvals'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type for verification_status
    verification_status_enum = postgresql.ENUM('APPROVED', 'REJECTED', name='verificationstatus', create_type=False)
    verification_status_enum.create(op.get_bind(), checkfirst=True)
    
    op.create_table(
        'property_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('atp_id', sa.Integer(), nullable=False, comment='Area Coordinator/ATP who approved/rejected'),
        sa.Column('approval_type', sa.String(length=100), nullable=False, comment='Type of approval (e.g., PERSONAL_DETAILS, DOCUMENTS, PROPERTY_DETAILS)'),
        sa.Column('verification_type', sa.Enum('APPROVED', 'REJECTED', name='verificationstatus'), nullable=False, comment='APPROVED or REJECTED'),
        sa.Column('note', sa.String(length=1000), nullable=True, comment='Notes or comments from the ATP'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['atp_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_property_approvals_id'), 'property_approvals', ['id'], unique=False)
    op.create_index(op.f('ix_property_approvals_property_id'), 'property_approvals', ['property_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_property_approvals_property_id'), table_name='property_approvals')
    op.drop_index(op.f('ix_property_approvals_id'), table_name='property_approvals')
    op.drop_table('property_approvals')


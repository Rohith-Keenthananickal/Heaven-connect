"""Create corporation and municipality tables

Revision ID: create_corporation_municipality_tables
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_corporation_municipality_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create corporations table
    op.create_table('corporations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('district_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('area_sq_km', sa.Float(), nullable=True),
        sa.Column('mayor_name', sa.String(length=100), nullable=True),
        sa.Column('established_year', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_corporations_id'), 'corporations', ['id'], unique=False)
    op.create_index(op.f('ix_corporations_name'), 'corporations', ['name'], unique=False)
    op.create_index(op.f('ix_corporations_district_id'), 'corporations', ['district_id'], unique=False)
    op.create_index(op.f('ix_corporations_code'), 'corporations', ['code'], unique=True)

    # Create municipalities table
    op.create_table('municipalities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('district_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('area_sq_km', sa.Float(), nullable=True),
        sa.Column('chairman_name', sa.String(length=100), nullable=True),
        sa.Column('established_year', sa.Integer(), nullable=True),
        sa.Column('municipality_type', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_municipalities_id'), 'municipalities', ['id'], unique=False)
    op.create_index(op.f('ix_municipalities_name'), 'municipalities', ['name'], unique=False)
    op.create_index(op.f('ix_municipalities_district_id'), 'municipalities', ['district_id'], unique=False)
    op.create_index(op.f('ix_municipalities_code'), 'municipalities', ['code'], unique=True)


def downgrade():
    # Drop municipalities table
    op.drop_index(op.f('ix_municipalities_code'), table_name='municipalities')
    op.drop_index(op.f('ix_municipalities_district_id'), table_name='municipalities')
    op.drop_index(op.f('ix_municipalities_name'), table_name='municipalities')
    op.drop_index(op.f('ix_municipalities_id'), table_name='municipalities')
    op.drop_table('municipalities')

    # Drop corporations table
    op.drop_index(op.f('ix_corporations_code'), table_name='corporations')
    op.drop_index(op.f('ix_corporations_district_id'), table_name='corporations')
    op.drop_index(op.f('ix_corporations_name'), table_name='corporations')
    op.drop_index(op.f('ix_corporations_id'), table_name='corporations')
    op.drop_table('corporations')

"""Connect AreaCoordinator to existing location tables using foreign keys

Revision ID: connect_area_coordinator_to_location_tables
Revises: add_area_coordinator_business_local_body_fields
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'connect_area_coordinator_to_location_tables'
down_revision = 'add_area_coordinator_business_local_body_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Connect AreaCoordinator to existing location tables using foreign keys"""
    try:
        # Drop the old text-based local body fields
        op.drop_column('area_coordinators', 'local_body')
        print("SUCCESS: Dropped local_body column")
        
        op.drop_column('area_coordinators', 'local_body_pincode')
        print("SUCCESS: Dropped local_body_pincode column")
        
        op.drop_column('area_coordinators', 'local_body_district')
        print("SUCCESS: Dropped local_body_district column")
        
        op.drop_column('area_coordinators', 'local_body_corporation_municipality')
        print("SUCCESS: Dropped local_body_corporation_municipality column")
        
        # Add foreign key fields to existing location tables
        op.add_column('area_coordinators', sa.Column('local_body_district_id', sa.Integer(), nullable=True, comment="Reference to districts table"))
        print("SUCCESS: Added local_body_district_id field")
        
        op.add_column('area_coordinators', sa.Column('local_body_grama_panchayat_id', sa.Integer(), nullable=True, comment="Reference to grama_panchayats table"))
        print("SUCCESS: Added local_body_grama_panchayat_id field")
        
        op.add_column('area_coordinators', sa.Column('local_body_corporation_id', sa.Integer(), nullable=True, comment="Reference to corporations table"))
        print("SUCCESS: Added local_body_corporation_id field")
        
        op.add_column('area_coordinators', sa.Column('local_body_municipality_id', sa.Integer(), nullable=True, comment="Reference to municipalities table"))
        print("SUCCESS: Added local_body_municipality_id field")
        
        # Add foreign key constraints
        op.create_foreign_key('fk_area_coordinators_district', 'area_coordinators', 'districts', ['local_body_district_id'], ['id'])
        print("SUCCESS: Created foreign key constraint for district")
        
        op.create_foreign_key('fk_area_coordinators_grama_panchayat', 'area_coordinators', 'grama_panchayats', ['local_body_grama_panchayat_id'], ['id'])
        print("SUCCESS: Created foreign key constraint for grama_panchayat")
        
        op.create_foreign_key('fk_area_coordinators_corporation', 'area_coordinators', 'corporations', ['local_body_corporation_id'], ['id'])
        print("SUCCESS: Created foreign key constraint for corporation")
        
        op.create_foreign_key('fk_area_coordinators_municipality', 'area_coordinators', 'municipalities', ['local_body_municipality_id'], ['id'])
        print("SUCCESS: Created foreign key constraint for municipality")
        
        # Create indexes for better query performance
        op.create_index('idx_area_coordinators_district_id', 'area_coordinators', ['local_body_district_id'])
        print("SUCCESS: Created index for local_body_district_id")
        
        op.create_index('idx_area_coordinators_grama_panchayat_id', 'area_coordinators', ['local_body_grama_panchayat_id'])
        print("SUCCESS: Created index for local_body_grama_panchayat_id")
        
        op.create_index('idx_area_coordinators_corporation_id', 'area_coordinators', ['local_body_corporation_id'])
        print("SUCCESS: Created index for local_body_corporation_id")
        
        op.create_index('idx_area_coordinators_municipality_id', 'area_coordinators', ['local_body_municipality_id'])
        print("SUCCESS: Created index for local_body_municipality_id")
        
    except Exception as e:
        print(f"ERROR: Failed to connect AreaCoordinator to location tables: {e}")
        raise


def downgrade():
    """Remove foreign key connections and restore text-based fields"""
    try:
        # Drop indexes
        op.drop_index('idx_area_coordinators_municipality_id', table_name='area_coordinators')
        print("SUCCESS: Dropped municipality index")
        
        op.drop_index('idx_area_coordinators_corporation_id', table_name='area_coordinators')
        print("SUCCESS: Dropped corporation index")
        
        op.drop_index('idx_area_coordinators_grama_panchayat_id', table_name='area_coordinators')
        print("SUCCESS: Dropped grama_panchayat index")
        
        op.drop_index('idx_area_coordinators_district_id', table_name='area_coordinators')
        print("SUCCESS: Dropped district index")
        
        # Drop foreign key constraints
        op.drop_constraint('fk_area_coordinators_municipality', 'area_coordinators', type_='foreignkey')
        print("SUCCESS: Dropped municipality foreign key constraint")
        
        op.drop_constraint('fk_area_coordinators_corporation', 'area_coordinators', type_='foreignkey')
        print("SUCCESS: Dropped corporation foreign key constraint")
        
        op.drop_constraint('fk_area_coordinators_grama_panchayat', 'area_coordinators', type_='foreignkey')
        print("SUCCESS: Dropped grama_panchayat foreign key constraint")
        
        op.drop_constraint('fk_area_coordinators_district', 'area_coordinators', type_='foreignkey')
        print("SUCCESS: Dropped district foreign key constraint")
        
        # Drop foreign key columns
        op.drop_column('area_coordinators', 'local_body_municipality_id')
        print("SUCCESS: Dropped local_body_municipality_id column")
        
        op.drop_column('area_coordinators', 'local_body_corporation_id')
        print("SUCCESS: Dropped local_body_corporation_id column")
        
        op.drop_column('area_coordinators', 'local_body_grama_panchayat_id')
        print("SUCCESS: Dropped local_body_grama_panchayat_id column")
        
        op.drop_column('area_coordinators', 'local_body_district_id')
        print("SUCCESS: Dropped local_body_district_id column")
        
        # Restore text-based fields
        op.add_column('area_coordinators', sa.Column('local_body', sa.String(200), nullable=True, comment="Local body name"))
        print("SUCCESS: Restored local_body column")
        
        op.add_column('area_coordinators', sa.Column('local_body_pincode', sa.String(20), nullable=True, comment="Local body pincode"))
        print("SUCCESS: Restored local_body_pincode column")
        
        op.add_column('area_coordinators', sa.Column('local_body_district', sa.String(100), nullable=True, comment="Local body district"))
        print("SUCCESS: Restored local_body_district column")
        
        op.add_column('area_coordinators', sa.Column('local_body_corporation_municipality', sa.String(200), nullable=True, comment="Local body corporation or municipality"))
        print("SUCCESS: Restored local_body_corporation_municipality column")
        
    except Exception as e:
        print(f"ERROR: Failed to remove foreign key connections: {e}")
        raise

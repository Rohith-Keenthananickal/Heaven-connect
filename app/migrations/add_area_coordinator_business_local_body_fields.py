"""Add business and local body fields to area_coordinators table

Revision ID: add_area_coordinator_business_local_body_fields
Revises: add_country_code_field
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_area_coordinator_business_local_body_fields'
down_revision = 'add_country_code_field'
branch_labels = None
depends_on = None


def upgrade():
    """Add business and local body fields to area_coordinators table"""
    try:
        # Add business information field
        op.add_column('area_coordinators', sa.Column('business_name', sa.String(200), nullable=True, comment="Business name of the area coordinator"))
        print("SUCCESS: Added business_name field")
        
        # Add local body information fields
        op.add_column('area_coordinators', sa.Column('local_body', sa.String(200), nullable=True, comment="Local body name"))
        print("SUCCESS: Added local_body field")
        
        op.add_column('area_coordinators', sa.Column('local_body_pincode', sa.String(20), nullable=True, comment="Local body pincode"))
        print("SUCCESS: Added local_body_pincode field")
        
        op.add_column('area_coordinators', sa.Column('local_body_district', sa.String(100), nullable=True, comment="Local body district"))
        print("SUCCESS: Added local_body_district field")
        
        op.add_column('area_coordinators', sa.Column('local_body_corporation_municipality', sa.String(200), nullable=True, comment="Local body corporation or municipality"))
        print("SUCCESS: Added local_body_corporation_municipality field")
        
        op.add_column('area_coordinators', sa.Column('local_body_ward', sa.String(100), nullable=True, comment="Local body ward"))
        print("SUCCESS: Added local_body_ward field")
        
    except Exception as e:
        print(f"ERROR: Failed to add business and local body fields: {e}")
        raise


def downgrade():
    """Remove business and local body fields from area_coordinators table"""
    try:
        # Drop local body fields
        op.drop_column('area_coordinators', 'local_body_ward')
        print("SUCCESS: Dropped local_body_ward column")
        
        op.drop_column('area_coordinators', 'local_body_corporation_municipality')
        print("SUCCESS: Dropped local_body_corporation_municipality column")
        
        op.drop_column('area_coordinators', 'local_body_district')
        print("SUCCESS: Dropped local_body_district column")
        
        op.drop_column('area_coordinators', 'local_body_pincode')
        print("SUCCESS: Dropped local_body_pincode column")
        
        op.drop_column('area_coordinators', 'local_body')
        print("SUCCESS: Dropped local_body column")
        
        # Drop business field
        op.drop_column('area_coordinators', 'business_name')
        print("SUCCESS: Dropped business_name column")
        
    except Exception as e:
        print(f"ERROR: Failed to remove business and local body fields: {e}")
        raise

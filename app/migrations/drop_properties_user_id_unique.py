"""Drop unique constraint on properties.user_id to allow multiple properties per user

Revision ID: drop_properties_user_id_unique
Revises:
Create Date: 2026-03-03

"""
from alembic import op

revision = "drop_properties_user_id_unique"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Allow multiple properties per user: drop unique on user_id.
    # MySQL names the key 'user_id'; if this fails, check SHOW CREATE TABLE properties.
    op.drop_constraint("user_id", "properties", type_="unique")
    # Add non-unique index for listing properties by user
    op.create_index("ix_properties_user_id", "properties", ["user_id"], unique=False)


def downgrade():
    op.drop_index("ix_properties_user_id", table_name="properties")
    op.create_unique_constraint("user_id", "properties", ["user_id"])

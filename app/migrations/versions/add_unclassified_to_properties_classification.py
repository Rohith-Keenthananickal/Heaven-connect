"""Extend properties.classification ENUM with UNCLASSIFIED (MySQL).

Revision ID: prop_cls_unclassified (<=32 chars for alembic_version.version_num)
Revises:
Create Date: 2026-03-21

MySQL returns (1265, Data truncated for column 'classification') when the value
is not listed on the column ENUM. The ORM enum includes UNCLASSIFIED; the DB
must be altered to match.
"""
from alembic import op
import sqlalchemy as sa

revision = "prop_cls_unclassified"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "mysql":
        return
    op.execute(
        sa.text(
            "ALTER TABLE properties MODIFY COLUMN classification "
            "ENUM('SILVER','GOLD','DIAMOND','UNCLASSIFIED') NOT NULL DEFAULT 'SILVER'"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "mysql":
        return
    op.execute(
        sa.text(
            "UPDATE properties SET classification = 'SILVER' WHERE classification = 'UNCLASSIFIED'"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE properties MODIFY COLUMN classification "
            "ENUM('SILVER','GOLD','DIAMOND') NOT NULL DEFAULT 'SILVER'"
        )
    )

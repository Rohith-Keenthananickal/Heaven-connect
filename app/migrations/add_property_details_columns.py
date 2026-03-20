"""
Add missing columns to property_details table to match PropertyDetails model.

Fixes: Unknown column 'property_details.nearby_attractions' in 'field list'

Run from project root: python -m app.migrations.add_property_details_columns
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text
from app.core.config import settings


# Columns that may be missing: (name, sql_type, default_clause)
# default_clause is for NOT NULL columns only (e.g. "DEFAULT 0" or "DEFAULT FALSE")
COLUMNS_TO_ADD = [
    ("nearby_attractions", "JSON", None),
    ("nearby_activities", "JSON", None),
    ("seasonal_experiences", "JSON", None),
    ("comfort_services_list", "JSON", None),
    ("noise_level", "TINYINT(1)", "DEFAULT 0"),
    ("checkin_time", "VARCHAR(20)", None),
    ("checkout_time", "VARCHAR(20)", None),
    ("smoking_allowed", "TINYINT(1)", "DEFAULT 0"),
    ("pets_allowed", "TINYINT(1)", "DEFAULT 0"),
    ("alcohol_allowed", "TINYINT(1)", "DEFAULT 0"),
    ("visitor_policy", "VARCHAR(1000)", None),
    ("quiet_hours", "VARCHAR(200)", None),
    ("comfort_services", "TINYINT(1)", "DEFAULT 0"),
    ("meals_available", "TINYINT(1)", "DEFAULT 0"),
    ("airport_pickup", "TINYINT(1)", "DEFAULT 0"),
    ("laundry_service", "TINYINT(1)", "DEFAULT 0"),
    ("housekeeping_frequency", "VARCHAR(100)", None),
    ("about_space", "VARCHAR(5000)", None),
    ("host_languages", "JSON", None),
    ("other_name", "VARCHAR(255)", None),
]


def column_exists(connection, table: str, column: str) -> bool:
    """Check if a column exists in the table (MySQL)."""
    r = connection.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
        ),
        {"t": table, "c": column},
    )
    return r.scalar() > 0


def add_property_details_columns():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as connection:
        try:
            for col_name, sql_type, default_clause in COLUMNS_TO_ADD:
                if column_exists(connection, "property_details", col_name):
                    print(f"Column property_details.{col_name} already exists, skipping.")
                    continue
                nullable = "NULL" if default_clause is None else "NOT NULL"
                default = f" {default_clause}" if default_clause else ""
                sql = f"ALTER TABLE property_details ADD COLUMN {col_name} {sql_type} {nullable}{default}"
                connection.execute(text(sql))
                connection.commit()
                print(f"Added column property_details.{col_name}")
            print("Migration completed successfully.")
        except Exception as e:
            print(f"Migration failed: {e}")
            connection.rollback()
            return False
    return True


if __name__ == "__main__":
    success = add_property_details_columns()
    sys.exit(0 if success else 1)

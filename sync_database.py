"""
Comprehensive database synchronization script to ensure all tables and columns
from SQLAlchemy models exist in the database.
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text, MetaData
from sqlalchemy.schema import CreateTable
from app.database import Base
from app.core.config import settings

# Import all models to ensure they're registered with SQLAlchemy
from app.models.user import (
    User, Guest, Host, AreaCoordinator, BankDetails, OTPVerification,
    AuthProvider, UserType, UserStatus, ApprovalStatus
)
from app.models.property import (
    Property, Room, Facility, PropertyPhoto, 
    Location, Availability, PropertyAgreement
)
from app.models.location import (
    District, GramaPanchayat, Corporation, Municipality
)
from app.models.training import (
    TrainingModule, TrainingContent, TrainingProgress, 
    ContentType, TrainingStatus
)

def sync_database():
    """
    Synchronize database schema with SQLAlchemy models by adding missing columns.
    """
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Get metadata from SQLAlchemy models
    metadata = Base.metadata
    
    # Get inspector to examine database schema
    inspector = inspect(engine)
    
    with engine.connect() as connection:
        try:
            # Get all tables in the database
            existing_tables = inspector.get_table_names()
            
            # Tables that need to be created
            tables_to_create = []
            for table_name, table in metadata.tables.items():
                if table_name not in existing_tables:
                    tables_to_create.append((table_name, table))
            
            # Create missing tables
            if tables_to_create:
                print(f"Creating {len(tables_to_create)} missing tables...")
                for table_name, table in tables_to_create:
                    print(f"  - Creating table: {table_name}")
                    create_table_stmt = CreateTable(table)
                    connection.execute(text(str(create_table_stmt.compile(engine))))
                print("All missing tables created")
            else:
                print("No missing tables to create")
            
            # For each existing table, check for missing columns
            for table_name, table in metadata.tables.items():
                if table_name in existing_tables:
                    # Get existing columns in the database
                    existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
                    
                    # Get columns defined in the SQLAlchemy model
                    model_columns = {col.name for col in table.columns}
                    
                    # Find missing columns
                    missing_columns = model_columns - existing_columns
                    
                    if missing_columns:
                        print(f"Found {len(missing_columns)} missing columns in table {table_name}:")
                        
                        # Add each missing column
                        for column_name in missing_columns:
                            # Get column object from the model
                            column = table.columns[column_name]
                            
                            # Generate SQL type definition
                            column_type = column.type.compile(engine.dialect)
                            
                            # Determine if column is nullable
                            nullable = "NULL" if column.nullable else "NOT NULL"
                            
                            # Get default value if specified
                            default = ""
                            if column.server_default:
                                default_value = column.server_default.arg
                                if isinstance(default_value, str):
                                    default = f" DEFAULT '{default_value}'"
                                else:
                                    default = f" DEFAULT {default_value}"
                            elif not column.nullable:
                                if column_type in ('BOOLEAN', 'TINYINT(1)'):
                                    default = " DEFAULT false"
                                elif column_type in ('INTEGER', 'INT'):
                                    default = " DEFAULT 0"
                                elif column_type.startswith('VARCHAR') or column_type.startswith('CHAR'):
                                    default = " DEFAULT ''"
                            
                            # Create ALTER TABLE statement
                            alter_stmt = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {nullable}{default}"
                            
                            print(f"  - Adding column: {column_name} ({column_type})")
                            try:
                                connection.execute(text(alter_stmt))
                                print(f"    SUCCESS: Added column {column_name} to table {table_name}")
                            except Exception as e:
                                print(f"    ERROR: Failed to add column {column_name}: {e}")
                    else:
                        print(f"No missing columns in table {table_name}")
            
            # Commit all changes
            connection.commit()
            print("\nDatabase synchronization completed successfully!")
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"ERROR: Failed to synchronize database: {e}")
            return False

if __name__ == "__main__":
    print("Starting database synchronization...")
    success = sync_database()
    
    if success:
        print("Database synchronized successfully!")
        sys.exit(0)
    else:
        print("Database synchronization failed!")
        sys.exit(1)

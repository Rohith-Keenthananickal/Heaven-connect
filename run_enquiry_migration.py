"""
Script to run the enquiry table migration
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def create_enquiry_table():
    """Create the enquiries table in the database"""
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if table already exists
        try:
            result = connection.execute(text("SHOW TABLES LIKE 'enquiries'"))
            table_exists = result.rowcount > 0
            
            if table_exists:
                print("WARNING: enquiries table already exists")
                return True
                
            print("Creating enquiries table...")
            
            # Create ENUM types if they don't exist
            # For MySQL, we'll create them as part of the table
            
            # Create the table
            connection.execute(text("""
                CREATE TABLE enquiries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_name VARCHAR(200) NULL,
                    host_name VARCHAR(200) NOT NULL,
                    email VARCHAR(255) NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    alternate_phone_number VARCHAR(20) NULL,
                    dob DATE NULL,
                    gender ENUM('MALE', 'FEMALE', 'OTHER') NULL,
                    id_card_type ENUM('AADHAR', 'PAN', 'DRIVING_LICENSE', 'VOTER_ID', 'PASSPORT', 'OTHER') NULL,
                    id_card_number VARCHAR(100) NULL,
                    atp_id VARCHAR(20) NULL,
                    status ENUM('PENDING', 'PROCESSED', 'REJECTED', 'CONVERTED') NOT NULL DEFAULT 'PENDING',
                    remarks VARCHAR(500) NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes
            connection.execute(text("CREATE INDEX ix_enquiries_phone_number ON enquiries (phone_number)"))
            connection.execute(text("CREATE INDEX ix_enquiries_email ON enquiries (email)"))
            connection.execute(text("CREATE INDEX ix_enquiries_id_card_number ON enquiries (id_card_number)"))
            connection.execute(text("CREATE INDEX ix_enquiries_atp_id ON enquiries (atp_id)"))
            connection.execute(text("CREATE INDEX ix_enquiries_status ON enquiries (status)"))
            connection.execute(text("CREATE UNIQUE INDEX ux_enquiries_atp_id ON enquiries (atp_id)"))
            
            # Commit changes
            connection.commit()
            print("SUCCESS: Created enquiries table with indexes")
            
        except Exception as e:
            print(f"ERROR: Failed running migration: {e}")
            connection.rollback()
            return False
            
    return True

if __name__ == "__main__":
    success = create_enquiry_table()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)

"""
Database migration script to create profile tables for class table inheritance.

This script creates the new tables:
- guests
- hosts  
- area_coordinators (enhanced with new fields and approval status)
- bank_details

Run this after updating your models to create the new table structure.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_profile_tables():
    """Create the new profile tables."""
    
    with engine.connect() as connection:
        # Create guests table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY,
                passport_number VARCHAR(50),
                nationality VARCHAR(100),
                preferences JSON,
                FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Create hosts table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS hosts (
                id INTEGER PRIMARY KEY,
                license_number VARCHAR(100),
                experience_years INTEGER,
                company_name VARCHAR(200),
                FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Create enhanced area_coordinators table with approval status
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS area_coordinators (
                id INTEGER PRIMARY KEY,
                region VARCHAR(200),
                assigned_properties INTEGER DEFAULT 0,
                approval_status VARCHAR(20) DEFAULT 'PENDING' NOT NULL,
                approval_date TIMESTAMP WITH TIME ZONE,
                approved_by INTEGER,
                rejection_reason VARCHAR(500),
                id_proof_type VARCHAR(50),
                id_proof_number VARCHAR(100),
                pancard_number VARCHAR(20),
                passport_size_photo VARCHAR(500),
                id_proof_document VARCHAR(500),
                address_proof_document VARCHAR(500),
                district VARCHAR(100),
                panchayat VARCHAR(100),
                address_line1 VARCHAR(200),
                address_line2 VARCHAR(200),
                city VARCHAR(100),
                state VARCHAR(100),
                postal_code VARCHAR(20),
                latitude FLOAT,
                longitude FLOAT,
                emergency_contact VARCHAR(20),
                emergency_contact_name VARCHAR(100),
                emergency_contact_relationship VARCHAR(50),
                FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """))
        
        # Create bank_details table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS bank_details (
                id INTEGER PRIMARY KEY,
                area_coordinator_id INTEGER UNIQUE NOT NULL,
                bank_name VARCHAR(200) NOT NULL,
                account_holder_name VARCHAR(200) NOT NULL,
                account_number VARCHAR(50) NOT NULL,
                ifsc_code VARCHAR(20) NOT NULL,
                branch_name VARCHAR(200),
                branch_code VARCHAR(20),
                account_type VARCHAR(50),
                is_verified BOOLEAN DEFAULT FALSE,
                bank_passbook_image VARCHAR(500),
                cancelled_cheque_image VARCHAR(500),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                FOREIGN KEY (area_coordinator_id) REFERENCES area_coordinators(id) ON DELETE CASCADE
            )
        """))
        
        # Create indexes for better performance
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_guests_passport ON guests(passport_number)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_hosts_license ON hosts(license_number)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_coordinators_region ON area_coordinators(region)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_coordinators_district ON area_coordinators(district)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_coordinators_panchayat ON area_coordinators(panchayat)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_coordinators_id_proof ON area_coordinators(id_proof_number)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_coordinators_pancard ON area_coordinators(pancard_number)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_coordinators_approval_status ON area_coordinators(approval_status)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_coordinators_approved_by ON area_coordinators(approved_by)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_bank_details_account ON bank_details(account_number)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_bank_details_ifsc ON bank_details(ifsc_code)"))
        
        connection.commit()
        print("Profile tables created successfully!")


def drop_profile_tables():
    """Drop the profile tables (use with caution!)."""
    
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS bank_details"))
        connection.execute(text("DROP TABLE IF EXISTS area_coordinators"))
        connection.execute(text("DROP TABLE IF EXISTS hosts"))
        connection.execute(text("DROP TABLE IF EXISTS guests"))
        connection.commit()
        print("Profile tables dropped successfully!")


def migrate_existing_users():
    """
    Migrate existing users to have profile records based on their user_type.
    
    This is a basic migration - you may need to customize based on your data.
    """
    
    db = SessionLocal()
    try:
        # Get all users
        result = db.execute(text("SELECT id, user_type FROM users"))
        users = result.fetchall()
        
        for user_id, user_type in users:
            if user_type == "GUEST":
                # Check if guest profile already exists
                existing = db.execute(text("SELECT id FROM guests WHERE id = :user_id"), {"user_id": user_id}).first()
                if not existing:
                    db.execute(text("""
                        INSERT INTO guests (id, passport_number, nationality, preferences)
                        VALUES (:user_id, NULL, NULL, '{}')
                    """), {"user_id": user_id})
                    
            elif user_type == "HOST":
                # Check if host profile already exists
                existing = db.execute(text("SELECT id FROM hosts WHERE id = :user_id"), {"user_id": user_id}).first()
                if not existing:
                    db.execute(text("""
                        INSERT INTO hosts (id, license_number, experience_years, company_name)
                        VALUES (:user_id, NULL, NULL, NULL)
                    """), {"user_id": user_id})
                    
            elif user_type == "AREA_COORDINATOR":
                # Check if area coordinator profile already exists
                existing = db.execute(text("SELECT id FROM area_coordinators WHERE id = :user_id"), {"user_id": user_id}).first()
                if not existing:
                    db.execute(text("""
                        INSERT INTO area_coordinators (id, region, assigned_properties, approval_status, district, panchayat, address_line1, city, state, postal_code)
                        VALUES (:user_id, 'Default Region', 0, 'PENDING', 'Default District', 'Default Panchayat', 'Default Address', 'Default City', 'Default State', '000000')
                    """), {"user_id": user_id})
        
        db.commit()
        print("Existing users migrated successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("User Profile Tables Migration")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. Create profile tables")
        print("2. Migrate existing users")
        print("3. Drop profile tables (DANGEROUS!)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            create_profile_tables()
        elif choice == "2":
            migrate_existing_users()
        elif choice == "3":
            confirm = input("Are you sure you want to drop all profile tables? (yes/no): ").strip().lower()
            if confirm == "yes":
                drop_profile_tables()
            else:
                print("Operation cancelled.")
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

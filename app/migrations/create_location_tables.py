"""
Database migration script to create location tables for districts and grama panchayats.

This script creates the new tables:
- districts
- grama_panchayats

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


def create_location_tables():
    """Create the new location tables."""
    
    with engine.connect() as connection:
        # Create districts table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS districts (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(200) NOT NULL UNIQUE,
                state VARCHAR(100) NOT NULL,
                code VARCHAR(20) UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_districts_name (name),
                INDEX idx_districts_state (state),
                INDEX idx_districts_code (code),
                INDEX idx_districts_active (is_active)
            )
        """))
        
        # Create grama_panchayats table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS grama_panchayats (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(200) NOT NULL,
                district_id INTEGER NOT NULL,
                code VARCHAR(20) UNIQUE,
                description TEXT,
                population INTEGER,
                area_sq_km FLOAT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
                INDEX idx_grama_panchayats_name (name),
                INDEX idx_grama_panchayats_district_id (district_id),
                INDEX idx_grama_panchayats_code (code),
                INDEX idx_grama_panchayats_active (is_active)
            )
        """))
        
        print("Location tables created successfully!")
        
        # Insert some sample data for testing
        insert_sample_data(connection)


def insert_sample_data(connection):
    """Insert sample data for testing purposes."""
    
    # Insert sample districts
    sample_districts = [
        ("Thiruvananthapuram", "Kerala", "TVM", "Capital district of Kerala"),
        ("Ernakulam", "Kerala", "EKM", "Commercial capital of Kerala"),
        ("Kozhikode", "Kerala", "KZK", "Cultural capital of Kerala"),
        ("Mysuru", "Karnataka", "MYS", "Cultural capital of Karnataka"),
        ("Bangalore Urban", "Karnataka", "BLR", "Capital of Karnataka"),
        ("Chennai", "Tamil Nadu", "CHN", "Capital of Tamil Nadu"),
        ("Coimbatore", "Tamil Nadu", "CBE", "Manchester of South India")
    ]
    
    for district in sample_districts:
        connection.execute(text("""
            INSERT IGNORE INTO districts (name, state, code, description) 
            VALUES (:name, :state, :code, :description)
        """), {
            "name": district[0],
            "state": district[1],
            "code": district[2],
            "description": district[3]
        })
    
    # Insert sample grama panchayats
    sample_panchayats = [
        ("Kovalam", 1, "KVL", "Famous beach destination", 15000, 25.5),
        ("Varkala", 1, "VRK", "Cliff beach and spiritual center", 12000, 20.0),
        ("Fort Kochi", 2, "FKC", "Historic port area", 25000, 15.0),
        ("Mattancherry", 2, "MTC", "Jew Town and spice trade center", 18000, 12.5),
        ("Beypore", 3, "BYP", "Traditional shipbuilding center", 22000, 30.0),
        ("Kappad", 3, "KPD", "Historic landing site of Vasco da Gama", 8000, 8.0),
        ("Srirangapatna", 4, "SRP", "Historic island town", 35000, 45.0),
        ("Nanjangud", 4, "NJD", "Temple town and industrial center", 42000, 50.0),
        ("Electronic City", 5, "ELC", "IT hub of Bangalore", 15000, 10.0),
        ("Whitefield", 5, "WTF", "International tech park area", 20000, 15.0),
        ("Mylapore", 6, "MLP", "Traditional cultural center", 28000, 18.0),
        ("T Nagar", 6, "TNG", "Shopping and commercial hub", 35000, 22.0),
        ("Singanallur", 7, "SGL", "Industrial and residential area", 32000, 28.0),
        ("Peelamedu", 7, "PLM", "Educational and residential hub", 25000, 20.0)
    ]
    
    for panchayat in sample_panchayats:
        connection.execute(text("""
            INSERT IGNORE INTO grama_panchayats (name, district_id, code, description, population, area_sq_km) 
            VALUES (:name, :district_id, :code, :description, :population, :area_sq_km)
        """), {
            "name": panchayat[0],
            "district_id": panchayat[1],
            "code": panchayat[2],
            "description": panchayat[3],
            "population": panchayat[4],
            "area_sq_km": panchayat[5]
        })
    
    print("Sample data inserted successfully!")


def drop_location_tables():
    """Drop the location tables (use with caution!)."""
    
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS grama_panchayats"))
        connection.execute(text("DROP TABLE IF EXISTS districts"))
        print("Location tables dropped successfully!")


if __name__ == "__main__":
    print("Creating location tables...")
    create_location_tables()
    print("Migration completed successfully!")
    
    # Uncomment the line below if you want to drop the tables
    # drop_location_tables()

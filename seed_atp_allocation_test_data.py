#!/usr/bin/env python3
"""
Script to seed mock data for testing ATP auto-allocation API
Creates:
- Area Coordinator (ATP) users with different coordinates and workload
- Host users
- Properties with locations (with coordinates)

Usage:
    python seed_atp_allocation_test_data.py

Prerequisites:
    Set environment variables or modify DATABASE_URL below:
    - DATABASE_URL (or DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

This script creates:
- 5 ATP users with different locations around Kerala, India
- 5 Properties with locations spread across Kerala
- Each ATP has different workload (assigned_properties count)
- Properties are created without area_coordinator_id so you can test auto-allocation

After running, test the API with:
    PATCH /properties/property/atp-auto-allocate?property_id=<property_id>
"""

import os
import sys
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import random

# Try to get database URL from environment or use defaults
def get_database_url():
    """Get database URL from environment or construct from components"""
    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed, continue without it
    
    # First try to get DATABASE_URL directly
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Handle URL encoding - if password is already encoded, use as is
        return database_url
    
    # Construct from individual components if DATABASE_URL not set
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_name = os.getenv("DB_NAME", "heaven_connect")
    
    # URL encode the password if it contains special characters
    from urllib.parse import quote_plus
    encoded_password = quote_plus(db_password)
    
    return f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"


def create_db_session():
    """Create database session directly without importing app.config"""
    database_url = get_database_url()
    
    # Create engine
    engine = create_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20
    )
    
    # Create session maker
    SessionLocal = sessionmaker(
        bind=engine,
        expire_on_commit=False
    )
    
    return SessionLocal()


def seed_test_data():
    """Seed test data for ATP auto-allocation"""
    
    # Import models after we have the session
    try:
        from app.models.user import User, AreaCoordinator, UserType, UserStatus, AuthProvider, ApprovalStatus
        from app.models.property import Property, Location, PropertyStatus, PropertyVerificationStatus, PropertyClassification, PropertyType
    except ImportError as e:
        print("=" * 60)
        print("ERROR: Failed to import models")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nPlease ensure you're running from the project root directory.")
        print("=" * 60)
        sys.exit(1)
    
    db: Session = create_db_session()
    
    try:
        print("Starting to seed ATP allocation test data...")
        print(f"Database URL: {get_database_url().split('@')[1] if '@' in get_database_url() else 'configured'}\n")
        
        # Kerala, India coordinates (central point)
        # We'll create ATPs and properties around Kerala
        base_lat = 10.8505  # Kochi area
        base_lon = 76.2711
        
        # Create 5 ATP users with different coordinates and workloads
        atp_users = []
        atp_coordinates = [
            # ATP 1: Near Kochi (base location) - 0 properties
            {"lat": 10.8505, "lon": 76.2711, "name": "ATP Kochi Central", "workload": 0},
            # ATP 2: Trivandrum area - 2 properties
            {"lat": 8.5241, "lon": 76.9366, "name": "ATP Trivandrum", "workload": 2},
            # ATP 3: Kozhikode area - 1 property
            {"lat": 11.2588, "lon": 75.7804, "name": "ATP Kozhikode", "workload": 1},
            # ATP 4: Munnar area - 3 properties
            {"lat": 10.0889, "lon": 77.0595, "name": "ATP Munnar", "workload": 3},
            # ATP 5: Alleppey area - 0 properties
            {"lat": 9.4981, "lon": 76.3388, "name": "ATP Alleppey", "workload": 0},
        ]
        
        print("Creating ATP users...")
        for idx, atp_data in enumerate(atp_coordinates, 1):
            # Create User for ATP
            email = f"atp{idx}@heavenconnect.test"
            phone = f"9876543{idx:03d}"
            atp_uuid = f"ATP-{idx:05d}"
            
            # Check if ATP UUID already exists
            existing_atp = db.query(AreaCoordinator).filter(
                AreaCoordinator.atp_uuid == atp_uuid
            ).first()
            
            if existing_atp:
                print(f"  ATP {idx} with UUID {atp_uuid} already exists, skipping...")
                existing_user = db.query(User).filter(User.id == existing_atp.id).first()
                if existing_user:
                    atp_users.append(existing_user)
                continue
            
            # Check if user already exists by email/phone
            existing_user = db.query(User).filter(
                (User.email == email) | (User.phone_number == phone)
            ).first()
            
            if existing_user:
                print(f"  ATP user {idx} already exists, skipping...")
                atp_users.append(existing_user)
                continue
            
            user = User(
                auth_provider=AuthProvider.EMAIL,
                user_type=UserType.AREA_COORDINATOR,
                email=email,
                email_verified=True,
                phone_number=phone,
                country_code="+91",
                phone_verified=True,
                password_hash="$2b$12$dummyhash",  # Dummy hash for testing
                full_name=atp_data["name"],
                status=UserStatus.ACTIVE
            )
            db.add(user)
            db.flush()  # Get the user ID
            
            # Create AreaCoordinator profile
            area_coordinator = AreaCoordinator(
                id=user.id,
                atp_uuid=atp_uuid,
                application_number=f"APP-{idx:04d}",
                region=f"Region {idx}",
                assigned_properties=atp_data["workload"],
                approval_status=ApprovalStatus.APPROVED,
                approval_date=datetime.now(),
                latitude=atp_data["lat"],
                longitude=atp_data["lon"],
                district=f"District {idx}",
                city=f"City {idx}",
                state="Kerala",
                postal_code=f"68{idx:03d}",
                address_line1=f"ATP Office Address {idx}",
                business_name=f"{atp_data['name']} Business",
                id_proof_type="Aadhar",
                id_proof_number=f"1234{idx:08d}",
                pancard_number=f"ABCDE{idx:04d}F"
            )
            db.add(area_coordinator)
            atp_users.append(user)
            print(f"  Created ATP {idx}: {atp_data['name']} at ({atp_data['lat']}, {atp_data['lon']}) with {atp_data['workload']} properties")
        
        db.commit()
        print(f"Created {len(atp_users)} ATP users\n")
        
        # Create Host users and Properties
        print("Creating Host users and Properties...")
        
        # Property locations - spread around Kerala
        property_locations = [
            # Property 1: Near Kochi (should match with ATP 1 or 5)
            {"lat": 10.8600, "lon": 76.2800, "name": "Kochi Beach Villa"},
            # Property 2: Between Trivandrum and Kochi
            {"lat": 9.5000, "lon": 76.5000, "name": "Midway Resort"},
            # Property 3: Near Munnar (should match with ATP 4)
            {"lat": 10.1000, "lon": 77.1000, "name": "Munnar Hill Station"},
            # Property 4: Near Alleppey (should match with ATP 5)
            {"lat": 9.5200, "lon": 76.3500, "name": "Alleppey Backwater"},
            # Property 5: Far from all ATPs (to test 50km radius)
            {"lat": 11.5000, "lon": 75.5000, "name": "Northern Property"},
        ]
        
        created_properties = []
        
        for idx, prop_data in enumerate(property_locations, 1):
            # Create Host User
            host_email = f"host{idx}@heavenconnect.test"
            host_phone = f"9876544{idx:03d}"
            
            # Check if host user already exists
            existing_host = db.query(User).filter(
                (User.email == host_email) | (User.phone_number == host_phone)
            ).first()
            
            if existing_host:
                print(f"  Host user {idx} already exists, using existing...")
                host_user = existing_host
            else:
                host_user = User(
                    auth_provider=AuthProvider.EMAIL,
                    user_type=UserType.HOST,
                    email=host_email,
                    email_verified=True,
                    phone_number=host_phone,
                    country_code="+91",
                    phone_verified=True,
                    password_hash="$2b$12$dummyhash",
                    full_name=f"Host {idx}",
                    status=UserStatus.ACTIVE
                )
                db.add(host_user)
                db.flush()
            
            # Create Property
            # Check if property already exists for this user
            existing_property = db.query(Property).filter(
                Property.user_id == host_user.id
            ).first()
            
            if existing_property:
                print(f"  Property {idx} already exists for host {idx}, skipping...")
                created_properties.append(existing_property)
                continue
            
            # Get first property type if available, otherwise None
            property_type = db.query(PropertyType).filter(PropertyType.is_active == True).first()
            property_type_id = property_type.id if property_type else None
            
            property_obj = Property(
                user_id=host_user.id,
                property_name=prop_data["name"],
                alternate_phone=f"9876545{idx:03d}",
                property_type_id=property_type_id,
                classification=PropertyClassification.SILVER,
                status=PropertyStatus.ACTIVE,
                verification_status=PropertyVerificationStatus.DRAFT,
                progress_step=7,  # Location step completed
                is_verified=False
            )
            db.add(property_obj)
            db.flush()
            
            # Create Location for Property
            # Check if latitude/longitude columns exist in the database
            from sqlalchemy import inspect
            inspector = inspect(db.bind)
            location_columns = [col['name'] for col in inspector.get_columns('location')]
            has_coords = 'latitude' in location_columns and 'longitude' in location_columns
            
            if has_coords:
                location = Location(
                    property_id=property_obj.id,
                    address=f"{prop_data['name']}, Kerala, India",
                    google_map_link=f"https://maps.google.com/?q={prop_data['lat']},{prop_data['lon']}",
                    latitude=prop_data["lat"],
                    longitude=prop_data["lon"],
                    floor="Ground Floor",
                    elderly_friendly=random.choice([True, False]),
                    nearby_airport="Cochin International Airport",
                    distance_to_airport=f"{random.randint(20, 50)} km",
                    nearest_railway_station=f"Station {idx}",
                    distance_to_railway_station=f"{random.randint(5, 15)} km",
                    nearest_bus_stand=f"Bus Stand {idx}",
                    distance_to_bus_stand=f"{random.randint(1, 5)} km"
                )
            else:
                print(f"    Warning: latitude/longitude columns not found in location table. Coordinates not set.")
                print(f"    Note: You may need to run database migrations to add these columns for ATP auto-allocation to work.")
                # Create location without coordinates using raw SQL to avoid model field issues
                from sqlalchemy import text
                db.execute(text("""
                    INSERT INTO location (property_id, address, google_map_link, floor, elderly_friendly, 
                                         nearby_airport, distance_to_airport, nearest_railway_station, 
                                         distance_to_railway_station, nearest_bus_stand, distance_to_bus_stand)
                    VALUES (:property_id, :address, :google_map_link, :floor, :elderly_friendly,
                            :nearby_airport, :distance_to_airport, :nearest_railway_station,
                            :distance_to_railway_station, :nearest_bus_stand, :distance_to_bus_stand)
                """), {
                    "property_id": property_obj.id,
                    "address": f"{prop_data['name']}, Kerala, India",
                    "google_map_link": f"https://maps.google.com/?q={prop_data['lat']},{prop_data['lon']}",
                    "floor": "Ground Floor",
                    "elderly_friendly": random.choice([True, False]),
                    "nearby_airport": "Cochin International Airport",
                    "distance_to_airport": f"{random.randint(20, 50)} km",
                    "nearest_railway_station": f"Station {idx}",
                    "distance_to_railway_station": f"{random.randint(5, 15)} km",
                    "nearest_bus_stand": f"Bus Stand {idx}",
                    "distance_to_bus_stand": f"{random.randint(1, 5)} km"
                })
                location = None  # Skip adding to session since we used raw SQL
            if location:
                db.add(location)
            created_properties.append(property_obj)
            print(f"  Created Property {idx}: {prop_data['name']} at ({prop_data['lat']}, {prop_data['lon']})")
        
        db.commit()
        print(f"\nCreated {len(created_properties)} properties with locations\n")
        
        # Print summary
        print("=" * 60)
        print("SEEDING SUMMARY")
        print("=" * 60)
        print(f"\nATPs Created: {len(atp_users)}")
        for i, atp_user in enumerate(atp_users, 1):
            atp_profile = db.query(AreaCoordinator).filter(AreaCoordinator.id == atp_user.id).first()
            if atp_profile:
                print(f"  {i}. {atp_user.full_name} (ATP-{i:05d})")
                print(f"     Location: ({atp_profile.latitude}, {atp_profile.longitude})")
                print(f"     Assigned Properties: {atp_profile.assigned_properties}")
                print(f"     Status: {atp_profile.approval_status.value}")
        
        print(f"\nProperties Created: {len(created_properties)}")
        for i, prop in enumerate(created_properties, 1):
            # Use raw SQL to query location to avoid model field issues
            from sqlalchemy import text
            location_result = db.execute(
                text("SELECT property_id, address FROM location WHERE property_id = :property_id"),
                {"property_id": prop.id}
            ).first()
            
            print(f"  {i}. {prop.property_name} (ID: {prop.id})")
            if location_result:
                print(f"     Address: {location_result.address}")
            print(f"     Area Coordinator: {prop.area_coordinator_id or 'Not assigned'}")
        
        print("\n" + "=" * 60)
        print("Test the API with:")
        print("PATCH /properties/property/atp-auto-allocate?property_id=<property_id>")
        print("=" * 60)
        print("\nSeeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        # Check for common database connection errors
        if "Access denied" in error_msg or "1045" in error_msg:
            print("=" * 60)
            print("DATABASE CONNECTION ERROR")
            print("=" * 60)
            print("The script cannot connect to the database with the provided credentials.")
            print(f"\nCurrent database URL: {get_database_url().split('@')[1] if '@' in get_database_url() else 'configured'}")
            print("\nTo fix this:")
            print("1. Set environment variables:")
            print("   - DATABASE_URL (full connection string)")
            print("   - OR set: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME")
            print("2. Or create a .env file in the project root with:")
            print("   DATABASE_URL=mysql+pymysql://user:password@host:port/database")
            print("3. Ensure MySQL is running and the database exists")
            print("=" * 60)
        else:
            print(f"Error seeding test data: {e}")
            import traceback
            traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed_test_data()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

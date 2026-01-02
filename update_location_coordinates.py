#!/usr/bin/env python3
"""
Script to update existing location records with coordinates
This will populate latitude and longitude for properties that were created before the columns were added
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SyncSessionLocal

# Property locations - spread around Kerala (same as seed script)
property_coordinates = {
    3: {"lat": 10.8600, "lon": 76.2800},  # Kochi Beach Villa
    4: {"lat": 9.5000, "lon": 76.5000},   # Midway Resort
    5: {"lat": 10.1000, "lon": 77.1000},  # Munnar Hill Station
    6: {"lat": 9.5200, "lon": 76.3500},   # Alleppey Backwater
    7: {"lat": 11.5000, "lon": 75.5000},  # Northern Property
}

def update_coordinates():
    """Update location coordinates for existing properties"""
    
    db: Session = SyncSessionLocal()
    
    try:
        print("Updating location coordinates for existing properties...")
        
        for property_id, coords in property_coordinates.items():
            # Check if location exists for this property
            location_exists = db.execute(
                text("SELECT COUNT(*) FROM location WHERE property_id = :property_id"),
                {"property_id": property_id}
            ).scalar()
            
            if location_exists:
                # Update coordinates
                db.execute(
                    text("""
                        UPDATE location 
                        SET latitude = :lat, longitude = :lon 
                        WHERE property_id = :property_id
                    """),
                    {
                        "property_id": property_id,
                        "lat": coords["lat"],
                        "lon": coords["lon"]
                    }
                )
                print(f"  Updated coordinates for property {property_id}: ({coords['lat']}, {coords['lon']})")
            else:
                print(f"  Property {property_id} has no location record")
        
        db.commit()
        print("\nCoordinates updated successfully!")
        print("\nYou can now test the ATP auto-allocation API:")
        print("PATCH /properties/property/atp-auto-allocate?property_id=<property_id>")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating coordinates: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_coordinates()


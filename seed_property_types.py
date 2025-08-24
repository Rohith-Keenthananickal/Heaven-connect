#!/usr/bin/env python3
"""
Script to seed initial property types for the Heaven Connect platform
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import engine
from app.models.property import PropertyType
from app.services.property_service import PropertyTypeService
from app.schemas.property import PropertyTypeCreate


async def seed_property_types():
    """Seed initial property types"""
    
    # Initial property types
    property_types_data = [
        {
            "name": "Backwater & Scenic",
            "description": "Properties located near backwaters, lakes, rivers, and scenic natural landscapes"
        },
        {
            "name": "Hill Stations & Wildlife",
            "description": "Properties in hill stations, mountains, and wildlife sanctuaries"
        },
        {
            "name": "Beaches & Coastal",
            "description": "Properties near beaches, coastal areas, and sea views"
        },
        {
            "name": "Heritage & Cultural",
            "description": "Properties in heritage sites, cultural centers, and historical locations"
        },
        {
            "name": "Adventure & Sports",
            "description": "Properties near adventure sports locations, trekking trails, and outdoor activities"
        },
        {
            "name": "Wellness & Spa",
            "description": "Properties focused on wellness, spa, yoga, and meditation"
        },
        {
            "name": "Business & Corporate",
            "description": "Properties suitable for business travelers and corporate events"
        },
        {
            "name": "Family & Kids",
            "description": "Family-friendly properties with activities for children"
        },
        {
            "name": "Luxury & Premium",
            "description": "High-end luxury properties with premium amenities"
        },
        {
            "name": "Budget & Backpacker",
            "description": "Affordable properties for budget travelers and backpackers"
        }
    ]
    
    try:
        print("Starting to seed property types...")
        
        # Create async session
        async with engine.begin() as conn:
            # For seeding, we'll use raw SQL since PropertyTypeService expects sync Session
            # This is a workaround for the seeding script
            for type_data in property_types_data:
                # Check if property type already exists
                result = await conn.execute(
                    text("SELECT id FROM property_types WHERE name = :name"),
                    {"name": type_data["name"]}
                )
                existing = result.fetchone()
                
                if existing:
                    print(f"Property type '{type_data['name']}' already exists, skipping...")
                    continue
                
                # Create property type using raw SQL
                await conn.execute(
                    text("""
                        INSERT INTO property_types (name, description, is_active, created_at, updated_at)
                        VALUES (:name, :description, :is_active, NOW(), NOW())
                    """),
                    {
                        "name": type_data["name"],
                        "description": type_data["description"],
                        "is_active": True
                    }
                )
                print(f"Created property type: {type_data['name']}")
        
        print("Property types seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding property types: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_property_types())

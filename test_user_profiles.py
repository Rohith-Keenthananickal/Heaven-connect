#!/usr/bin/env python3
"""
Test script for the new user profile functionality.

This script demonstrates:
1. Creating users with different profile types
2. Updating user profiles
3. Querying users with profiles
4. Error handling for invalid operations

Run this after setting up your database and running the migration.
"""

import asyncio
import json
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, Guest, Host, AreaCoordinator, UserType, AuthProvider, UserStatus
from app.services.users_service import users_service


async def test_create_guest_user():
    """Test creating a guest user with profile"""
    print("\n=== Testing Guest User Creation ===")
    
    async for db in get_db():
        try:
            # Create guest user data
            guest_data = {
                "auth_provider": AuthProvider.EMAIL,
                "user_type": UserType.GUEST,
                "email": "test.guest@example.com",
                "phone_number": "+1234567890",
                "full_name": "Test Guest User",
                "dob": date(1990, 5, 15),
                "status": UserStatus.ACTIVE,
                "password": "testpassword123",
                "guest_profile": {
                    "passport_number": "TEST123456",
                    "nationality": "US",
                    "preferences": {
                        "preferred_style": "modern",
                        "max_price": 2000,
                        "amenities": ["wifi", "parking"]
                    }
                }
            }
            
            # Create user
            user = await users_service.create(db, obj_in=guest_data)
            
            print(f"✅ Guest user created successfully!")
            print(f"   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   User Type: {user.user_type}")
            print(f"   Profile ID: {user.guest_profile.id if user.guest_profile else 'None'}")
            print(f"   Passport: {user.guest_profile.passport_number if user.guest_profile else 'None'}")
            
            return user
            
        except Exception as e:
            print(f"❌ Failed to create guest user: {e}")
            return None


async def test_create_host_user():
    """Test creating a host user with profile"""
    print("\n=== Testing Host User Creation ===")
    
    async for db in get_db():
        try:
            # Create host user data
            host_data = {
                "auth_provider": AuthProvider.EMAIL,
                "user_type": UserType.HOST,
                "email": "test.host@example.com",
                "phone_number": "+0987654321",
                "full_name": "Test Host User",
                "dob": date(1985, 8, 22),
                "status": UserStatus.ACTIVE,
                "password": "hostpassword456",
                "host_profile": {
                    "license_number": "HOST_TEST_123",
                    "experience_years": 5,
                    "company_name": "Test Properties LLC"
                }
            }
            
            # Create user
            user = await users_service.create(db, obj_in=host_data)
            
            print(f"✅ Host user created successfully!")
            print(f"   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   User Type: {user.user_type}")
            print(f"   Profile ID: {user.host_profile.id if user.host_profile else 'None'}")
            print(f"   License: {user.host_profile.license_number if user.host_profile else 'None'}")
            print(f"   Experience: {user.host_profile.experience_years if user.host_profile else 'None'} years")
            
            return user
            
        except Exception as e:
            print(f"❌ Failed to create host user: {e}")
            return None


async def test_create_area_coordinator_user():
    """Test creating an area coordinator user with profile"""
    print("\n=== Testing Area Coordinator User Creation ===")
    
    async for db in get_db():
        try:
            # Create area coordinator user data
            coordinator_data = {
                "auth_provider": AuthProvider.EMAIL,
                "user_type": UserType.AREA_COORDINATOR,
                "email": "test.coordinator@example.com",
                "phone_number": "+1122334455",
                "full_name": "Test Coordinator User",
                "dob": date(1978, 12, 10),
                "status": UserStatus.ACTIVE,
                "password": "coordinator789",
                "area_coordinator_profile": {
                    "region": "Test District",
                    "assigned_properties": 0
                }
            }
            
            # Create user
            user = await users_service.create(db, obj_in=coordinator_data)
            
            print(f"✅ Area Coordinator user created successfully!")
            print(f"   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   User Type: {user.user_type}")
            print(f"   Profile ID: {user.area_coordinator_profile.id if user.area_coordinator_profile else 'None'}")
            print(f"   Region: {user.area_coordinator_profile.region if user.area_coordinator_profile else 'None'}")
            
            return user
            
        except Exception as e:
            print(f"❌ Failed to create area coordinator user: {e}")
            return None


async def test_update_user_profile(guest_user: User):
    """Test updating a user's profile"""
    print("\n=== Testing Profile Update ===")
    
    async for db in get_db():
        try:
            # Update guest preferences
            profile_update = {
                "preferences": {
                    "preferred_style": "luxury",
                    "max_price": 3500,
                    "amenities": ["wifi", "parking", "pool", "gym"],
                    "location_preference": "beachfront"
                }
            }
            
            result = await users_service.update_profile(
                db, guest_user.id, profile_update, UserType.GUEST
            )
            
            print(f"✅ Profile updated successfully!")
            print(f"   Profile Type: {result['type']}")
            print(f"   New Max Price: {result['profile'].preferences.get('max_price')}")
            print(f"   New Amenities: {result['profile'].preferences.get('amenities')}")
            
        except Exception as e:
            print(f"❌ Failed to update profile: {e}")


async def test_query_users_with_profiles():
    """Test querying users with their profiles"""
    print("\n=== Testing User Queries ===")
    
    async for db in get_db():
        try:
            # Get all users
            users = await users_service.get_multi(db, skip=0, limit=10)
            
            print(f"✅ Found {len(users)} users:")
            
            for user in users:
                print(f"   User {user.id}: {user.full_name} ({user.user_type.value})")
                
                if user.guest_profile:
                    print(f"     Guest Profile: Passport {user.guest_profile.passport_number}")
                elif user.host_profile:
                    print(f"     Host Profile: License {user.host_profile.license_number}")
                elif user.area_coordinator_profile:
                    print(f"     Coordinator Profile: Region {user.area_coordinator_profile.region}")
                else:
                    print(f"     No Profile")
            
        except Exception as e:
            print(f"❌ Failed to query users: {e}")


async def test_get_users_by_type():
    """Test getting users by specific type"""
    print("\n=== Testing Users by Type ===")
    
    async for db in get_db():
        try:
            # Get guests
            guests = await users_service.get_users_by_type(db, UserType.GUEST, skip=0, limit=10)
            print(f"✅ Found {len(guests)} guest users")
            
            # Get hosts
            hosts = await users_service.get_users_by_type(db, UserType.HOST, skip=0, limit=10)
            print(f"✅ Found {len(hosts)} host users")
            
            # Get area coordinators
            coordinators = await users_service.get_users_by_type(db, UserType.AREA_COORDINATOR, skip=0, limit=10)
            print(f"✅ Found {len(coordinators)} area coordinator users")
            
        except Exception as e:
            print(f"❌ Failed to get users by type: {e}")


async def test_error_handling():
    """Test error handling for invalid operations"""
    print("\n=== Testing Error Handling ===")
    
    async for db in get_db():
        try:
            # Try to create guest user without profile
            invalid_guest_data = {
                "auth_provider": AuthProvider.EMAIL,
                "user_type": UserType.GUEST,
                "email": "invalid.guest@example.com",
                "full_name": "Invalid Guest User",
                "password": "testpassword123"
                # Missing guest_profile
            }
            
            await users_service.create(db, obj_in=invalid_guest_data)
            print("❌ Should have failed - missing profile")
            
        except Exception as e:
            print(f"✅ Correctly caught error: {e}")
        
        try:
            # Try to create user with multiple profiles
            invalid_multi_profile_data = {
                "auth_provider": AuthProvider.EMAIL,
                "user_type": UserType.GUEST,
                "email": "multi.profile@example.com",
                "full_name": "Multi Profile User",
                "password": "testpassword123",
                "guest_profile": {"passport_number": "TEST123", "nationality": "US"},
                "host_profile": {"license_number": "HOST123", "experience_years": 5}
            }
            
            await users_service.create(db, obj_in=invalid_multi_profile_data)
            print("❌ Should have failed - multiple profiles")
            
        except Exception as e:
            print(f"✅ Correctly caught error: {e}")


async def main():
    """Run all tests"""
    print("🚀 Starting User Profile Tests")
    print("=" * 50)
    
    # Test user creation
    guest_user = await test_create_guest_user()
    host_user = await test_create_host_user()
    coordinator_user = await test_create_area_coordinator_user()
    
    # Test profile updates
    if guest_user:
        await test_update_user_profile(guest_user)
    
    # Test queries
    await test_query_users_with_profiles()
    await test_get_users_by_type()
    
    # Test error handling
    await test_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    
    if guest_user and host_user and coordinator_user:
        print(f"\n📊 Test Summary:")
        print(f"   Guest User ID: {guest_user.id}")
        print(f"   Host User ID: {host_user.id}")
        print(f"   Coordinator User ID: {coordinator_user.id}")
        print(f"\n💡 You can now test the API endpoints with these user IDs!")


if __name__ == "__main__":
    # Run the async tests
    asyncio.run(main())

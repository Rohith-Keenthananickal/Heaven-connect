#!/usr/bin/env python3
"""
Debug script to test authentication logic
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database import get_db
from services.users_service import users_service
from models.user import AuthProvider, UserStatus
from utils.auth import verify_password, get_password_hash

async def test_authentication():
    """Test the authentication logic step by step"""
    print("🔍 Testing Authentication Logic...")
    
    # Get database session
    async for db in get_db():
        try:
            # Test email to search for
            test_email = "rajesh@example.com"  # Change this to an email that exists in your database
            
            print(f"\n📧 Looking for user with email: {test_email}")
            
            # 1. Check if user exists
            result = await db.execute(f"SELECT id, email, password_hash, status FROM users WHERE email = '{test_email}'")
            user_row = result.fetchone()
            
            if not user_row:
                print("❌ User not found in database")
                return
            
            user_id, email, password_hash, status = user_row
            print(f"✅ User found: ID={user_id}, Email={email}, Status={status}")
            print(f"🔐 Password hash exists: {bool(password_hash)}")
            print(f"🔐 Password hash length: {len(password_hash) if password_hash else 0}")
            
            # 2. Test password verification
            test_password = "password123"  # Change this to the password you're trying to use
            print(f"\n🔑 Testing password verification with: {test_password}")
            
            if password_hash:
                is_valid = verify_password(test_password, password_hash)
                print(f"🔐 Password verification result: {is_valid}")
                
                if not is_valid:
                    # Let's see what happens if we hash the test password
                    new_hash = get_password_hash(test_password)
                    print(f"🔐 New hash for test password: {new_hash}")
                    print(f"🔐 New hash length: {len(new_hash)}")
                    
                    # Test if the new hash works
                    is_valid_new = verify_password(test_password, new_hash)
                    print(f"🔐 New hash verification: {is_valid_new}")
            else:
                print("❌ No password hash found in database")
            
            # 3. Test the service method
            print(f"\n🔧 Testing users_service.authenticate_user...")
            try:
                user = await users_service.authenticate_user(db, AuthProvider.EMAIL, test_email, test_password)
                if user:
                    print(f"✅ Authentication successful: {user['id']}")
                    print(f"📋 User data: {user.keys()}")
                else:
                    print("❌ Authentication failed")
            except Exception as e:
                print(f"❌ Authentication error: {str(e)}")
                import traceback
                traceback.print_exc()
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(test_authentication())

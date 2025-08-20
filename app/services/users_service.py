from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User, AuthProvider
from app.schemas.users import UserCreate, UserUpdate
from app.services.base_service import BaseService
from app.utils.auth import get_password_hash, verify_password
from app.utils.error_handler import (
    create_http_exception,
    create_server_error_http_exception
)
from app.schemas.errors import ErrorCodes, ErrorMessages


class UsersService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user with password hashing"""
        obj_data = obj_in.dict()
        
        # Hash password if provided
        if obj_data.get("password"):
            obj_data["password_hash"] = get_password_hash(obj_data.pop("password"))
        
        # Check for existing user with same email or phone
        if obj_data.get("email"):
            existing = await db.execute(select(User).where(User.email == obj_data["email"]))
            if existing.scalar_one_or_none():
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="User with this email already exists",
                    error_code=ErrorCodes.USER_ALREADY_EXISTS
                )
        
        if obj_data.get("phone_number"):
            existing = await db.execute(select(User).where(User.phone_number == obj_data["phone_number"]))
            if existing.scalar_one_or_none():
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="User with this phone number already exists",
                    error_code=ErrorCodes.USER_ALREADY_EXISTS
                )
        
        db_obj = User(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_phone(self, db: AsyncSession, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        result = await db.execute(select(User).where(User.phone_number == phone_number))
        return result.scalar_one_or_none()

    async def get_active_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users only"""
        return await self.get_multi(db, skip=skip, limit=limit, filters={"status": True})

    async def authenticate_user(self, db: AsyncSession, auth_provider: str, identifier: str, password: Optional[str] = None) -> Optional[User]:
        """Authenticate user based on auth provider"""
        try:
            if auth_provider == AuthProvider.EMAIL:
                if not password:
                    raise create_http_exception(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Password is required for email authentication",
                        error_code=ErrorCodes.BAD_REQUEST
                    )
                user = await self.get_by_email(db, identifier)
                if user and verify_password(password, user.password_hash or ""):
                    return user
                    
            elif auth_provider == AuthProvider.MOBILE:
                user = await self.get_by_phone(db, identifier)
                if user:
                    return user
                    
            elif auth_provider == AuthProvider.GOOGLE:
                # For Google OAuth, we'll need to verify the token
                # This is a simplified version - in production you'd verify the Google token
                user = await self.get_by_email(db, identifier)
                if user:
                    return user
            
            return None
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Authentication failed: {str(e)}",
                component="user_authentication"
            )

    async def authenticate_with_otp(self, db: AsyncSession, phone_number: str, otp: str) -> Optional[User]:
        """Authenticate user with OTP"""
        try:
            # Verify OTP (you'll need to implement OTP verification logic)
            # For now, we'll just check if the user exists
            user = await self.get_by_phone(db, phone_number)
            if user:
                # TODO: Implement actual OTP verification
                return user
            return None
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"OTP authentication failed: {str(e)}",
                component="otp_authentication"
            )


users_service = UsersService()

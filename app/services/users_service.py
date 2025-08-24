from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException, status
from app.models.user import User, AuthProvider, UserStatus
from app.schemas.users import UserCreate, UserUpdate, UserSearchRequest
from app.services.base_service import BaseService
from app.utils.auth import get_password_hash, verify_password
from app.utils.error_handler import (
    create_http_exception,
    create_server_error_http_exception
)
from app.schemas.errors import ErrorCodes, ErrorMessages
from datetime import datetime


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
        return await self.get_multi(db, skip=skip, limit=limit, filters={"status": UserStatus.ACTIVE})

    async def search_users(self, db: AsyncSession, search_request: UserSearchRequest) -> dict:
        """Search users with pagination and filters"""
        try:
            # Build base query
            query = select(User)
            filters = []
            
            # Apply user type filter (array support)
            if search_request.user_type:
                if len(search_request.user_type) == 1:
                    filters.append(User.user_type == search_request.user_type[0])
                else:
                    filters.append(User.user_type.in_(search_request.user_type))
            
            # Apply status filter (array support)
            if search_request.status:
                if len(search_request.status) == 1:
                    filters.append(User.status == search_request.status[0])
                else:
                    filters.append(User.status.in_(search_request.status))
            
            # Apply date filter
            if search_request.date_filter:
                if search_request.date_filter.from_date:
                    from_date = datetime.fromtimestamp(search_request.date_filter.from_date / 1000)
                    filters.append(User.created_at >= from_date)
                
                if search_request.date_filter.to_date:
                    to_date = datetime.fromtimestamp(search_request.date_filter.to_date / 1000)
                    filters.append(User.created_at <= to_date)
            
            # Apply search query filter
            if search_request.search_query:
                search_term = f"%{search_request.search_query}%"
                filters.append(
                    or_(
                        User.full_name.ilike(search_term),
                        User.email.ilike(search_term),
                        User.phone_number.ilike(search_term)
                    )
                )
            
            # Apply all filters
            if filters:
                query = query.where(and_(*filters))
            
            # Get total count for pagination
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Calculate pagination
            total_pages = (total + search_request.limit - 1) // search_request.limit
            skip = (search_request.page - 1) * search_request.limit
            
            # Apply pagination
            query = query.offset(skip).limit(search_request.limit)
            
            # Order by created_at desc
            query = query.order_by(User.created_at.desc())
            
            # Execute query
            result = await db.execute(query)
            users = result.scalars().all()
            
            # Build pagination info
            pagination_info = {
                "page": search_request.page,
                "limit": search_request.limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": search_request.page < total_pages,
                "has_prev": search_request.page > 1
            }
            
            return {
                "users": users,
                "pagination": pagination_info
            }
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"User search failed: {str(e)}",
                component="user_search"
            )

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
                if user and user.status == UserStatus.ACTIVE and verify_password(password, user.password_hash or ""):
                    return user
                    
            elif auth_provider == AuthProvider.MOBILE:
                user = await self.get_by_phone(db, identifier)
                if user and user.status == UserStatus.ACTIVE:
                    return user
                    
            elif auth_provider == AuthProvider.GOOGLE:
                # For Google OAuth, we'll need to verify the token
                # This is a simplified version - in production you'd verify the Google token
                user = await self.get_by_email(db, identifier)
                if user and user.status == UserStatus.ACTIVE:
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
            if user and user.status == UserStatus.ACTIVE:
                # TODO: Implement actual OTP verification
                return user
            return None
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"OTP authentication failed: {str(e)}",
                component="otp_authentication"
            )

    async def soft_delete(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Soft delete user by changing status to DELETED"""
        try:
            user = await self.get(db, user_id)
            if not user:
                return None
            
            # Change status to DELETED instead of actually deleting
            user.status = UserStatus.DELETED
            await db.commit()
            await db.refresh(user)
            return user
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Failed to soft delete user: {str(e)}",
                component="user_soft_delete"
            )

    async def block_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Block user by changing status to BLOCKED"""
        try:
            user = await self.get(db, user_id)
            if not user:
                return None
            
            # Change status to BLOCKED
            user.status = UserStatus.BLOCKED
            await db.commit()
            await db.refresh(user)
            return user
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Failed to block user: {str(e)}",
                component="user_block"
            )

    async def activate_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Activate user by changing status to ACTIVE"""
        try:
            user = await self.get(db, user_id)
            if not user:
                return None
            
            # Change status to ACTIVE
            user.status = UserStatus.ACTIVE
            await db.commit()
            await db.refresh(user)
            return user
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Failed to activate user: {str(e)}",
                component="user_activate"
            )


users_service = UsersService()

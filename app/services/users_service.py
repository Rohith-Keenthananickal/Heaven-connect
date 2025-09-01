from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException, status
from app.models.user import User, Guest, Host, AreaCoordinator, BankDetails, AuthProvider, UserStatus, UserType, ApprovalStatus
from app.schemas.users import UserCreate, UserUpdate, UserSearchRequest
from app.services.base_service import BaseService
from app.utils.auth import get_password_hash, verify_password
from app.utils.error_handler import (
    create_http_exception
)
from app.schemas.errors import ErrorCodes, ErrorMessages
from datetime import datetime


class UsersService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> dict:
        """Create a new user with profile and password hashing"""
        obj_data = obj_in.dict()
        
        # Extract profile data
        guest_profile_data = obj_data.pop("guest_profile", None)
        host_profile_data = obj_data.pop("host_profile", None)
        area_coordinator_profile_data = obj_data.pop("area_coordinator_profile", None)
        
        # Validate profile data matches user_type
        await self._validate_profile_data(obj_data["user_type"], guest_profile_data, host_profile_data, area_coordinator_profile_data)
        
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
        
        # Create user
        db_obj = User(**obj_data)
        db.add(db_obj)
        await db.flush()  # Get the user ID
        
        # Create profile based on user_type
        await self._create_user_profile(
            db, db_obj.id, obj_data["user_type"],
            guest_profile_data, host_profile_data, area_coordinator_profile_data
        )
        
        # Commit the transaction
        await db.commit()
        
        # Refresh the user object to get the latest data
        await db.refresh(db_obj)
        
        # Manually load profile data to avoid additional queries
        if db_obj.user_type == UserType.GUEST:
            guest_result = await db.execute(select(Guest).where(Guest.id == db_obj.id))
            db_obj.guest_profile = guest_result.scalar_one_or_none()
        elif db_obj.user_type == UserType.HOST:
            host_result = await db.execute(select(Host).where(Host.id == db_obj.id))
            db_obj.host_profile = host_result.scalar_one_or_none()
        elif db_obj.user_type == UserType.AREA_COORDINATOR:
            coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == db_obj.id))
            db_obj.area_coordinator_profile = coordinator_result.scalar_one_or_none()
            
            # Also load bank details if they exist
            if db_obj.area_coordinator_profile:
                bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == db_obj.id))
                db_obj.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert to dictionary to avoid SQLAlchemy issues
        return self._convert_user_to_dict(db_obj)

    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate) -> dict:
        """Update user and profile data"""
        obj_data = obj_in.dict(exclude_unset=True)
        
        # Extract profile update data
        guest_profile_update = obj_data.pop("guest_profile", None)
        host_profile_update = obj_data.pop("host_profile", None)
        area_coordinator_profile_update = obj_data.pop("area_coordinator_profile", None)
        
        # Update user fields
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        # Update profile if provided
        if any([guest_profile_update, host_profile_update, area_coordinator_profile_update]):
            await self._update_user_profile(
                db, db_obj.id, db_obj.user_type,
                guest_profile_update, host_profile_update, area_coordinator_profile_update
            )
        
        await db.commit()
        
        # Refresh the user object to get the latest data
        await db.refresh(db_obj)
        
        # Manually load profile data to avoid additional queries
        if db_obj.user_type == UserType.GUEST:
            guest_result = await db.execute(select(Guest).where(Guest.id == db_obj.id))
            db_obj.guest_profile = guest_result.scalar_one_or_none()
        elif db_obj.user_type == UserType.HOST:
            host_result = await db.execute(select(Host).where(Host.id == db_obj.id))
            db_obj.host_profile = host_result.scalar_one_or_none()
        elif db_obj.user_type == UserType.AREA_COORDINATOR:
            coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == db_obj.id))
            db_obj.area_coordinator_profile = coordinator_result.scalar_one_or_none()
            
            # Also load bank details if they exist
            if db_obj.area_coordinator_profile:
                bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == db_obj.id))
                db_obj.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert to dictionary to avoid SQLAlchemy issues
        return self._convert_user_to_dict(db_obj)

    def _convert_user_to_dict(self, user: User) -> dict:
        """Convert User object to clean dictionary to avoid SQLAlchemy issues"""
        user_dict = {
            "id": user.id,
            "auth_provider": user.auth_provider,
            "user_type": user.user_type,
            "email": user.email,
            "phone_number": user.phone_number,
            "full_name": user.full_name,
            "dob": user.dob,
            "profile_image": user.profile_image,
            "status": user.status,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "guest_profile": None,
            "host_profile": None,
            "area_coordinator_profile": None
        }
        
        # Add profile data as dictionaries
        if user.user_type == UserType.GUEST and user.guest_profile:
            user_dict["guest_profile"] = {
                "id": user.guest_profile.id,
                "passport_number": user.guest_profile.passport_number,
                "nationality": user.guest_profile.nationality,
                "preferences": user.guest_profile.preferences
            }
        elif user.user_type == UserType.HOST and user.host_profile:
            user_dict["host_profile"] = {
                "id": user.host_profile.id,
                "license_number": user.host_profile.license_number,
                "experience_years": user.host_profile.experience_years,
                "company_name": user.host_profile.company_name
            }
        elif user.user_type == UserType.AREA_COORDINATOR and user.area_coordinator_profile:
            user_dict["area_coordinator_profile"] = {
                "id": user.area_coordinator_profile.id,
                "region": user.area_coordinator_profile.region,
                "assigned_properties": user.area_coordinator_profile.assigned_properties,
                "approval_status": user.area_coordinator_profile.approval_status,
                "approval_date": user.area_coordinator_profile.approval_date,
                "approved_by": user.area_coordinator_profile.approved_by,
                "rejection_reason": user.area_coordinator_profile.rejection_reason,
                "id_proof_type": user.area_coordinator_profile.id_proof_type,
                "id_proof_number": user.area_coordinator_profile.id_proof_number,
                "pancard_number": user.area_coordinator_profile.pancard_number,
                "passport_size_photo": user.area_coordinator_profile.passport_size_photo,
                "id_proof_document": user.area_coordinator_profile.id_proof_document,
                "address_proof_document": user.area_coordinator_profile.address_proof_document,
                "district": user.area_coordinator_profile.district,
                "panchayat": user.area_coordinator_profile.panchayat,
                "address_line1": user.area_coordinator_profile.address_line1,
                "address_line2": user.area_coordinator_profile.address_line2,
                "city": user.area_coordinator_profile.city,
                "state": user.area_coordinator_profile.state,
                "postal_code": user.area_coordinator_profile.postal_code,
                "latitude": user.area_coordinator_profile.latitude,
                "longitude": user.area_coordinator_profile.longitude,
                "emergency_contact": user.area_coordinator_profile.emergency_contact,
                "emergency_contact_name": user.area_coordinator_profile.emergency_contact_name,
                "emergency_contact_relationship": user.area_coordinator_profile.emergency_contact_relationship
            }
            
            # Add bank details if they exist
            if user.area_coordinator_profile.bank_details:
                user_dict["area_coordinator_profile"]["bank_details"] = {
                    "id": user.area_coordinator_profile.bank_details.id,
                    "area_coordinator_id": user.area_coordinator_profile.bank_details.area_coordinator_id,
                    "bank_name": user.area_coordinator_profile.bank_details.bank_name,
                    "account_holder_name": user.area_coordinator_profile.bank_details.account_holder_name,
                    "account_number": user.area_coordinator_profile.bank_details.account_number,
                    "ifsc_code": user.area_coordinator_profile.bank_details.ifsc_code,
                    "branch_name": user.area_coordinator_profile.bank_details.branch_name,
                    "branch_code": user.area_coordinator_profile.bank_details.branch_code,
                    "account_type": user.area_coordinator_profile.bank_details.account_type,
                    "is_verified": user.area_coordinator_profile.bank_details.is_verified,
                    "bank_passbook_image": user.area_coordinator_profile.bank_details.bank_passbook_image,
                    "cancelled_cheque_image": user.area_coordinator_profile.bank_details.cancelled_cheque_image,
                    "created_at": user.area_coordinator_profile.bank_details.created_at,
                    "updated_at": user.area_coordinator_profile.bank_details.updated_at
                }
        
        return user_dict

    def _convert_area_coordinator_to_dict(self, coordinator: AreaCoordinator, bank_details: Optional[BankDetails] = None) -> dict:
        """Convert AreaCoordinator object to clean dictionary to avoid SQLAlchemy issues"""
        coordinator_dict = {
            "id": coordinator.id,
            "region": coordinator.region,
            "assigned_properties": coordinator.assigned_properties,
            "approval_status": coordinator.approval_status,
            "approval_date": coordinator.approval_date,
            "approved_by": coordinator.approved_by,
            "rejection_reason": coordinator.rejection_reason,
            "id_proof_type": coordinator.id_proof_type,
            "id_proof_number": coordinator.id_proof_number,
            "pancard_number": coordinator.pancard_number,
            "passport_size_photo": coordinator.passport_size_photo,
            "id_proof_document": coordinator.id_proof_document,
            "address_proof_document": coordinator.address_proof_document,
            "district": coordinator.district,
            "panchayat": coordinator.panchayat,
            "address_line1": coordinator.address_line1,
            "address_line2": coordinator.address_line2,
            "city": coordinator.city,
            "state": coordinator.state,
            "postal_code": coordinator.postal_code,
            "latitude": coordinator.latitude,
            "longitude": coordinator.longitude,
            "emergency_contact": coordinator.emergency_contact,
            "emergency_contact_name": coordinator.emergency_contact_name,
            "emergency_contact_relationship": coordinator.emergency_contact_relationship,
            "bank_details": None
        }
        
        # Add bank details if they exist (passed as parameter to avoid relationship access)
        if bank_details:
            coordinator_dict["bank_details"] = {
                "id": bank_details.id,
                "area_coordinator_id": bank_details.area_coordinator_id,
                "bank_name": bank_details.bank_name,
                "account_holder_name": bank_details.account_holder_name,
                "account_number": bank_details.account_number,
                "ifsc_code": bank_details.ifsc_code,
                "branch_name": bank_details.branch_name,
                "branch_code": bank_details.branch_code,
                "account_type": bank_details.account_type,
                "is_verified": bank_details.is_verified,
                "bank_passbook_image": bank_details.bank_passbook_image,
                "cancelled_cheque_image": bank_details.cancelled_cheque_image,
                "created_at": bank_details.created_at,
                "updated_at": bank_details.updated_at
            }
        
        return coordinator_dict

    async def _validate_profile_data(self, user_type: UserType, guest_profile: dict, host_profile: dict, area_coordinator_profile: dict):
        """Validate that profile data is provided for the given user_type"""
        if user_type == UserType.GUEST and not guest_profile:
            raise create_http_exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Guest profile is required for GUEST user type",
                error_code=ErrorCodes.VALIDATION_ERROR
            )
        elif user_type == UserType.HOST and not host_profile:
            raise create_http_exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Host profile is required for HOST user type",
                error_code=ErrorCodes.VALIDATION_ERROR
            )
        elif user_type == UserType.AREA_COORDINATOR and not area_coordinator_profile:
            raise create_http_exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Area coordinator profile is required for AREA_COORDINATOR user type",
                error_code=ErrorCodes.VALIDATION_ERROR
            )
        
        # Ensure only one profile type is provided
        profile_count = sum(1 for p in [guest_profile, host_profile, area_coordinator_profile] if p is not None)
        if profile_count > 1:
            raise create_http_exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Only one profile type can be provided",
                error_code=ErrorCodes.VALIDATION_ERROR
            )

    async def _create_user_profile(self, db: AsyncSession, user_id: int, user_type: UserType, 
                                 guest_profile: dict, host_profile: dict, area_coordinator_profile: dict):
        """Create the appropriate profile for the user"""
        if user_type == UserType.GUEST and guest_profile:
            profile = Guest(id=user_id, **guest_profile)
            db.add(profile)
        elif user_type == UserType.HOST and host_profile:
            profile = Host(id=user_id, **host_profile)
            db.add(profile)
        elif user_type == UserType.AREA_COORDINATOR and area_coordinator_profile:
            profile = AreaCoordinator(id=user_id, **area_coordinator_profile)
            db.add(profile)

    async def _update_user_profile(self, db: AsyncSession, user_id: int, user_type: UserType,
                                 guest_profile_update: dict, host_profile_update: dict, area_coordinator_profile_update: dict):
        """Update the user's profile data"""
        if user_type == UserType.GUEST and guest_profile_update:
            profile = await db.execute(select(Guest).where(Guest.id == user_id))
            profile = profile.scalar_one_or_none()
            if profile:
                for field, value in guest_profile_update.items():
                    if value is not None:
                        setattr(profile, field, value)
            else:
                # Create profile if it doesn't exist
                profile = Guest(id=user_id, **guest_profile_update)
                db.add(profile)
                
        elif user_type == UserType.HOST and host_profile_update:
            profile = await db.execute(select(Host).where(Host.id == user_id))
            profile = profile.scalar_one_or_none()
            if profile:
                for field, value in host_profile_update.items():
                    if value is not None:
                        setattr(profile, field, value)
            else:
                # Create profile if it doesn't exist
                profile = Host(id=user_id, **host_profile_update)
                db.add(profile)
                
        elif user_type == UserType.AREA_COORDINATOR and area_coordinator_profile_update:
            profile = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user_id))
            profile = profile.scalar_one_or_none()
            if profile:
                for field, value in area_coordinator_profile_update.items():
                    if value is not None:
                        setattr(profile, field, value)
            else:
                # Create profile if it doesn't exist
                profile = AreaCoordinator(id=user_id, **area_coordinator_profile_update)
                db.add(profile)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[dict]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
            
        # Manually load profile relationships based on user type
        if user.user_type == UserType.GUEST:
            guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
            user.guest_profile = guest_result.scalar_one_or_none()
        elif user.user_type == UserType.HOST:
            host_result = await db.execute(select(Host).where(Host.id == user.id))
            user.host_profile = host_result.scalar_one_or_none()
        elif user.user_type == UserType.AREA_COORDINATOR:
            coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
            user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
            
            # Also load bank details if they exist
            if user.area_coordinator_profile:
                bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert to dictionary to avoid SQLAlchemy issues
        return self._convert_user_to_dict(user)

    async def get_by_phone(self, db: AsyncSession, phone_number: str) -> Optional[dict]:
        """Get user by phone number"""
        result = await db.execute(select(User).where(User.phone_number == phone_number))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
            
        # Manually load profile relationships based on user type
        if user.user_type == UserType.GUEST:
            guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
            user.guest_profile = guest_result.scalar_one_or_none()
        elif user.user_type == UserType.HOST:
            host_result = await db.execute(select(Host).where(Host.id == user.id))
            user.host_profile = host_result.scalar_one_or_none()
        elif user.user_type == UserType.AREA_COORDINATOR:
            coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
            user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
            
            # Also load bank details if they exist
            if user.area_coordinator_profile:
                bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert to dictionary to avoid SQLAlchemy issues
        return self._convert_user_to_dict(user)

    async def get_active_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[dict]:
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
                        User.email.ilike(search_term) if User.email else False,
                        User.phone_number.ilike(search_term) if User.phone_number else False
                    )
                )
            
            # Apply filters
            if filters:
                query = query.where(and_(*filters))
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            query = query.offset((search_request.page - 1) * search_request.limit).limit(search_request.limit)
            
            # Execute query
            result = await db.execute(query)
            users = result.scalars().all()
            

            
            # Manually load profile relationships for each user
            for user in users:
                try:
                    if user.user_type == UserType.GUEST:
                        guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
                        user.guest_profile = guest_result.scalar_one_or_none()
                    elif user.user_type == UserType.HOST:
                        host_result = await db.execute(select(Host).where(Host.id == user.id))
                        user.host_profile = host_result.scalar_one_or_none()
                    elif user.user_type == UserType.AREA_COORDINATOR:
                        coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
                        user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
                        
                        # Also load bank details if they exist
                        if user.area_coordinator_profile:
                            bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                            user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
                except Exception as e:
                    # Log error but continue processing other users
                    continue
            
            # Apply approval status filtering for area coordinators if specified
            if search_request.approval_status and search_request.approval_status:
                filtered_users = []
                for user in users:
                    if user.user_type == UserType.AREA_COORDINATOR and user.area_coordinator_profile:
                        if user.area_coordinator_profile.approval_status in search_request.approval_status:
                            filtered_users.append(user)
                    else:
                        # Include non-area coordinator users
                        filtered_users.append(user)
                users = filtered_users
                
                # Recalculate total for filtered results
                total = len(filtered_users)
            
            # Calculate pagination info
            total_pages = (total + search_request.limit - 1) // search_request.limit
            has_next = search_request.page < total_pages
            has_prev = search_request.page > 1
            
            pagination = {
                "page": search_request.page,
                "limit": search_request.limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
            
            # Convert users to dictionaries to avoid SQLAlchemy issues
            users_dict = [self._convert_user_to_dict(user) for user in users]
            
            return {
                "users": users_dict,
                "pagination": pagination
            }
            
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to search users: {str(e)}",
                error_code=ErrorCodes.SEARCH_FAILED
            )

    async def get(self, db: AsyncSession, id: int) -> Optional[dict]:
        """Override base get method to load profile relationships"""
        # First get the user
        user_result = await db.execute(select(User).where(User.id == id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            return None
            
        # Manually load profile relationships based on user type
        if user.user_type == UserType.GUEST:
            guest_result = await db.execute(select(Guest).where(Guest.id == id))
            user.guest_profile = guest_result.scalar_one_or_none()
        elif user.user_type == UserType.HOST:
            host_result = await db.execute(select(Host).where(Host.id == id))
            user.host_profile = host_result.scalar_one_or_none()
        elif user.user_type == UserType.AREA_COORDINATOR:
            coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == id))
            user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
            
            # Also load bank details if they exist
            if user.area_coordinator_profile:
                bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == id))
                user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert to dictionary to avoid SQLAlchemy issues
        return self._convert_user_to_dict(user)

    async def get_user_with_profile(self, db: AsyncSession, user_id: int) -> Optional[dict]:
        """Get user with their profile loaded"""
        return await self.get(db, user_id)

    async def update_profile(self, db: AsyncSession, user_id: int, profile_data: dict, user_type: UserType) -> dict:
        """Update user profile based on user type"""
        try:
            if user_type == UserType.GUEST:
                profile = await db.execute(select(Guest).where(Guest.id == user_id))
                profile = profile.scalar_one_or_none()
                if not profile:
                    raise create_http_exception(
                        status_code=status.HTTP_404_NOT_FOUND,
                        message="Guest profile not found",
                        error_code=ErrorCodes.PROFILE_NOT_FOUND
                    )
                
                for field, value in profile_data.items():
                    if value is not None:
                        setattr(profile, field, value)
                
                await db.commit()
                return {"profile": profile, "type": "guest"}
                
            elif user_type == UserType.HOST:
                profile = await db.execute(select(Host).where(Host.id == user_id))
                profile = profile.scalar_one_or_none()
                if not profile:
                    raise create_http_exception(
                        status_code=status.HTTP_404_NOT_FOUND,
                        message="Host profile not found",
                        error_code=ErrorCodes.PROFILE_NOT_FOUND
                    )
                
                for field, value in profile_data.items():
                    if value is not None:
                        setattr(profile, field, value)
                
                await db.commit()
                return {"profile": profile, "type": "host"}
                
            elif user_type == UserType.AREA_COORDINATOR:
                profile = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user_id))
                profile = profile.scalar_one_or_none()
                if not profile:
                    raise create_http_exception(
                        status_code=status.HTTP_404_NOT_FOUND,
                        message="Area coordinator profile not found",
                        error_code=ErrorCodes.PROFILE_NOT_FOUND
                    )
                
                for field, value in profile_data.items():
                    if value is not None:
                        setattr(profile, field, value)
                
                await db.commit()
                return {"profile": profile, "type": "area_coordinator"}
                
            else:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Invalid user type for profile update",
                    error_code=ErrorCodes.INVALID_USER_TYPE
                )
                
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to update profile: {str(e)}",
                error_code=ErrorCodes.PROFILE_UPDATE_FAILED
            )

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[dict]:
        """Override base get_multi method to load profile relationships"""
        # Build base query
        query = select(User)
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if hasattr(User, field) and value is not None:
                    query = query.where(getattr(User, field) == value)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Manually load profile relationships for each user
        for user in users:
            if user.user_type == UserType.GUEST:
                guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
                user.guest_profile = guest_result.scalar_one_or_none()
            elif user.user_type == UserType.HOST:
                host_result = await db.execute(select(Host).where(Host.id == user.id))
                user.host_profile = host_result.scalar_one_or_none()
            elif user.user_type == UserType.AREA_COORDINATOR:
                coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
                user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
                
                # Also load bank details if they exist
                if user.area_coordinator_profile:
                    bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                    user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert users to dictionaries to avoid SQLAlchemy issues
        return [self._convert_user_to_dict(user) for user in users]

    async def get_or_404(self, db: AsyncSession, id: int, detail: str = "User not found") -> dict:
        """Override base get_or_404 method to load profile relationships"""
        user = await self.get(db, id)
        if not user:
            raise create_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                message=detail,
                error_code=ErrorCodes.USER_NOT_FOUND
            )
        return user

    async def get_users_by_type(self, db: AsyncSession, user_type: UserType, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get users of a specific type with pagination"""
        query = select(User).where(User.user_type == user_type).offset(skip).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Manually load profile relationships for each user
        for user in users:
            if user.user_type == UserType.GUEST:
                guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
                user.guest_profile = guest_result.scalar_one_or_none()
            elif user.user_type == UserType.HOST:
                host_result = await db.execute(select(Host).where(Host.id == user.id))
                user.host_profile = host_result.scalar_one_or_none()
            elif user.user_type == UserType.AREA_COORDINATOR:
                coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
                user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
                
                # Also load bank details if they exist
                if user.area_coordinator_profile:
                    bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                    user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert users to dictionaries to avoid SQLAlchemy issues
        return [self._convert_user_to_dict(user) for user in users]

    async def activate_user(self, db: AsyncSession, user_id: int) -> Optional[dict]:
        """Activate a user (change status to ACTIVE)"""
        user = await self.get_or_404(db, user_id, "User not found")
        user.status = UserStatus.ACTIVE
        await db.commit()
        
        # Refresh the user object to get the latest data
        await db.refresh(user)
        
        # Manually attach the profile data to avoid additional queries
        if user.user_type == UserType.GUEST:
            guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
            user.guest_profile = guest_result.scalar_one_or_none()
        elif user.user_type == UserType.HOST:
            host_result = await db.execute(select(Host).where(Host.id == user.id))
            user.host_profile = host_result.scalar_one_or_none()
        elif user.user_type == UserType.AREA_COORDINATOR:
            coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
            user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
            
            # Also load bank details if they exist
            if user.area_coordinator_profile:
                bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert to dictionary to avoid SQLAlchemy issues
        return self._convert_user_to_dict(user)

    async def block_user(self, db: AsyncSession, user_id: int) -> Optional[dict]:
        """Block a user (change status to BLOCKED)"""
        user = await self.get_or_404(db, user_id, "User not found")
        user.status = UserStatus.BLOCKED
        await db.commit()
        
        # Refresh the user object to get the latest data
        await db.refresh(user)
        
        # Manually attach the profile data to avoid additional queries
        if user.user_type == UserType.GUEST:
            guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
            user.guest_profile = guest_result.scalar_one_or_none()
        elif user.user_type == UserType.HOST:
            host_result = await db.execute(select(Host).where(Host.id == user.id))
            user.host_profile = host_result.scalar_one_or_none()
        elif user.user_type == UserType.AREA_COORDINATOR:
            coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
            user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
            
            # Also load bank details if they exist
            if user.area_coordinator_profile:
                bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert to dictionary to avoid SQLAlchemy issues
        return self._convert_user_to_dict(user)

    async def soft_delete(self, db: AsyncSession, user_id: int) -> Optional[dict]:
        """Soft delete a user (change status to DELETED)"""
        user = await self.get_or_404(db, user_id, "User not found")
        user.status = UserStatus.DELETED
        await db.commit()
        
        # Refresh the user object to get the latest data
        await db.refresh(user)
        
        # Manually attach the profile data to avoid additional queries
        if user.user_type == UserType.GUEST:
            guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
            user.guest_profile = guest_result.scalar_one_or_none()
        elif user.user_type == UserType.HOST:
            host_result = await db.execute(select(Host).where(Host.id == user.id))
            user.host_profile = host_result.scalar_one_or_none()
        elif user.user_type == UserType.AREA_COORDINATOR:
            coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
            user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
            
            # Also load bank details if they exist
            if user.area_coordinator_profile:
                bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
        
        # Convert to dictionary to avoid SQLAlchemy issues
        return self._convert_user_to_dict(user)

    # Area Coordinator Approval methods
    async def approve_area_coordinator(self, db: AsyncSession, coordinator_id: int, admin_user_id: int) -> dict:
        """Approve an area coordinator"""
        try:
            # Get the area coordinator profile
            coordinator = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == coordinator_id))
            coordinator = coordinator.scalar_one_or_none()
            
            if not coordinator:
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Area coordinator not found",
                    error_code=ErrorCodes.AREA_COORDINATOR_NOT_FOUND
                )
            
            # Check if already approved
            if coordinator.approval_status == ApprovalStatus.APPROVED:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Area coordinator is already approved",
                    error_code=ErrorCodes.ALREADY_APPROVED
                )
            
            # Update approval status
            coordinator.approval_status = ApprovalStatus.APPROVED
            coordinator.approval_date = datetime.utcnow()
            coordinator.approved_by = admin_user_id
            coordinator.rejection_reason = None  # Clear any previous rejection reason
            
            await db.commit()
            await db.refresh(coordinator)
            
            # Load bank details explicitly to avoid relationship access issues
            bank_details = await db.execute(
                select(BankDetails).where(BankDetails.area_coordinator_id == coordinator.id)
            )
            bank_details = bank_details.scalar_one_or_none()
            
            # Convert to dictionary to avoid SQLAlchemy issues
            return self._convert_area_coordinator_to_dict(coordinator, bank_details)
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to approve area coordinator: {str(e)}",
                error_code=ErrorCodes.APPROVAL_FAILED
            )

    async def reject_area_coordinator(self, db: AsyncSession, coordinator_id: int, admin_user_id: int, rejection_reason: str) -> dict:
        """Reject an area coordinator"""
        try:
            # Get the area coordinator profile
            coordinator = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == coordinator_id))
            coordinator = coordinator.scalar_one_or_none()
            
            if not coordinator:
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Area coordinator not found",
                    error_code=ErrorCodes.AREA_COORDINATOR_NOT_FOUND
                )
            
            # Check if already rejected
            if coordinator.approval_status == ApprovalStatus.REJECTED:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Area coordinator is already rejected",
                    error_code=ErrorCodes.ALREADY_REJECTED
                )
            
            # Update approval status
            coordinator.approval_status = ApprovalStatus.REJECTED
            coordinator.approval_date = datetime.utcnow()
            coordinator.approved_by = admin_user_id
            coordinator.rejection_reason = rejection_reason
            
            await db.commit()
            await db.refresh(coordinator)
            
            # Load bank details explicitly to avoid relationship access issues
            bank_details = await db.execute(
                select(BankDetails).where(BankDetails.area_coordinator_id == coordinator.id)
            )
            bank_details = bank_details.scalar_one_or_none()
            
            # Convert to dictionary to avoid SQLAlchemy issues
            return self._convert_area_coordinator_to_dict(coordinator, bank_details)
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to reject area coordinator: {str(e)}",
                error_code=ErrorCodes.REJECTION_FAILED
            )

    # Bank Details methods
    async def create_bank_details(self, db: AsyncSession, area_coordinator_id: int, bank_data: dict) -> BankDetails:
        """Create bank details for an area coordinator"""
        try:
            # Check if area coordinator exists
            coordinator = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == area_coordinator_id))
            if not coordinator.scalar_one_or_none():
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Area coordinator not found",
                    error_code=ErrorCodes.AREA_COORDINATOR_NOT_FOUND
                )
            
            # Check if bank details already exist
            existing = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == area_coordinator_id))
            if existing.scalar_one_or_none():
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Bank details already exist for this area coordinator",
                    error_code=ErrorCodes.BANK_DETAILS_ALREADY_EXISTS
                )
            
            # Create bank details
            bank_details = BankDetails(area_coordinator_id=area_coordinator_id, **bank_data)
            db.add(bank_details)
            await db.commit()
            await db.refresh(bank_details)
            
            return bank_details
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to create bank details: {str(e)}",
                error_code=ErrorCodes.BANK_DETAILS_CREATION_FAILED
            )

    async def update_bank_details(self, db: AsyncSession, area_coordinator_id: int, bank_data: dict) -> BankDetails:
        """Update bank details for an area coordinator"""
        try:
            # Get existing bank details
            bank_details = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == area_coordinator_id))
            bank_details = bank_details.scalar_one_or_none()
            
            if not bank_details:
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Bank details not found",
                    error_code=ErrorCodes.BANK_DETAILS_NOT_FOUND
                )
            
            # Update fields
            for field, value in bank_data.items():
                if value is not None:
                    setattr(bank_details, field, value)
            
            await db.commit()
            await db.refresh(bank_details)
            
            return bank_details
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to update bank details: {str(e)}",
                error_code=ErrorCodes.BANK_DETAILS_UPDATE_FAILED
            )

    async def get_bank_details(self, db: AsyncSession, area_coordinator_id: int) -> Optional[BankDetails]:
        """Get bank details for an area coordinator"""
        result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == area_coordinator_id))
        return result.scalar_one_or_none()

    async def verify_bank_details(self, db: AsyncSession, area_coordinator_id: int) -> BankDetails:
        """Mark bank details as verified"""
        try:
            bank_details = await self.get_bank_details(db, area_coordinator_id)
            if not bank_details:
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Bank details not found",
                    error_code=ErrorCodes.BANK_DETAILS_NOT_FOUND
                )
            
            bank_details.is_verified = True
            await db.commit()
            await db.refresh(bank_details)
            
            return bank_details
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to verify bank details: {str(e)}",
                error_code=ErrorCodes.BANK_DETAILS_VERIFICATION_FAILED
            )


    # Authentication methods
    async def authenticate_user(self, db: AsyncSession, auth_provider: AuthProvider, identifier: str, password: str) -> Optional[dict]:
        """Authenticate user with email/phone and password"""
        try:
            # Find user by identifier (email or phone) - get raw SQLAlchemy object for password verification
            user = None
            if auth_provider == AuthProvider.EMAIL:
                result = await db.execute(select(User).where(User.email == identifier))
                user = result.scalar_one_or_none()
            elif auth_provider == AuthProvider.MOBILE:
                result = await db.execute(select(User).where(User.phone_number == identifier))
                user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Verify password using raw SQLAlchemy object
            if not verify_password(password, user.password_hash):
                return None
            
            # Check if user is active
            if user.status != UserStatus.ACTIVE:
                return None
            
            # Load profile data
            if user.user_type == UserType.GUEST:
                guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
                user.guest_profile = guest_result.scalar_one_or_none()
            elif user.user_type == UserType.HOST:
                host_result = await db.execute(select(Host).where(Host.id == user.id))
                user.host_profile = host_result.scalar_one_or_none()
            elif user.user_type == UserType.AREA_COORDINATOR:
                coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
                user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
                
                # Also load bank details if they exist
                if user.area_coordinator_profile:
                    bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                    user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
            
            # Convert to dictionary to avoid SQLAlchemy issues
            return self._convert_user_to_dict(user)
            
        except Exception as e:
            # Log error but don't expose it to user
            return None

    async def authenticate_with_otp(self, db: AsyncSession, phone_number: str, otp: str) -> Optional[dict]:
        """Authenticate user with phone number and OTP"""
        try:
            # Find user by phone number - get raw SQLAlchemy object
            result = await db.execute(select(User).where(User.phone_number == phone_number))
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # TODO: Implement OTP verification logic
            # For now, we'll just check if the user exists and is active
            # In a real implementation, you would verify the OTP against stored/expired OTPs
            
            # Check if user is active
            if user.status != UserStatus.ACTIVE:
                return None
            
            # Load profile data
            if user.user_type == UserType.GUEST:
                guest_result = await db.execute(select(Guest).where(Guest.id == user.id))
                user.guest_profile = guest_result.scalar_one_or_none()
            elif user.user_type == UserType.HOST:
                host_result = await db.execute(select(Host).where(Host.id == user.id))
                user.host_profile = host_result.scalar_one_or_none()
            elif user.user_type == UserType.AREA_COORDINATOR:
                coordinator_result = await db.execute(select(AreaCoordinator).where(AreaCoordinator.id == user.id))
                user.area_coordinator_profile = coordinator_result.scalar_one_or_none()
                
                # Also load bank details if they exist
                if user.area_coordinator_profile:
                    bank_result = await db.execute(select(BankDetails).where(BankDetails.area_coordinator_id == user.id))
                    user.area_coordinator_profile.bank_details = bank_result.scalar_one_or_none()
            
            # Convert to dictionary to avoid SQLAlchemy issues
            return self._convert_user_to_dict(user)
            
        except Exception as e:
            # Log error but don't expose it to user
            return None

    # Bank Details methods
    async def create_bank_details(self, db: AsyncSession, area_coordinator_id: int, bank_details_data: dict) -> dict:
        """Create bank details for an area coordinator"""
        try:
            # Check if bank details already exist for this coordinator
            existing_bank_details = await db.execute(
                select(BankDetails).where(BankDetails.area_coordinator_id == area_coordinator_id)
            )
            existing_bank_details = existing_bank_details.scalar_one_or_none()
            
            if existing_bank_details:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Bank details already exist for this area coordinator",
                    error_code=ErrorCodes.BANK_DETAILS_ALREADY_EXISTS
                )
            
            # Create new bank details
            bank_details = BankDetails(
                area_coordinator_id=area_coordinator_id,
                **bank_details_data
            )
            
            db.add(bank_details)
            await db.commit()
            await db.refresh(bank_details)
            
            # Convert to dictionary to avoid SQLAlchemy issues
            return self._convert_bank_details_to_dict(bank_details)
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to create bank details: {str(e)}",
                error_code=ErrorCodes.BANK_DETAILS_CREATION_FAILED
            )

    async def get_bank_details(self, db: AsyncSession, area_coordinator_id: int) -> Optional[dict]:
        """Get bank details for an area coordinator"""
        try:
            bank_details = await db.execute(
                select(BankDetails).where(BankDetails.area_coordinator_id == area_coordinator_id)
            )
            bank_details = bank_details.scalar_one_or_none()
            
            if not bank_details:
                return None
            
            # Convert to dictionary to avoid SQLAlchemy issues
            return self._convert_bank_details_to_dict(bank_details)
            
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to fetch bank details: {str(e)}",
                error_code=ErrorCodes.BANK_DETAILS_FETCH_FAILED
            )

    async def update_bank_details(self, db: AsyncSession, area_coordinator_id: int, bank_details_data: dict) -> dict:
        """Update bank details for an area coordinator"""
        try:
            # Get existing bank details
            bank_details = await db.execute(
                select(BankDetails).where(BankDetails.area_coordinator_id == area_coordinator_id)
            )
            bank_details = bank_details.scalar_one_or_none()
            
            if not bank_details:
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Bank details not found",
                    error_code=ErrorCodes.BANK_DETAILS_NOT_FOUND
                )
            
            # Update fields
            for field, value in bank_details_data.items():
                if hasattr(bank_details, field):
                    setattr(bank_details, field, value)
            
            await db.commit()
            await db.refresh(bank_details)
            
            # Convert to dictionary to avoid SQLAlchemy issues
            return self._convert_bank_details_to_dict(bank_details)
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to update bank details: {str(e)}",
                error_code=ErrorCodes.BANK_DETAILS_UPDATE_FAILED
            )

    async def verify_bank_details(self, db: AsyncSession, area_coordinator_id: int) -> dict:
        """Mark bank details as verified (admin only)"""
        try:
            # Get existing bank details
            bank_details = await db.execute(
                select(BankDetails).where(BankDetails.area_coordinator_id == area_coordinator_id)
            )
            bank_details = bank_details.scalar_one_or_none()
            
            if not bank_details:
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message="Bank details not found",
                    error_code=ErrorCodes.BANK_DETAILS_NOT_FOUND
                )
            
            # Mark as verified
            bank_details.is_verified = True
            
            await db.commit()
            await db.refresh(bank_details)
            
            # Convert to dictionary to avoid SQLAlchemy issues
            return self._convert_bank_details_to_dict(bank_details)
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to verify bank details: {str(e)}",
                error_code=ErrorCodes.BANK_DETAILS_VERIFICATION_FAILED
            )

    def _convert_bank_details_to_dict(self, bank_details: BankDetails) -> dict:
        """Convert BankDetails object to clean dictionary to avoid SQLAlchemy issues"""
        return {
            "id": bank_details.id,
            "area_coordinator_id": bank_details.area_coordinator_id,
            "bank_name": bank_details.bank_name,
            "account_holder_name": bank_details.account_holder_name,
            "account_number": bank_details.account_number,
            "ifsc_code": bank_details.ifsc_code,
            "branch_name": bank_details.branch_name,
            "branch_code": bank_details.branch_code,
            "account_type": bank_details.account_type,
            "is_verified": bank_details.is_verified,
            "bank_passbook_image": bank_details.bank_passbook_image,
            "cancelled_cheque_image": bank_details.cancelled_cheque_image,
            "created_at": bank_details.created_at,
            "updated_at": bank_details.updated_at
        }


# Service instance
users_service = UsersService()

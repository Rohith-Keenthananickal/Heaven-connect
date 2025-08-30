from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.users import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, UserSearchRequest, 
    UserSearchResponse, UserStatus, UserStatusUpdate, ProfileUpdateRequest, ProfileResponse,
    BankDetailsCreateRequest, BankDetailsUpdateRequest, BankDetailsResponseWrapper,
    AreaCoordinatorApprovalRequest, AreaCoordinatorApprovalResponse
)
from app.services.users_service import users_service


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user with profile"""
    try:
        db_user = await users_service.create(db, obj_in=user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/search", response_model=UserSearchResponse)
async def search_users(
    search_request: UserSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Search users with pagination and filters"""
    try:
        result = await users_service.search_users(db, search_request)
        
        return UserSearchResponse(
            data=result["users"],
            pagination=result["pagination"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )


@router.get("/", response_model=List[UserListResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    user_type: str = Query(None, description="Filter by user type"),
    db: AsyncSession = Depends(get_db)
):
    """Get all users with pagination and optional filtering"""
    try:
        if user_type:
            # Get users by specific type
            from app.models.user import UserType
            try:
                user_type_enum = UserType(user_type)
                users = await users_service.get_users_by_type(db, user_type_enum, skip=skip, limit=limit)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid user type: {user_type}"
                )
        elif active_only:
            users = await users_service.get_active_users(db, skip=skip, limit=limit)
        else:
            users = await users_service.get_multi(db, skip=skip, limit=limit)
        
        return users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by ID with profile"""
    try:
        db_user = await users_service.get_user_with_profile(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a user and their profile"""
    try:
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        updated_user = await users_service.update(db, db_obj=db_user, obj_in=user_update)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.patch("/{user_id}/profile", response_model=ProfileResponse)
async def update_user_profile(
    user_id: int,
    profile_update: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update user profile data"""
    try:
        # Get user to determine user type
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        
        # Update profile based on user type
        result = await users_service.update_profile(
            db, user_id, profile_update.profile_data.dict(exclude_unset=True), db_user.user_type
        )
        
        return ProfileResponse(
            data=result["profile"],
            message=f"{result['type'].title()} profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user status (ACTIVE, BLOCKED, DELETED)"""
    try:
        new_status = status_update.status
        
        # Update user status based on the new status
        if new_status == UserStatus.ACTIVE:
            updated_user = await users_service.activate_user(db, user_id)
        elif new_status == UserStatus.BLOCKED:
            updated_user = await users_service.block_user(db, user_id)
        elif new_status == UserStatus.DELETED:
            updated_user = await users_service.soft_delete(db, user_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value"
            )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        status_messages = {
            UserStatus.ACTIVE: "User activated successfully",
            UserStatus.BLOCKED: "User blocked successfully",
            UserStatus.DELETED: "User deleted successfully"
        }
        
        return {
            "status": "success", 
            "data": {
                "message": status_messages[new_status],
                "user": updated_user
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a user (change status to DELETED)"""
    try:
        deleted_user = await users_service.soft_delete(db, user_id)
        if not deleted_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"status": "success", "data": {"message": "User deleted successfully", "user": deleted_user}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


# Profile-specific endpoints
@router.get("/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user profile data"""
    try:
        db_user = await users_service.get_user_with_profile(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return profile based on user type
        if db_user.user_type.value == "GUEST" and db_user.guest_profile:
            return {"status": "success", "data": db_user.guest_profile, "type": "guest"}
        elif db_user.user_type.value == "HOST" and db_user.host_profile:
            return {"status": "success", "data": db_user.host_profile, "type": "host"}
        elif db_user.user_type.value == "AREA_COORDINATOR" and db_user.area_coordinator_profile:
            return {"status": "success", "data": db_user.area_coordinator_profile, "type": "area_coordinator"}
        else:
            return {"status": "success", "data": None, "type": "no_profile"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user profile: {str(e)}"
        )


@router.get("/types/{user_type}", response_model=List[UserListResponse])
async def get_users_by_type(
    user_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get users by specific type with pagination"""
    try:
        from app.models.user import UserType
        try:
            user_type_enum = UserType(user_type)
            users = await users_service.get_users_by_type(db, user_type_enum, skip=skip, limit=limit)
            return users
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user type: {user_type}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users by type: {str(e)}"
        )


# Area Coordinator Approval endpoints
@router.patch("/{user_id}/approval", response_model=AreaCoordinatorApprovalResponse)
async def update_area_coordinator_approval(
    user_id: int,
    approval_request: AreaCoordinatorApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject an area coordinator (Admin only)"""
    try:
        # Verify user is an area coordinator
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        if db_user.user_type.value != "AREA_COORDINATOR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approval can only be updated for area coordinators"
            )
        
        # TODO: Add admin authentication check here
        # For now, using a placeholder admin_user_id
        admin_user_id = 1  # This should come from authenticated admin user
        
        if approval_request.approval_status.value == "APPROVED":
            coordinator = await users_service.approve_area_coordinator(db, user_id, admin_user_id)
            message = "Area coordinator approved successfully"
        elif approval_request.approval_status.value == "REJECTED":
            if not approval_request.rejection_reason:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rejection reason is required when rejecting an area coordinator"
                )
            coordinator = await users_service.reject_area_coordinator(db, user_id, admin_user_id, approval_request.rejection_reason)
            message = "Area coordinator rejected successfully"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid approval status. Must be APPROVED or REJECTED"
            )
        
        return AreaCoordinatorApprovalResponse(
            data=coordinator,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update approval status: {str(e)}"
        )


# Bank Details endpoints for Area Coordinators
@router.post("/{user_id}/bank-details", response_model=BankDetailsResponseWrapper)
async def create_bank_details(
    user_id: int,
    bank_details_request: BankDetailsCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create bank details for an area coordinator"""
    try:
        # Verify user is an area coordinator
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        if db_user.user_type.value != "AREA_COORDINATOR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank details can only be created for area coordinators"
            )
        
        # Create bank details
        bank_details = await users_service.create_bank_details(
            db, user_id, bank_details_request.bank_details.dict()
        )
        
        return BankDetailsResponseWrapper(
            data=bank_details,
            message="Bank details created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bank details: {str(e)}"
        )


@router.get("/{user_id}/bank-details", response_model=BankDetailsResponseWrapper)
async def get_bank_details(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get bank details for an area coordinator"""
    try:
        # Verify user is an area coordinator
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        if db_user.user_type.value != "AREA_COORDINATOR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank details can only be accessed for area coordinators"
            )
        
        # Get bank details
        bank_details = await users_service.get_bank_details(db, user_id)
        if not bank_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank details not found"
            )
        
        return BankDetailsResponseWrapper(
            data=bank_details,
            message="Bank details retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch bank details: {str(e)}"
        )


@router.put("/{user_id}/bank-details", response_model=BankDetailsResponseWrapper)
async def update_bank_details(
    user_id: int,
    bank_details_update: BankDetailsUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update bank details for an area coordinator"""
    try:
        # Verify user is an area coordinator
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        if db_user.user_type.value != "AREA_COORDINATOR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank details can only be updated for area coordinators"
            )
        
        # Update bank details
        bank_details = await users_service.update_bank_details(
            db, user_id, bank_details_update.bank_details.dict(exclude_unset=True)
        )
        
        return BankDetailsResponseWrapper(
            data=bank_details,
            message="Bank details updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update bank details: {str(e)}"
        )


@router.patch("/{user_id}/bank-details/verify", response_model=BankDetailsResponseWrapper)
async def verify_bank_details(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark bank details as verified (admin only)"""
    try:
        # Verify user is an area coordinator
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        if db_user.user_type.value != "AREA_COORDINATOR":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank details can only be verified for area coordinators"
            )
        
        # Verify bank details
        bank_details = await users_service.verify_bank_details(db, user_id)
        
        return BankDetailsResponseWrapper(
            data=bank_details,
            message="Bank details verified successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify bank details: {str(e)}"
        )

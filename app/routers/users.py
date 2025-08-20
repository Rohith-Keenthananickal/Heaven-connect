from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services.users_service import users_service


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    try:
        db_user = await users_service.create(db, obj_in=user)
        return {"status": "success", "data": db_user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """Get all users with pagination"""
    try:
        if active_only:
            users = await users_service.get_active_users(db, skip=skip, limit=limit)
        else:
            users = await users_service.get_multi(db, skip=skip, limit=limit)
        
        return {"status": "success", "data": users}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by ID"""
    try:
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        return {"status": "success", "data": db_user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user: {str(e)}"
        )


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a user"""
    try:
        db_user = await users_service.get_or_404(db, user_id, "User not found")
        updated_user = await users_service.update(db, db_obj=db_user, obj_in=user_update)
        return {"status": "success", "data": updated_user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user"""
    try:
        deleted_user = await users_service.delete(db, id=user_id)
        if not deleted_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"status": "success", "data": {"message": "User deleted successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

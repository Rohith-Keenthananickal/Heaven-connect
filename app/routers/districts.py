from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.districts import (
    DistrictCreate, 
    DistrictUpdate, 
    DistrictResponse, 
    DistrictListResponse,
    DistrictWithPanchayatsResponse
)
from app.services.districts_service import district_service

router = APIRouter(prefix="/districts", tags=["Districts"])


@router.post("/", response_model=DistrictResponse, status_code=status.HTTP_201_CREATED)
async def create_district(
    district: DistrictCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new district"""
    try:
        # Check if district with same name and state already exists
        existing_district = await district_service.get_by_code(db, district.code) if district.code else None
        if existing_district:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="District with this code already exists"
            )
        
        db_district = await district_service.create(db, obj_in=district)
        return db_district
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to create district: {str(e)}"
        )


@router.get("/", response_model=List[DistrictListResponse])
async def get_districts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    state: Optional[str] = Query(None, description="Filter by state"),
    search: Optional[str] = Query(None, description="Search by name or state"),
    active_only: bool = Query(True, description="Return only active districts"),
    db: AsyncSession = Depends(get_db)
):
    """Get all districts with optional filtering and pagination"""
    try:
        if state:
            districts = await district_service.get_by_state(db, state, skip=skip, limit=limit)
        elif search:
            districts = await district_service.search_districts(db, search, skip=skip, limit=limit)
        elif active_only:
            districts = await district_service.get_active_districts(db, skip=skip, limit=limit)
        else:
            districts = await district_service.get_multi(db, skip=skip, limit=limit)
        
        return districts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch districts: {str(e)}"
        )


@router.get("/{district_id}", response_model=DistrictResponse)
async def get_district(
    district_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get a specific district by ID"""
    try:
        db_district = await district_service.get_or_404(db, district_id, "District not found")
        return db_district
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch district: {str(e)}"
        )


@router.get("/{district_id}/with-panchayats", response_model=DistrictWithPanchayatsResponse)
async def get_district_with_panchayats(
    district_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get a district with all its grama panchayats"""
    try:
        db_district = await district_service.get_or_404(db, district_id, "District not found")
        return db_district
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch district with panchayats: {str(e)}"
        )


@router.put("/{district_id}", response_model=DistrictResponse)
async def update_district(
    district_id: int, 
    district_update: DistrictUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a district"""
    try:
        db_district = await district_service.get_or_404(db, district_id, "District not found")
        updated_district = await district_service.update(db, db_obj=db_district, obj_in=district_update)
        return updated_district
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update district: {str(e)}"
        )


@router.delete("/{district_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_district(
    district_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Delete a district (soft delete by setting is_active to False)"""
    try:
        db_district = await district_service.get_or_404(db, district_id, "District not found")
        
        # Soft delete by setting is_active to False
        update_data = DistrictUpdate(is_active=False)
        await district_service.update(db, db_obj=db_district, obj_in=update_data)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to delete district: {str(e)}"
        )


@router.get("/states/list")
async def get_states(db: AsyncSession = Depends(get_db)):
    """Get list of all unique states"""
    try:
        # This would need to be implemented in the service
        # For now, we'll return a simple response
        return {"message": "States list endpoint - to be implemented"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch states: {str(e)}"
        )

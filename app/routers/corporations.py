from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.corporations import (
    CorporationCreate, 
    CorporationUpdate, 
    CorporationResponse, 
    CorporationListResponse,
    CorporationWithDistrictResponse,
    CorporationCreateAPIResponse, 
    CorporationListAPIResponse, 
    CorporationGetAPIResponse,
    CorporationUpdateAPIResponse, 
    CorporationDeleteAPIResponse, 
    CorporationWithDistrictAPIResponse
)
from app.services.corporations_service import corporation_service

router = APIRouter(prefix="/corporations", tags=["Corporations"])


@router.post("/", response_model=CorporationCreateAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_corporation(
    corporation: CorporationCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new corporation"""
    try:
        # Check if corporation with same code already exists
        if corporation.code:
            existing_corporation = await corporation_service.get_by_code(db, corporation.code)
            if existing_corporation:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Corporation with this code already exists"
                )
        
        db_corporation = await corporation_service.create(db, obj_in=corporation)
        return CorporationCreateAPIResponse(
            data=db_corporation,
            message="Corporation created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to create corporation: {str(e)}"
        )


@router.get("/", response_model=CorporationListAPIResponse)
async def get_corporations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    search: Optional[str] = Query(None, description="Search by name"),
    active_only: bool = Query(True, description="Return only active corporations"),
    min_population: Optional[int] = Query(None, ge=0, description="Minimum population filter"),
    max_population: Optional[int] = Query(None, ge=0, description="Maximum population filter"),
    established_year: Optional[int] = Query(None, ge=1800, le=2030, description="Filter by established year"),
    mayor_name: Optional[str] = Query(None, description="Filter by mayor name"),
    db: AsyncSession = Depends(get_db)
):
    """Get all corporations with optional filtering and pagination"""
    try:
        if district_id:
            corporations = await corporation_service.get_by_district(db, district_id, skip=skip, limit=limit)
        elif search:
            corporations = await corporation_service.search_corporations(db, search, skip=skip, limit=limit)
        elif min_population is not None and max_population is not None:
            corporations = await corporation_service.get_corporations_by_population_range(
                db, min_population, max_population, skip=skip, limit=limit
            )
        elif established_year:
            corporations = await corporation_service.get_corporations_by_established_year(
                db, established_year, skip=skip, limit=limit
            )
        elif mayor_name:
            corporations = await corporation_service.get_corporations_by_mayor(
                db, mayor_name, skip=skip, limit=limit
            )
        elif active_only:
            corporations = await corporation_service.get_active_corporations(db, skip=skip, limit=limit)
        else:
            corporations = await corporation_service.get_multi(db, skip=skip, limit=limit)
        
        return CorporationListAPIResponse(
            data=corporations,
            message="Corporations retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch corporations: {str(e)}"
        )


@router.get("/{corporation_id}", response_model=CorporationGetAPIResponse)
async def get_corporation(
    corporation_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get a specific corporation by ID"""
    try:
        db_corporation = await corporation_service.get_or_404(db, corporation_id, "Corporation not found")
        return CorporationGetAPIResponse(
            data=db_corporation,
            message="Corporation retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch corporation: {str(e)}"
        )


@router.get("/{corporation_id}/with-district", response_model=CorporationWithDistrictAPIResponse)
async def get_corporation_with_district(
    corporation_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get a corporation with its district information"""
    try:
        db_corporation = await corporation_service.get_or_404(db, corporation_id, "Corporation not found")
        return CorporationWithDistrictAPIResponse(
            data=db_corporation,
            message="Corporation with district retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch corporation with district: {str(e)}"
        )


@router.put("/{corporation_id}", response_model=CorporationUpdateAPIResponse)
async def update_corporation(
    corporation_id: int, 
    corporation_update: CorporationUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a corporation"""
    try:
        db_corporation = await corporation_service.get_or_404(db, corporation_id, "Corporation not found")
        updated_corporation = await corporation_service.update(db, db_obj=db_corporation, obj_in=corporation_update)
        return CorporationUpdateAPIResponse(
            data=updated_corporation,
            message="Corporation updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update corporation: {str(e)}"
        )


@router.delete("/{corporation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_corporation(
    corporation_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Delete a corporation (soft delete by setting is_active to False)"""
    try:
        db_corporation = await corporation_service.get_or_404(db, corporation_id, "Corporation not found")
        
        # Soft delete by setting is_active to False
        update_data = CorporationUpdate(is_active=False)
        await corporation_service.update(db, db_obj=db_corporation, obj_in=update_data)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to delete corporation: {str(e)}"
        )


@router.get("/district/{district_id}", response_model=CorporationListAPIResponse)
async def get_corporations_by_district(
    district_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    active_only: bool = Query(True, description="Return only active corporations"),
    db: AsyncSession = Depends(get_db)
):
    """Get all corporations for a specific district"""
    try:
        corporations = await corporation_service.get_by_district(db, district_id, skip=skip, limit=limit)
        
        if active_only:
            corporations = [c for c in corporations if c.is_active]
        
        return CorporationListAPIResponse(
            data=corporations,
            message="Corporations retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch corporations for district: {str(e)}"
        )

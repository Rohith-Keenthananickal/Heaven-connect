from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.grama_panchayats import (
    GramaPanchayatCreate, 
    GramaPanchayatUpdate, 
    GramaPanchayatResponse, 
    GramaPanchayatListResponse,
    GramaPanchayatWithDistrictResponse
)
from app.services.grama_panchayats_service import grama_panchayat_service

router = APIRouter(prefix="/grama-panchayats", tags=["Grama Panchayats"])


@router.post("/", response_model=GramaPanchayatResponse, status_code=status.HTTP_201_CREATED)
async def create_grama_panchayat(
    panchayat: GramaPanchayatCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new grama panchayat"""
    try:
        # Check if panchayat with same code already exists
        if panchayat.code:
            existing_panchayat = await grama_panchayat_service.get_by_code(db, panchayat.code)
            if existing_panchayat:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Grama panchayat with this code already exists"
                )
        
        db_panchayat = await grama_panchayat_service.create(db, obj_in=panchayat)
        return db_panchayat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to create grama panchayat: {str(e)}"
        )


@router.get("/", response_model=List[GramaPanchayatListResponse])
async def get_grama_panchayats(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    search: Optional[str] = Query(None, description="Search by name"),
    active_only: bool = Query(True, description="Return only active panchayats"),
    min_population: Optional[int] = Query(None, ge=0, description="Minimum population filter"),
    max_population: Optional[int] = Query(None, ge=0, description="Maximum population filter"),
    db: AsyncSession = Depends(get_db)
):
    """Get all grama panchayats with optional filtering and pagination"""
    try:
        if district_id:
            panchayats = await grama_panchayat_service.get_by_district(db, district_id, skip=skip, limit=limit)
        elif search:
            panchayats = await grama_panchayat_service.search_panchayats(db, search, skip=skip, limit=limit)
        elif min_population is not None and max_population is not None:
            panchayats = await grama_panchayat_service.get_panchayats_by_population_range(
                db, min_population, max_population, skip=skip, limit=limit
            )
        elif active_only:
            panchayats = await grama_panchayat_service.get_active_panchayats(db, skip=skip, limit=limit)
        else:
            panchayats = await grama_panchayat_service.get_multi(db, skip=skip, limit=limit)
        
        return panchayats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch grama panchayats: {str(e)}"
        )


@router.get("/{panchayat_id}", response_model=GramaPanchayatResponse)
async def get_grama_panchayat(
    panchayat_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get a specific grama panchayat by ID"""
    try:
        db_panchayat = await grama_panchayat_service.get_or_404(db, panchayat_id, "Grama panchayat not found")
        return db_panchayat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch grama panchayat: {str(e)}"
        )


@router.get("/{panchayat_id}/with-district", response_model=GramaPanchayatWithDistrictResponse)
async def get_grama_panchayat_with_district(
    panchayat_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get a grama panchayat with its district information"""
    try:
        db_panchayat = await grama_panchayat_service.get_or_404(db, panchayat_id, "Grama panchayat not found")
        return db_panchayat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch grama panchayat with district: {str(e)}"
        )


@router.put("/{panchayat_id}", response_model=GramaPanchayatResponse)
async def update_grama_panchayat(
    panchayat_id: int, 
    panchayat_update: GramaPanchayatUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a grama panchayat"""
    try:
        db_panchayat = await grama_panchayat_service.get_or_404(db, panchayat_id, "Grama panchayat not found")
        updated_panchayat = await grama_panchayat_service.update(db, db_obj=db_panchayat, obj_in=panchayat_update)
        return updated_panchayat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update grama panchayat: {str(e)}"
        )


@router.delete("/{panchayat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grama_panchayat(
    panchayat_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Delete a grama panchayat (soft delete by setting is_active to False)"""
    try:
        db_panchayat = await grama_panchayat_service.get_or_404(db, panchayat_id, "Grama panchayat not found")
        
        # Soft delete by setting is_active to False
        update_data = GramaPanchayatUpdate(is_active=False)
        await grama_panchayat_service.update(db, db_obj=db_panchayat, obj_in=update_data)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to delete grama panchayat: {str(e)}"
        )


@router.get("/district/{district_id}", response_model=List[GramaPanchayatListResponse])
async def get_panchayats_by_district(
    district_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    active_only: bool = Query(True, description="Return only active panchayats"),
    db: AsyncSession = Depends(get_db)
):
    """Get all grama panchayats for a specific district"""
    try:
        panchayats = await grama_panchayat_service.get_by_district(db, district_id, skip=skip, limit=limit)
        
        if active_only:
            panchayats = [p for p in panchayats if p.is_active]
        
        return panchayats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch panchayats for district: {str(e)}"
        )

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.municipalities import (
    MunicipalityCreate, 
    MunicipalityUpdate, 
    MunicipalityResponse, 
    MunicipalityListResponse,
    MunicipalityWithDistrictResponse,
    MunicipalityCreateAPIResponse, 
    MunicipalityListAPIResponse, 
    MunicipalityGetAPIResponse,
    MunicipalityUpdateAPIResponse, 
    MunicipalityDeleteAPIResponse, 
    MunicipalityWithDistrictAPIResponse
)
from app.services.municipalities_service import municipality_service

router = APIRouter(prefix="/municipalities", tags=["Municipalities"])


@router.post("/", response_model=MunicipalityCreateAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_municipality(
    municipality: MunicipalityCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new municipality"""
    try:
        # Check if municipality with same code already exists
        if municipality.code:
            existing_municipality = await municipality_service.get_by_code(db, municipality.code)
            if existing_municipality:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Municipality with this code already exists"
                )
        
        db_municipality = await municipality_service.create(db, obj_in=municipality)
        return MunicipalityCreateAPIResponse(
            data=db_municipality,
            message="Municipality created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to create municipality: {str(e)}"
        )


@router.get("/", response_model=MunicipalityListAPIResponse)
async def get_municipalities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    district_id: Optional[int] = Query(None, description="Filter by district ID"),
    search: Optional[str] = Query(None, description="Search by name"),
    active_only: bool = Query(True, description="Return only active municipalities"),
    min_population: Optional[int] = Query(None, ge=0, description="Minimum population filter"),
    max_population: Optional[int] = Query(None, ge=0, description="Maximum population filter"),
    established_year: Optional[int] = Query(None, ge=1800, le=2030, description="Filter by established year"),
    chairman_name: Optional[str] = Query(None, description="Filter by chairman name"),
    municipality_type: Optional[str] = Query(None, description="Filter by municipality type/grade"),
    db: AsyncSession = Depends(get_db)
):
    """Get all municipalities with optional filtering and pagination"""
    try:
        if district_id:
            municipalities = await municipality_service.get_by_district(db, district_id, skip=skip, limit=limit)
        elif search:
            municipalities = await municipality_service.search_municipalities(db, search, skip=skip, limit=limit)
        elif min_population is not None and max_population is not None:
            municipalities = await municipality_service.get_municipalities_by_population_range(
                db, min_population, max_population, skip=skip, limit=limit
            )
        elif established_year:
            municipalities = await municipality_service.get_municipalities_by_established_year(
                db, established_year, skip=skip, limit=limit
            )
        elif chairman_name:
            municipalities = await municipality_service.get_municipalities_by_chairman(
                db, chairman_name, skip=skip, limit=limit
            )
        elif municipality_type:
            municipalities = await municipality_service.get_municipalities_by_type(
                db, municipality_type, skip=skip, limit=limit
            )
        elif active_only:
            municipalities = await municipality_service.get_active_municipalities(db, skip=skip, limit=limit)
        else:
            municipalities = await municipality_service.get_multi(db, skip=skip, limit=limit)
        
        return MunicipalityListAPIResponse(
            data=municipalities,
            message="Municipalities retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch municipalities: {str(e)}"
        )


@router.get("/{municipality_id}", response_model=MunicipalityGetAPIResponse)
async def get_municipality(
    municipality_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get a specific municipality by ID"""
    try:
        db_municipality = await municipality_service.get_or_404(db, municipality_id, "Municipality not found")
        return MunicipalityGetAPIResponse(
            data=db_municipality,
            message="Municipality retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch municipality: {str(e)}"
        )


@router.get("/{municipality_id}/with-district", response_model=MunicipalityWithDistrictAPIResponse)
async def get_municipality_with_district(
    municipality_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get a municipality with its district information"""
    try:
        db_municipality = await municipality_service.get_or_404(db, municipality_id, "Municipality not found")
        return MunicipalityWithDistrictAPIResponse(
            data=db_municipality,
            message="Municipality with district retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch municipality with district: {str(e)}"
        )


@router.put("/{municipality_id}", response_model=MunicipalityUpdateAPIResponse)
async def update_municipality(
    municipality_id: int, 
    municipality_update: MunicipalityUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a municipality"""
    try:
        db_municipality = await municipality_service.get_or_404(db, municipality_id, "Municipality not found")
        updated_municipality = await municipality_service.update(db, db_obj=db_municipality, obj_in=municipality_update)
        return MunicipalityUpdateAPIResponse(
            data=updated_municipality,
            message="Municipality updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update municipality: {str(e)}"
        )


@router.delete("/{municipality_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_municipality(
    municipality_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Delete a municipality (soft delete by setting is_active to False)"""
    try:
        db_municipality = await municipality_service.get_or_404(db, municipality_id, "Municipality not found")
        
        # Soft delete by setting is_active to False
        update_data = MunicipalityUpdate(is_active=False)
        await municipality_service.update(db, db_obj=db_municipality, obj_in=update_data)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to delete municipality: {str(e)}"
        )


@router.get("/district/{district_id}", response_model=MunicipalityListAPIResponse)
async def get_municipalities_by_district(
    district_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    active_only: bool = Query(True, description="Return only active municipalities"),
    db: AsyncSession = Depends(get_db)
):
    """Get all municipalities for a specific district"""
    try:
        municipalities = await municipality_service.get_by_district(db, district_id, skip=skip, limit=limit)
        
        if active_only:
            municipalities = [m for m in municipalities if m.is_active]
        
        return MunicipalityListAPIResponse(
            data=municipalities,
            message="Municipalities retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch municipalities for district: {str(e)}"
        )

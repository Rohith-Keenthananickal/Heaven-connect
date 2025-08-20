from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.facilities import FacilityCreate, FacilityUpdate, FacilityResponse, FacilityListResponse
from app.services.facilities_service import facilities_service
from app.models.property import FacilityCategory


router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.post("/")
async def create_facility(facility: FacilityCreate, db: AsyncSession = Depends(get_db)):
    """Create a new facility"""
    try:
        db_facility = await facilities_service.create(db, obj_in=facility)
        return {"status": "success", "data": db_facility}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/")
async def get_facilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: int = Query(None),
    category: FacilityCategory = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all facilities with pagination and filters"""
    try:
        if property_id and category:
            facilities = await facilities_service.get_by_property_and_category(db, property_id, category)
        elif property_id:
            facilities = await facilities_service.get_by_property(db, property_id)
        elif category:
            facilities = await facilities_service.get_by_category(db, category, skip=skip, limit=limit)
        else:
            facilities = await facilities_service.get_multi(db, skip=skip, limit=limit)
        return {"status": "success", "data": facilities}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{facility_id}")
async def get_facility(facility_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific facility by ID"""
    try:
        db_facility = await facilities_service.get_or_404(db, facility_id, "Facility not found")
        return {"status": "success", "data": db_facility}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{facility_id}")
async def update_facility(facility_id: int, facility_update: FacilityUpdate, db: AsyncSession = Depends(get_db)):
    """Update a facility"""
    try:
        db_facility = await facilities_service.get_or_404(db, facility_id, "Facility not found")
        updated_facility = await facilities_service.update(db, db_obj=db_facility, obj_in=facility_update)
        return {"status": "success", "data": updated_facility}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{facility_id}")
async def delete_facility(facility_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a facility"""
    try:
        deleted_facility = await facilities_service.delete(db, id=facility_id)
        if not deleted_facility:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found")
        return {"status": "success", "data": {"message": "Facility deleted successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.facilities import (
    FacilityCreate,
    FacilityUpdate,
    FacilityResponse,
    FacilityListResponse,
    facility_to_response,
    facility_to_list_response,
)
from app.services.facilities_service import facilities_service
from app.models.property import FacilityCategory


router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.post("/")
async def create_facility(facility: FacilityCreate, db: AsyncSession = Depends(get_db)):
    """Create a new facility linked to a facility master (by facility_master_id)."""
    try:
        db_facility = await facilities_service.create(db, obj_in=facility)
        # Return with master populated for consistency
        db_facility = await facilities_service.get_or_404_with_master(db, db_facility.id)
        return {"status": "success", "data": facility_to_response(db_facility)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/")
async def get_facilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: int = Query(None),
    category: FacilityCategory = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all facilities with pagination and filters; each item includes populated facility_master."""
    try:
        filters = None
        if property_id is not None and category is not None:
            filters = {"property_id": property_id, "category": category}
        elif property_id is not None:
            filters = {"property_id": property_id}
        elif category is not None:
            filters = {"category": category}
        facilities = await facilities_service.get_multi_with_master(
            db, skip=skip, limit=limit, filters=filters
        )
        return {"status": "success", "data": [facility_to_list_response(f) for f in facilities]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{facility_id}")
async def get_facility(facility_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific facility by ID with facility_master populated."""
    try:
        db_facility = await facilities_service.get_or_404_with_master(db, facility_id, "Facility not found")
        return {"status": "success", "data": facility_to_response(db_facility)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{facility_id}")
async def update_facility(facility_id: int, facility_update: FacilityUpdate, db: AsyncSession = Depends(get_db)):
    """Update a facility."""
    try:
        db_facility = await facilities_service.get_or_404(db, facility_id, "Facility not found")
        updated_facility = await facilities_service.update(db, db_obj=db_facility, obj_in=facility_update)
        # Return with master populated
        updated_facility = await facilities_service.get_or_404_with_master(db, updated_facility.id)
        return {"status": "success", "data": facility_to_response(updated_facility)}
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

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse, LocationListResponse
from app.services.location_service import location_service


router = APIRouter(prefix="/location", tags=["Location"])


@router.post("/")
async def create_location(location: LocationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new location"""
    try:
        db_location = await location_service.create(db, obj_in=location)
        return {"status": "success", "data": db_location}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/")
async def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: int = Query(None),
    elderly_friendly: bool = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all locations with pagination and filters"""
    try:
        if property_id:
            location = await location_service.get_by_property(db, property_id)
            locations = [location] if location else []
        elif elderly_friendly is True:
            locations = await location_service.get_elderly_friendly(db, skip=skip, limit=limit)
        else:
            filters = {"elderly_friendly": elderly_friendly} if elderly_friendly is not None else None
            locations = await location_service.get_multi(db, skip=skip, limit=limit, filters=filters)
        return {"status": "success", "data": locations}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{location_id}")
async def get_location(location_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific location by ID"""
    try:
        db_location = await location_service.get_or_404(db, location_id, "Location not found")
        return {"status": "success", "data": db_location}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{location_id}")
async def update_location(location_id: int, location_update: LocationUpdate, db: AsyncSession = Depends(get_db)):
    """Update a location"""
    try:
        db_location = await location_service.get_or_404(db, location_id, "Location not found")
        updated_location = await location_service.update(db, db_obj=db_location, obj_in=location_update)
        return {"status": "success", "data": updated_location}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{location_id}")
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a location"""
    try:
        deleted_location = await location_service.delete(db, id=location_id)
        if not deleted_location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
        return {"status": "success", "data": {"message": "Location deleted successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

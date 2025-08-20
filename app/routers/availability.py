from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import get_db
from app.schemas.availability import AvailabilityCreate, AvailabilityUpdate, AvailabilityResponse, AvailabilityListResponse
from app.services.availability_service import availability_service


router = APIRouter(prefix="/availability", tags=["Availability"])


@router.post("/")
async def create_availability(availability: AvailabilityCreate, db: AsyncSession = Depends(get_db)):
    """Create a new availability record"""
    try:
        db_availability = await availability_service.create(db, obj_in=availability)
        return {"status": "success", "data": db_availability}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/")
async def get_availability(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: int = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    available_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """Get availability records with pagination and filters"""
    try:
        if property_id and available_only:
            availability = await availability_service.get_available_dates(db, property_id, from_date, to_date)
        elif property_id:
            availability = await availability_service.get_by_property(db, property_id)
        else:
            availability = await availability_service.get_multi(db, skip=skip, limit=limit)
        return {"status": "success", "data": availability}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{availability_id}")
async def get_availability_record(availability_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific availability record by ID"""
    try:
        db_availability = await availability_service.get_or_404(db, availability_id, "Availability record not found")
        return {"status": "success", "data": db_availability}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{availability_id}")
async def update_availability(availability_id: int, availability_update: AvailabilityUpdate, db: AsyncSession = Depends(get_db)):
    """Update an availability record"""
    try:
        db_availability = await availability_service.get_or_404(db, availability_id, "Availability record not found")
        updated_availability = await availability_service.update(db, db_obj=db_availability, obj_in=availability_update)
        return {"status": "success", "data": updated_availability}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{availability_id}")
async def delete_availability(availability_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an availability record"""
    try:
        deleted_availability = await availability_service.delete(db, id=availability_id)
        if not deleted_availability:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability record not found")
        return {"status": "success", "data": {"message": "Availability record deleted successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

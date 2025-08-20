from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.property_photos import PropertyPhotoCreate, PropertyPhotoUpdate, PropertyPhotoResponse, PropertyPhotoListResponse
from app.services.property_photos_service import property_photos_service
from app.models.property import PhotoCategory


router = APIRouter(prefix="/property-photos", tags=["Property Photos"])


@router.post("/")
async def create_property_photo(photo: PropertyPhotoCreate, db: AsyncSession = Depends(get_db)):
    """Create a new property photo"""
    try:
        db_photo = await property_photos_service.create(db, obj_in=photo)
        return {"status": "success", "data": db_photo}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/")
async def get_property_photos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: int = Query(None),
    category: PhotoCategory = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all property photos with pagination and filters"""
    try:
        if property_id and category:
            photos = await property_photos_service.get_by_property_and_category(db, property_id, category)
        elif property_id:
            photos = await property_photos_service.get_by_property(db, property_id)
        elif category:
            photos = await property_photos_service.get_by_category(db, category, skip=skip, limit=limit)
        else:
            photos = await property_photos_service.get_multi(db, skip=skip, limit=limit)
        return {"status": "success", "data": photos}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{photo_id}")
async def get_property_photo(photo_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific property photo by ID"""
    try:
        db_photo = await property_photos_service.get_or_404(db, photo_id, "Property photo not found")
        return {"status": "success", "data": db_photo}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{photo_id}")
async def update_property_photo(photo_id: int, photo_update: PropertyPhotoUpdate, db: AsyncSession = Depends(get_db)):
    """Update a property photo"""
    try:
        db_photo = await property_photos_service.get_or_404(db, photo_id, "Property photo not found")
        updated_photo = await property_photos_service.update(db, db_obj=db_photo, obj_in=photo_update)
        return {"status": "success", "data": updated_photo}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{photo_id}")
async def delete_property_photo(photo_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a property photo"""
    try:
        deleted_photo = await property_photos_service.delete(db, id=photo_id)
        if not deleted_photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property photo not found")
        return {"status": "success", "data": {"message": "Property photo deleted successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.database import get_db, get_sync_db
from app.schemas.property import (
    PropertyCreate, PropertyProfileCreate, PropertyProfileUpdate, 
    PropertyProfileResponse, PropertyResponse, PropertySearchRequest, 
    PropertySearchResponse, PropertyStatusUpdate
)
from app.services.property_service import PropertyService
from app.utils.error_handler import create_server_error_http_exception
from app.models.property import PropertyStatus
from typing import List, Optional


router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/profile", response_model=PropertyProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_property_profile(
    property_profile: PropertyProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new property profile"""
    try:
        db_property = await PropertyService.create_property_profile(
            db, 
            property_profile.user_id,
            property_profile.property_name,
            property_profile.alternate_phone,
            property_profile.area_coordinator_id,
            property_profile.property_type_id,
            property_profile.id_proof_type,
            property_profile.id_proof_url,
            property_profile.certificate_number,
            property_profile.trade_license_number,
            property_profile.classification,
            property_profile.status,
            property_profile.progress_step,
            property_profile.is_verified
        )
        return db_property
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create property profile: {str(e)}"
        )


@router.get("/profile/{property_id}", response_model=PropertyProfileResponse)
async def get_property_profile(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific property profile by ID"""
    try:
        db_property = await PropertyService.get_property_profile(db, property_id)
        if not db_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        return db_property
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property profile: {str(e)}"
        )


@router.put("/profile/{property_id}", response_model=PropertyProfileResponse)
async def update_property_profile(
    property_id: int,
    property_update: PropertyProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a property profile"""
    try:
        db_property = await PropertyService.update_property_profile(
            db, 
            property_id, 
            property_update
        )
        if not db_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        return db_property
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property profile: {str(e)}"
        )


@router.delete("/profile/{property_id}")
async def delete_property_profile(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a property profile"""
    try:
        success = await PropertyService.delete_property_profile(db, property_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        return {"status": "success", "message": "Property profile deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete property profile: {str(e)}"
        )


@router.post("/search", response_model=PropertySearchResponse)
async def search_properties(
    search_request: PropertySearchRequest,
    db: Session = Depends(get_sync_db)
):
    """Search properties with pagination and filters"""
    try:
        result = PropertyService.search_properties(db, search_request)
        
        return PropertySearchResponse(
            data=result["properties"],
            pagination=result["pagination"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search properties: {str(e)}"
        )


@router.patch("/{property_id}/status")
async def update_property_status(
    property_id: int,
    status_update: PropertyStatusUpdate,
    db: Session = Depends(get_sync_db)
):
    """Update property status (ACTIVE, INACTIVE, BLOCKED, DELETED)"""
    try:
        new_status = status_update.status
        
        # Update property status based on the new status
        if new_status == PropertyStatus.ACTIVE:
            updated_property = PropertyService.activate_property(db, property_id)
        elif new_status == PropertyStatus.INACTIVE:
            updated_property = PropertyService.deactivate_property(db, property_id)
        elif new_status == PropertyStatus.BLOCKED:
            updated_property = PropertyService.block_property(db, property_id)
        elif new_status == PropertyStatus.DELETED:
            updated_property = PropertyService.soft_delete_property(db, property_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value"
            )
        
        if not updated_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        status_messages = {
            PropertyStatus.ACTIVE: "Property activated successfully",
            PropertyStatus.INACTIVE: "Property deactivated successfully",
            PropertyStatus.BLOCKED: "Property blocked successfully",
            PropertyStatus.DELETED: "Property deleted successfully"
        }
        
        return {
            "status": "success", 
            "data": {
                "message": status_messages[new_status],
                "property": updated_property
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property status: {str(e)}"
        ) 
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.property import PropertyProfileCreate, PropertyProfileResponse, PropertyOnboardingStatus
from app.services.property_service import PropertyService


router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/", response_model=PropertyProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_property_profile(
    profile_data: PropertyProfileCreate,
    user_id: int = Query(..., description="User ID to create property profile for"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new property profile (Step 1)"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            property_profile = PropertyService.create_property_profile(session, user_id, profile_data)
            return property_profile
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[PropertyProfileResponse])
async def get_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    verified_only: bool = Query(False),
    coordinator_id: int = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all properties with pagination and filters"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            if verified_only:
                properties = PropertyService.get_all_properties(session, skip=skip, limit=limit, verified_only=True)
            elif coordinator_id:
                properties = PropertyService.get_properties_by_coordinator(session, coordinator_id)
            else:
                properties = PropertyService.get_all_properties(session, skip=skip, limit=limit)
            
            return properties
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch properties: {str(e)}"
        )


@router.get("/{property_id}", response_model=PropertyProfileResponse)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific property by ID"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            property_obj = PropertyService.get_property_by_id(session, property_id)
            if not property_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Property not found"
                )
            return property_obj
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property: {str(e)}"
        )


@router.get("/{property_id}/onboarding-status", response_model=PropertyOnboardingStatus)
async def get_property_onboarding_status(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get property onboarding status"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            status_obj = PropertyService.get_onboarding_status(session, property_id)
            return status_obj
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property onboarding status: {str(e)}"
        )


@router.post("/{property_id}/verify")
async def verify_property(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Verify property profile"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            property_obj = PropertyService.verify_property(session, property_id)
            return {"message": "Property verified successfully", "property": property_obj}
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify property: {str(e)}"
        )


@router.post("/{property_id}/assign-coordinator")
async def assign_coordinator(
    property_id: int,
    coordinator_id: int = Query(..., description="Coordinator user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Assign area coordinator to property"""
    try:
        # Convert AsyncSession to Session for PropertyService
        from sqlalchemy.orm import Session
        session = Session(bind=db.bind)
        try:
            property_obj = PropertyService.assign_coordinator(session, property_id, coordinator_id)
            return {"message": "Coordinator assigned successfully", "property": property_obj}
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign coordinator: {str(e)}"
        ) 
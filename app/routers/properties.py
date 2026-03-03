from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.database import get_db, get_sync_db
from app.schemas.property import (
    PropertyCreate, PropertyProfileCreate, PropertyProfileUpdate, 
    PropertyProfileResponse, PropertyResponse, PropertySearchRequest, 
    PropertySearchResponse, PropertyStatusUpdate,
    PropertyCreateAPIResponse, PropertyGetAPIResponse, PropertyUpdateAPIResponse,
    PropertyDeleteAPIResponse, PropertyStatusUpdateAPIResponse,
    PropertyApprovalCreate, PropertyApprovalAPIResponse, PropertyApprovalResponse, PropertyApprovalListResponse, VerificationType,
    PropertyVerificationStatusUpdate, PropertyVerificationStatusAPIResponse,
    ATPAutoAllocationAPIResponse, ATPInRangeAPIResponse
)
from app.models.property import PropertyVerificationStatus
from app.services.property_service import PropertyService
from app.utils.error_handler import create_server_error_http_exception
from app.models.property import PropertyStatus
from typing import List, Optional


router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/profile", response_model=PropertyCreateAPIResponse, status_code=status.HTTP_201_CREATED)
def create_property_profile(
    property_profile: PropertyProfileCreate,
    db: Session = Depends(get_sync_db)
):
    """Create a new property profile"""
    try:
        db_property = PropertyService.create_property_profile(
            db,
            property_profile.user_id,
            property_profile
        )
        data = PropertyProfileResponse.model_validate(db_property)
        data.property_type_name = (
            db_property.property_type.name if db_property.property_type else None
        )
        return PropertyCreateAPIResponse(
            data=data,
            message="Property created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create property profile: {str(e)}"
        )


@router.get("/profile/{property_id}", response_model=PropertyGetAPIResponse)
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
        return PropertyGetAPIResponse(
            data=db_property,
            message="Property retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property profile: {str(e)}"
        )


@router.put("/profile/{property_id}", response_model=PropertyUpdateAPIResponse)
def update_property_profile(
    property_id: int,
    property_update: PropertyProfileUpdate,
    db: Session = Depends(get_sync_db)
):
    """Update a property profile"""
    try:
        db_property = PropertyService.update_property_profile(
            db,
            property_id,
            property_update
        )
        if not db_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property profile not found"
            )
        return PropertyUpdateAPIResponse(
            data=db_property,
            message="Property updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property profile: {str(e)}"
        )


@router.delete("/profile/{property_id}", response_model=PropertyDeleteAPIResponse)
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
        return PropertyDeleteAPIResponse(
            data={"property_id": property_id},
            message="Property profile deleted successfully"
        )
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


@router.patch("/{property_id}/status", response_model=PropertyStatusUpdateAPIResponse)
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
        
        return PropertyStatusUpdateAPIResponse(
            data={
                "property": updated_property,
                "new_status": new_status.value
            },
            message=status_messages[new_status]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property status: {str(e)}"
        )


@router.post("/approval", response_model=PropertyApprovalAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_property_approval(
    approval_data: PropertyApprovalCreate,
    db: Session = Depends(get_sync_db)
):
    """Create a property approval/rejection by ATP (Area Coordinator)"""
    try:
        approval = PropertyService.create_property_approval(
            db,
            approval_data.property_id,
            approval_data.atp_id,
            approval_data.approval_type,
            approval_data.verification_type.value,
            approval_data.note
        )
        
        return PropertyApprovalAPIResponse(
            status="success",
            data=PropertyApprovalResponse(
                id=approval.id,
                property_id=approval.property_id,
                atp_id=approval.atp_id,
                approval_type=approval.approval_type,
                verification_type=VerificationType(approval.verification_type.value),
                note=approval.note,
                created_at=approval.created_at,
                updated_at=approval.updated_at
            ),
            message=f"Property {approval_data.approval_type.lower()} {approval_data.verification_type.value.lower()} successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create property approval: {str(e)}"
        )


@router.get("/{property_id}/approvals", response_model=PropertyApprovalListResponse)
async def get_property_approvals(
    property_id: int,
    db: Session = Depends(get_sync_db)
):
    """Get all approvals for a specific property"""
    try:
        approvals = PropertyService.get_property_approvals(db, property_id)
        
        # Convert to response models
        approval_responses = [
            PropertyApprovalResponse(
                id=approval.id,
                property_id=approval.property_id,
                atp_id=approval.atp_id,
                approval_type=approval.approval_type,
                verification_type=VerificationType(approval.verification_type.value),
                note=approval.note,
                created_at=approval.created_at,
                updated_at=approval.updated_at
            )
            for approval in approvals
        ]
        
        return PropertyApprovalListResponse(
            status="success",
            data=approval_responses,
            message=f"Retrieved {len(approval_responses)} approval(s) for property {property_id}",
            count=len(approval_responses)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property approvals: {str(e)}"
        )


@router.patch("/{property_id}/verification-status", response_model=PropertyVerificationStatusAPIResponse)
async def update_property_verification_status(
    property_id: int,
    status_update: PropertyVerificationStatusUpdate,
    db: Session = Depends(get_sync_db)
):
    """Update property verification status (DRAFT, PENDING, APPROVED, REJECTED)"""
    try:
        updated_property = PropertyService.update_property_verification_status(
            db,
            property_id,
            status_update.verification_status
        )
        
        if not updated_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        status_messages = {
            PropertyVerificationStatus.DRAFT: "Property verification status set to DRAFT",
            PropertyVerificationStatus.PENDING: "Property verification status set to PENDING",
            PropertyVerificationStatus.APPROVED: "Property verification status set to APPROVED",
            PropertyVerificationStatus.REJECTED: "Property verification status set to REJECTED"
        }
        
        return PropertyVerificationStatusAPIResponse(
            status="success",
            data={
                "property_id": updated_property.id,
                "verification_status": updated_property.verification_status.value,
                "is_verified": updated_property.is_verified
            },
            message=status_messages[status_update.verification_status]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property verification status: {str(e)}"
        )


@router.patch("/property/atp-auto-allocate", response_model=ATPAutoAllocationAPIResponse)
async def auto_allocate_atp(
    property_id: int = Query(..., description="ID of the property to allocate ATP for"),
    db: Session = Depends(get_sync_db)
):
    """
    Automatically allocate an Area Coordinator (ATP) to a property based on:
    - Geographic proximity (searching within expanding radius: 5km to 50km)
    - Workload balance (lowest assigned_properties count)
    - Seniority (earliest created_at for tie-breaking)
    
    The endpoint searches for approved ATPs starting from 5km radius and expands
    by 5km increments up to 50km until an ATP is found.
    """
    try:
        result = PropertyService.auto_allocate_atp(db, property_id)
        
        return ATPAutoAllocationAPIResponse(
            status="success",
            data=result,
            message="ATP allocated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-allocate ATP: {str(e)}"
        )


@router.get("/property/atp-in-range", response_model=ATPInRangeAPIResponse)
def check_atp_in_range(
    property_id: int = Query(..., description="ID of the property"),
    atp_uuid: str = Query(..., description="ATP UUID (e.g. ATP-01234)"),
    radius_km: float = Query(..., gt=0, description="Radius in kilometers to check"),
    db: Session = Depends(get_sync_db)
):
    """
    Check whether an ATP (Area Coordinator) is within the given radius of a property.

    Uses property location (latitude/longitude) and ATP coordinates with haversine distance.
    Returns within_range (true/false), distance_km, and the requested radius_km.
    """
    try:
        result = PropertyService.check_atp_in_range(db, property_id, atp_uuid, radius_km)
        return ATPInRangeAPIResponse(
            status="success",
            data=result,
            message="ATP in range check completed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check ATP in range: {str(e)}"
        )
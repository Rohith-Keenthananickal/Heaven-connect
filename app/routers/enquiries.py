from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.enquiry import (
    EnquiryCreate, EnquiryUpdate, EnquiryResponse, EnquiryStatusUpdate,
    EnquirySearchRequest, EnquirySearchResponse,
    EnquiryCreateAPIResponse, EnquiryListAPIResponse, EnquiryGetAPIResponse,
    EnquiryUpdateAPIResponse, EnquiryDeleteAPIResponse, EnquiryStatusUpdateAPIResponse
)
from app.models.enquiry import EnquiryStatus
from app.services.enquiry_service import enquiry_service


router = APIRouter(prefix="/enquiries", tags=["Enquiries"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EnquiryCreateAPIResponse)
async def create_enquiry(
    enquiry: EnquiryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new enquiry"""
    try:
        db_enquiry = await enquiry_service.create_enquiry(db, obj_in=enquiry)
        return EnquiryCreateAPIResponse(
            data=db_enquiry
            # Using default message from schema
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create enquiry: {str(e)}"
        )


@router.post("/search", response_model=EnquirySearchResponse)
async def search_enquiries(
    search_request: EnquirySearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Search enquiries with pagination and filters"""
    try:
        result = await enquiry_service.search_enquiries(db, search_params=search_request.dict(exclude_unset=True))
        
        # Convert pagination dict to PaginationInfo model
        from app.schemas.base import PaginationInfo
        pagination = PaginationInfo(**result["pagination"])
        
        return EnquirySearchResponse(
            data=result["enquiries"],
            pagination=pagination
            # Using default status from schema
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search enquiries: {str(e)}"
        )


@router.get("/", response_model=EnquiryListAPIResponse)
async def get_enquiries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None, description="Filter by enquiry status"),
    db: AsyncSession = Depends(get_db)
):
    """Get all enquiries with pagination and optional filtering"""
    try:
        if status:
            # Get enquiries by specific status
            try:
                status_enum = EnquiryStatus(status)
                enquiries = await enquiry_service.get_enquiries_by_status(
                    db, status=status_enum, skip=skip, limit=limit
                )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid enquiry status: {status}"
                )
        else:
            # Get all enquiries
            enquiries = await enquiry_service.get_multi(db, skip=skip, limit=limit)
        
        return EnquiryListAPIResponse(
            data=enquiries
            # Using default message from schema
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch enquiries: {str(e)}"
        )


@router.get("/{enquiry_id}", response_model=EnquiryGetAPIResponse)
async def get_enquiry(
    enquiry_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific enquiry by ID"""
    try:
        db_enquiry = await enquiry_service.get(db, enquiry_id)
        if not db_enquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )
        return EnquiryGetAPIResponse(
            data=db_enquiry
            # Using default message from schema
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch enquiry: {str(e)}"
        )


@router.put("/{enquiry_id}", response_model=EnquiryUpdateAPIResponse)
async def update_enquiry(
    enquiry_id: int,
    enquiry_update: EnquiryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an enquiry"""
    try:
        updated_enquiry = await enquiry_service.update_enquiry(
            db, enquiry_id=enquiry_id, obj_in=enquiry_update
        )
        if not updated_enquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )
        return EnquiryUpdateAPIResponse(
            data=updated_enquiry
            # Using default message from schema
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update enquiry: {str(e)}"
        )


@router.patch("/{enquiry_id}/status", response_model=EnquiryStatusUpdateAPIResponse)
async def update_enquiry_status(
    enquiry_id: int,
    status_update: EnquiryStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update enquiry status and optional remarks"""
    try:
        updated_enquiry = await enquiry_service.update_status(
            db, enquiry_id=enquiry_id, status_update=status_update
        )
        if not updated_enquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )
        
        status_messages = {
            EnquiryStatus.PENDING: "Enquiry marked as pending",
            EnquiryStatus.PROCESSED: "Enquiry marked as processed",
            EnquiryStatus.REJECTED: "Enquiry marked as rejected",
            EnquiryStatus.CONVERTED: "Enquiry marked as converted"
        }
        
        # Create EnquiryStatusData instance for the response
        data = EnquiryStatusUpdateAPIResponse.EnquiryStatusData(
            enquiry=updated_enquiry,
            new_status=status_update.status
        )
        
        return EnquiryStatusUpdateAPIResponse(
            data=data,
            message=status_messages.get(
                status_update.status, 
                "Enquiry status updated successfully"
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update enquiry status: {str(e)}"
        )


@router.delete("/{enquiry_id}", response_model=EnquiryDeleteAPIResponse)
async def delete_enquiry(
    enquiry_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an enquiry"""
    try:
        deleted_enquiry = await enquiry_service.delete(db, id=enquiry_id)
        if not deleted_enquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )
        return EnquiryDeleteAPIResponse(
            data={"enquiry_id": enquiry_id}
            # Using default message from schema
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete enquiry: {str(e)}"
        )

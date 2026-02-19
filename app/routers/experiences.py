from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.database import get_db, get_sync_db
from app.schemas.experience import (
    ApprovalStatusData, ExperienceCreate, ExperienceUpdate, ExperienceResponse,
    ExperienceStatusUpdate, ExperienceApprovalStatusUpdate,
    ExperienceSearchRequest
)
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo
from app.models.experience import Experience, ExperienceStatus, ExperienceApprovalStatus
from app.services.experience_service import ExperienceService
from typing import List, Optional


router = APIRouter(prefix="/experiences", tags=["Experiences"])


@router.post("", response_model=BaseResponse[ExperienceResponse], status_code=status.HTTP_201_CREATED)
async def create_experience(
    experience: ExperienceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new experience"""
    try:
        db_experience = await ExperienceService.create_experience(db, experience)
        experience_response = ExperienceResponse.model_validate(db_experience)
        return BaseResponse[ExperienceResponse](
            data=experience_response,
            message="Experience created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create experience: {str(e)}"
        )


@router.get("/{experience_id}", response_model=BaseResponse[ExperienceResponse])
async def get_experience(
    experience_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific experience by ID"""
    try:
        db_experience = await ExperienceService.get_experience(db, experience_id)
        if not db_experience:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experience not found"
            )
        experience_response = ExperienceResponse.model_validate(db_experience)
        return BaseResponse[ExperienceResponse](
            data=experience_response,
            message="Experience retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch experience: {str(e)}"
        )


@router.put("/{experience_id}", response_model=BaseResponse[ExperienceResponse])
async def update_experience(
    experience_id: int,
    experience_update: ExperienceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an experience"""
    try:
        db_experience = await ExperienceService.update_experience(
            db,
            experience_id,
            experience_update
        )
        if not db_experience:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experience not found"
            )
        experience_response = ExperienceResponse.model_validate(db_experience)
        return BaseResponse[ExperienceResponse](
            data=experience_response,
            message="Experience updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update experience: {str(e)}"
        )


@router.delete("/{experience_id}", response_model=BaseResponse[ExperienceResponse])
async def delete_experience(
    experience_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an experience (soft delete)"""
    try:
        success = await ExperienceService.delete_experience(db, experience_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experience not found"
            )
        return BaseResponse[ExperienceResponse](
            data=ExperienceResponse(id=experience_id,status=ExperienceStatus.DELETED),
            message="Experience deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete experience: {str(e)}"
        )


@router.get("", response_model=PaginatedResponse[ExperienceResponse])
async def list_experiences(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    area_coordinator_id: Optional[int] = Query(None),
    status_filter: Optional[ExperienceStatus] = Query(None),
    approval_status_filter: Optional[ExperienceApprovalStatus] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all experiences with optional filters"""
    try:
        experiences = await ExperienceService.get_all_experiences(
            db,
            skip=skip,
            limit=limit,
            user_id=user_id,
            area_coordinator_id=area_coordinator_id,
            status_filter=status_filter,
            approval_status_filter=approval_status_filter
        )
        experience_responses = [
            ExperienceResponse.model_validate(exp) for exp in experiences
        ]
        return PaginatedResponse(
            data=experience_responses,
            pagination=PaginationInfo(
                page=skip // limit + 1,
                limit=limit,
                total=len(experience_responses),
                total_pages=len(experience_responses) // limit + 1,
                has_next=skip + limit < len(experience_responses),
                has_prev=skip > 0
            ),
            message="Experiences retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list experiences: {str(e)}"
        )


@router.patch("/{experience_id}/status", response_model=BaseResponse[ExperienceResponse])
async def update_experience_status(
    experience_id: int,
    status_update: ExperienceStatusUpdate,
    db: Session = Depends(get_sync_db)
):
    """Update experience status (ACTIVE, BLOCKED, DELETED)"""
    try:
        new_status = status_update.status
        
        updated_experience = ExperienceService.update_experience_status(
            db,
            experience_id,
            new_status
        )
        
        if not updated_experience:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experience not found"
            )
        
        status_messages = {
            ExperienceStatus.ACTIVE: "Experience activated successfully",
            ExperienceStatus.BLOCKED: "Experience blocked successfully",
            ExperienceStatus.DELETED: "Experience deleted successfully"
        }
        
        experience_response = ExperienceResponse.model_validate(updated_experience)
        return BaseResponse[ExperienceResponse](
            data=experience_response,
            message=status_messages[new_status]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update experience status: {str(e)}"
        )


@router.patch("/{experience_id}/approval-status", response_model=BaseResponse[ApprovalStatusData])
async def update_experience_approval_status(
    experience_id: int,
    approval_status_update: ExperienceApprovalStatusUpdate,
    db: Session = Depends(get_sync_db)
):
    """Update experience approval status (DRAFT, PENDING, APPROVED, REJECTED)"""
    try:
        new_approval_status = approval_status_update.approval_status
        
        updated_experience = ExperienceService.update_experience_approval_status(
            db,
            experience_id,
            new_approval_status
        )
        
        if not updated_experience:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experience not found"
            )
        
        status_messages = {
            ExperienceApprovalStatus.DRAFT: "Experience approval status set to DRAFT",
            ExperienceApprovalStatus.PENDING: "Experience approval status set to PENDING",
            ExperienceApprovalStatus.APPROVED: "Experience approval status set to APPROVED",
            ExperienceApprovalStatus.REJECTED: "Experience approval status set to REJECTED"
        }
        
        return BaseResponse[ApprovalStatusData](
            data=ApprovalStatusData(
                experience_id=updated_experience.id,
                approval_status=updated_experience.approval_status.value
            ),
            message=status_messages[new_approval_status]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update experience approval status: {str(e)}"
        )


@router.post("/search", response_model=PaginatedResponse)
async def search_experiences(
    search_request: ExperienceSearchRequest,
    db: Session = Depends(get_sync_db)
):
    """Search experiences with pagination and filters"""
    try:
        result = ExperienceService.search_experiences(db, search_request)
        
        return PaginatedResponse(
            data=result["experiences"],
            pagination=result["pagination"],
            message="Experiences retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search experiences: {str(e)}"
        )

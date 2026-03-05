from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.base import BaseResponse
from app.schemas.facility_master import (
    FacilityMasterCreate,
    FacilityMasterUpdate,
    FacilityMasterResponse,
    FacilityMasterListResponse,
)
from app.services.facility_master_service import facility_master_service
from app.models.property import FacilityMasterType, FacilityMasterStatus

router = APIRouter(prefix="/facility-master", tags=["Facility Master"])


@router.post("", response_model=BaseResponse[FacilityMasterResponse])
async def create_facility_master(
    payload: FacilityMasterCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new facility master entry."""
    try:
        db_facility = await facility_master_service.create(db, obj_in=payload)
        return BaseResponse[FacilityMasterResponse](
            data=FacilityMasterResponse.model_validate(db_facility),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("", response_model=BaseResponse[List[FacilityMasterListResponse]])
async def get_facility_masters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[FacilityMasterType] = Query(None, description="Filter by PROPERTY or ROOM"),
    status: Optional[FacilityMasterStatus] = Query(None, description="Filter by status (ACTIVE, BLOCKED, DELETED)"),
    db: AsyncSession = Depends(get_db),
):
    """List facility masters with pagination and optional filters."""
    try:
        filters = {}
        if type is not None:
            filters["type"] = type
        if status is not None:
            filters["status"] = status
        facilities = await facility_master_service.get_multi(
            db, skip=skip, limit=limit, filters=filters if filters else None
        )
        return BaseResponse[List[FacilityMasterListResponse]](
            data=[FacilityMasterListResponse.model_validate(f) for f in facilities],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/{facility_master_id}", response_model=BaseResponse[FacilityMasterResponse])
async def get_facility_master(
    facility_master_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single facility master by ID."""
    try:
        db_facility = await facility_master_service.get_or_404(
            db, facility_master_id, "Facility master not found"
        )
        return BaseResponse[FacilityMasterResponse](
            data=FacilityMasterResponse.model_validate(db_facility),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put("/{facility_master_id}", response_model=BaseResponse[FacilityMasterResponse])
async def update_facility_master(
    facility_master_id: int,
    payload: FacilityMasterUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a facility master."""
    try:
        db_facility = await facility_master_service.get_or_404(
            db, facility_master_id, "Facility master not found"
        )
        updated = await facility_master_service.update(
            db, db_obj=db_facility, obj_in=payload
        )
        return BaseResponse[FacilityMasterResponse](
            data=FacilityMasterResponse.model_validate(updated),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/{facility_master_id}", response_model=BaseResponse[dict])
async def delete_facility_master(
    facility_master_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a facility master."""
    try:
        deleted = await facility_master_service.delete(db, id=facility_master_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility master not found",
            )
        return BaseResponse[dict](data={"message": "Facility master deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

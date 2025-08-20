from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.otp_verifications import (
    OTPVerificationCreate, 
    OTPVerificationUpdate, 
    OTPVerificationResponse, 
    OTPVerificationListResponse
)
from app.services.otp_verifications_service import otp_verifications_service


router = APIRouter(prefix="/otp-verifications", tags=["OTP Verifications"])


@router.post("/")
async def create_otp_verification(
    otp_verification: OTPVerificationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new OTP verification"""
    try:
        db_otp = await otp_verifications_service.create(db, obj_in=otp_verification)
        return {"status": "success", "data": db_otp}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create OTP verification: {str(e)}"
        )


@router.get("/")
async def get_otp_verifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    phone_number: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all OTP verifications with pagination"""
    try:
        filters = {}
        if phone_number:
            filters["phone_number"] = phone_number
            
        otps = await otp_verifications_service.get_multi(
            db, skip=skip, limit=limit, filters=filters if filters else None
        )
        return {"status": "success", "data": otps}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch OTP verifications: {str(e)}"
        )


@router.get("/{otp_id}")
async def get_otp_verification(
    otp_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific OTP verification by ID"""
    try:
        db_otp = await otp_verifications_service.get_or_404(db, otp_id, "OTP verification not found")
        return {"status": "success", "data": db_otp}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch OTP verification: {str(e)}"
        )


@router.put("/{otp_id}")
async def update_otp_verification(
    otp_id: int,
    otp_update: OTPVerificationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an OTP verification"""
    try:
        db_otp = await otp_verifications_service.get_or_404(db, otp_id, "OTP verification not found")
        updated_otp = await otp_verifications_service.update(db, db_obj=db_otp, obj_in=otp_update)
        return {"status": "success", "data": updated_otp}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update OTP verification: {str(e)}"
        )


@router.delete("/{otp_id}")
async def delete_otp_verification(
    otp_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an OTP verification"""
    try:
        deleted_otp = await otp_verifications_service.delete(db, id=otp_id)
        if not deleted_otp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OTP verification not found"
            )
        return {"status": "success", "data": {"message": "OTP verification deleted successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete OTP verification: {str(e)}"
        )


@router.post("/verify")
async def verify_otp(
    phone_number: str,
    otp: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify an OTP"""
    try:
        db_otp = await otp_verifications_service.get_by_phone_and_otp(db, phone_number, otp)
        if not db_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Mark as used
        await otp_verifications_service.mark_as_used(db, db_otp.id)
        
        return {"status": "success", "data": {"message": "OTP verified successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )


@router.post("/cleanup-expired")
async def cleanup_expired_otps(
    db: AsyncSession = Depends(get_db)
):
    """Remove expired OTP records"""
    try:
        deleted_count = await otp_verifications_service.cleanup_expired(db)
        return {
            "status": "success", 
            "data": {"message": f"Deleted {deleted_count} expired OTP records"}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup expired OTPs: {str(e)}"
        )

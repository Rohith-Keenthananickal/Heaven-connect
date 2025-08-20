from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from app.models.user import OTPVerification
from app.schemas.otp_verifications import OTPVerificationCreate, OTPVerificationUpdate
from app.services.base_service import BaseService


class OTPVerificationsService(BaseService[OTPVerification, OTPVerificationCreate, OTPVerificationUpdate]):
    def __init__(self):
        super().__init__(OTPVerification)

    async def get_by_phone_and_otp(
        self, 
        db: AsyncSession, 
        phone_number: str, 
        otp: str
    ) -> Optional[OTPVerification]:
        """Get OTP verification by phone number and OTP code"""
        result = await db.execute(
            select(OTPVerification).where(
                and_(
                    OTPVerification.phone_number == phone_number,
                    OTPVerification.otp == otp,
                    OTPVerification.is_used == False,
                    OTPVerification.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_valid_otp(
        self, 
        db: AsyncSession, 
        phone_number: str
    ) -> Optional[OTPVerification]:
        """Get the latest valid (unused and not expired) OTP for phone number"""
        result = await db.execute(
            select(OTPVerification)
            .where(
                and_(
                    OTPVerification.phone_number == phone_number,
                    OTPVerification.is_used == False,
                    OTPVerification.expires_at > datetime.utcnow()
                )
            )
            .order_by(OTPVerification.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def mark_as_used(self, db: AsyncSession, otp_id: int) -> Optional[OTPVerification]:
        """Mark OTP as used"""
        db_obj = await self.get(db, otp_id)
        if db_obj:
            db_obj.is_used = True
            await db.commit()
            await db.refresh(db_obj)
        return db_obj

    async def cleanup_expired(self, db: AsyncSession) -> int:
        """Remove expired OTP records and return count of deleted records"""
        result = await db.execute(
            select(OTPVerification).where(
                OTPVerification.expires_at <= datetime.utcnow()
            )
        )
        expired_otps = result.scalars().all()
        
        for otp in expired_otps:
            await db.delete(otp)
        
        await db.commit()
        return len(expired_otps)


otp_verifications_service = OTPVerificationsService()

import random
import string
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.user import OTPVerification
from app.core.config import settings


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))


async def create_otp_record(db: AsyncSession, phone_number: str) -> str:
    """Create OTP record in database and return OTP"""
    # Delete any existing OTP for this phone number
    await db.execute(
        delete(OTPVerification).where(
            OTPVerification.phone_number == phone_number,
            OTPVerification.is_used == False
        )
    )
    
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    
    otp_record = OTPVerification(
        phone_number=phone_number,
        otp=otp,
        expires_at=expires_at
    )
    
    db.add(otp_record)
    await db.commit()
    
    return otp


async def verify_otp(db: AsyncSession, phone_number: str, otp: str) -> bool:
    """Verify OTP for phone number"""
    result = await db.execute(
        select(OTPVerification).where(
            OTPVerification.phone_number == phone_number,
            OTPVerification.otp == otp,
            OTPVerification.is_used == False,
            OTPVerification.expires_at > datetime.utcnow()
        )
    )
    otp_record = result.scalar_one_or_none()
    
    if not otp_record:
        return False
    
    # Mark OTP as used
    otp_record.is_used = True
    await db.commit()
    
    return True


def send_otp_sms(phone_number: str, otp: str) -> bool:
    """Send OTP via SMS (placeholder implementation)"""
    # In production, integrate with SMS service like Twilio, AWS SNS, etc.
    print(f"Sending OTP {otp} to {phone_number}")
    
    # Simulate successful SMS sending
    return True

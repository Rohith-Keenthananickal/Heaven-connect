from pydantic import BaseModel, Field
from datetime import datetime


class OTPVerificationBase(BaseModel):
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp: str = Field(..., min_length=4, max_length=6)
    expires_at: datetime
    is_used: bool = False


class OTPVerificationCreate(BaseModel):
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp: str = Field(..., min_length=4, max_length=6)
    expires_at: datetime


class OTPVerificationUpdate(BaseModel):
    is_used: bool


class OTPVerificationResponse(OTPVerificationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OTPVerificationListResponse(BaseModel):
    id: int
    phone_number: str
    is_used: bool
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

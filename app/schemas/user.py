from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from app.models.user import AuthProvider


class UserResponse(BaseModel):
    id: int
    auth_provider: AuthProvider
    email: Optional[str]
    phone_number: Optional[str]
    full_name: str
    dob: Optional[date]
    profile_image: Optional[str]
    status: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    dob: Optional[date] = None
    profile_image: Optional[str] = None

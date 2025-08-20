from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from app.models.user import AuthProvider, UserType


class UserBase(BaseModel):
    auth_provider: AuthProvider
    user_type: UserType = UserType.GUEST
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    full_name: str = Field(..., min_length=1, max_length=200)
    dob: Optional[date] = None
    profile_image: Optional[str] = Field(None, max_length=500)
    status: bool = True


class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserUpdate(BaseModel):
    auth_provider: Optional[AuthProvider] = None
    user_type: Optional[UserType] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    dob: Optional[date] = None
    profile_image: Optional[str] = Field(None, max_length=500)
    status: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    id: int
    auth_provider: AuthProvider
    user_type: UserType
    email: Optional[str]
    phone_number: Optional[str]
    full_name: str
    status: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

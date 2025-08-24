from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from app.models.user import AuthProvider, UserType, UserStatus


class UserBase(BaseModel):
    auth_provider: AuthProvider
    user_type: UserType = UserType.GUEST
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    full_name: str = Field(..., min_length=1, max_length=200)
    dob: Optional[date] = None
    profile_image: Optional[str] = Field(None, max_length=500)
    status: UserStatus = UserStatus.ACTIVE


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
    status: Optional[UserStatus] = None


class UserStatusUpdate(BaseModel):
    status: UserStatus = Field(..., description="New user status (ACTIVE, BLOCKED, DELETED)")


class UserResponse(BaseModel):
    id: int
    auth_provider: AuthProvider
    user_type: UserType
    email: Optional[str]
    phone_number: Optional[str]
    full_name: str
    dob: Optional[date]
    profile_image: Optional[str]
    status: UserStatus
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
    dob: Optional[date]
    profile_image: Optional[str]
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DateFilter(BaseModel):
    from_date: Optional[int] = Field(None, description="From date in milliseconds")
    to_date: Optional[int] = Field(None, description="To date in milliseconds")


class UserSearchRequest(BaseModel):
    user_type: Optional[List[UserType]] = Field(None, description="Filter by user types (array)")
    page: int = Field(1, ge=1, description="Page number (1-based)")
    search_query: Optional[str] = Field(None, description="Search query for name, email, or phone")
    date_filter: Optional[DateFilter] = Field(None, description="Date range filter for created_at")
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")
    status: Optional[List[UserStatus]] = Field(None, description="Filter by user statuses (array)")


class PaginationInfo(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class UserSearchResponse(BaseModel):
    status: str = "success"
    data: List[UserListResponse]
    pagination: PaginationInfo

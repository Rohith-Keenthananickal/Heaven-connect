from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Union
from datetime import datetime, date
from app.models.user import AuthProvider, UserType, UserStatus, ApprovalStatus
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo


# Specific Response Models for proper Swagger documentation
class UserCreateAPIResponse(BaseModel):
    """Response schema for user creation"""
    status: str = "success"
    data: 'UserResponse'
    message: str = "User created successfully"


class UserListAPIResponse(BaseModel):
    """Response schema for user list endpoints"""
    status: str = "success"
    data: List['UserListResponse']
    message: str = "Users retrieved successfully"


class UserGetAPIResponse(BaseModel):
    """Response schema for single user retrieval"""
    status: str = "success"
    data: 'UserResponse'
    message: str = "User retrieved successfully"


class UserUpdateAPIResponse(BaseModel):
    """Response schema for user updates"""
    status: str = "success"
    data: 'UserResponse'
    message: str = "User updated successfully"


class UserStatusUpdateAPIResponse(BaseModel):
    """Response schema for user status updates"""
    status: str = "success"
    data: dict
    message: str


class UserDeleteAPIResponse(BaseModel):
    """Response schema for user deletion"""
    status: str = "success"
    data: dict
    message: str = "User deleted successfully"


class UserProfileGetAPIResponse(BaseModel):
    """Response schema for user profile retrieval"""
    status: str = "success"
    data: dict
    message: str


class UserTypeListAPIResponse(BaseModel):
    """Response schema for users by type"""
    status: str = "success"
    data: List['UserListResponse']
    message: str


# Profile-specific schemas
class GuestProfileBase(BaseModel):
    passport_number: Optional[str] = Field(None, max_length=50)
    nationality: Optional[str] = Field(None, max_length=100)
    preferences: Optional[dict] = Field(None, description="JSON preferences object")


class GuestProfileCreate(GuestProfileBase):
    passport_number: str = Field(..., max_length=50)
    nationality: str = Field(..., max_length=100)


class GuestProfileUpdate(GuestProfileBase):
    pass


class GuestProfileResponse(GuestProfileBase):
    id: int
    
    class Config:
        from_attributes = True


class HostProfileBase(BaseModel):
    license_number: Optional[str] = Field(None, max_length=100)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    company_name: Optional[str] = Field(None, max_length=200)


class HostProfileCreate(HostProfileBase):
    license_number: str = Field(..., max_length=100)
    experience_years: int = Field(..., ge=0, le=50)


class HostProfileUpdate(HostProfileBase):
    pass


class HostProfileResponse(HostProfileBase):
    id: int
    
    class Config:
        from_attributes = True


# Bank Details schemas
class BankDetailsBase(BaseModel):
    bank_name: str = Field(..., max_length=200)
    account_holder_name: str = Field(..., max_length=200)
    account_number: str = Field(..., max_length=50)
    ifsc_code: str = Field(..., max_length=20)
    branch_name: Optional[str] = Field(None, max_length=200)
    branch_code: Optional[str] = Field(None, max_length=20)
    account_type: Optional[str] = Field(None, max_length=50, description="Savings, Current, etc.")
    bank_passbook_image: Optional[str] = Field(None, max_length=500)
    cancelled_cheque_image: Optional[str] = Field(None, max_length=500)


class BankDetailsCreate(BankDetailsBase):
    pass


class BankDetailsUpdate(BaseModel):
    bank_name: Optional[str] = Field(None, max_length=200)
    account_holder_name: Optional[str] = Field(None, max_length=200)
    account_number: Optional[str] = Field(None, max_length=50)
    ifsc_code: Optional[str] = Field(None, max_length=20)
    branch_name: Optional[str] = Field(None, max_length=200)
    branch_code: Optional[str] = Field(None, max_length=20)
    account_type: Optional[str] = Field(None, max_length=50)
    bank_passbook_image: Optional[str] = Field(None, max_length=500)
    cancelled_cheque_image: Optional[str] = Field(None, max_length=500)


class BankDetailsResponse(BankDetailsBase):
    id: int
    area_coordinator_id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Enhanced Area Coordinator schemas
class AreaCoordinatorProfileBase(BaseModel):
    atp_uuid: Optional[str] = Field(None, max_length=20, description="ATP UUID in format ATP-01234")
    region: Optional[str] = Field(None, max_length=200)
    assigned_properties: Optional[int] = Field(0, ge=0)
    
    # Approval status fields
    approval_status: Optional[ApprovalStatus] = Field(ApprovalStatus.PENDING)
    approval_date: Optional[datetime] = None
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = Field(None, max_length=500)
    
    # ID Proof and Verification fields
    id_proof_type: Optional[str] = Field(None, max_length=50, description="Aadhar, PAN, Driving License, etc.")
    id_proof_number: Optional[str] = Field(None, max_length=100)
    pancard_number: Optional[str] = Field(None, max_length=20)
    
    # Photo and Document fields
    passport_size_photo: Optional[str] = Field(None, max_length=500)
    id_proof_document: Optional[List[str]] = Field(None, description="Array of URLs to ID proof documents")
    pancard_images: Optional[List[str]] = Field(None, description="Array of URLs to PAN card images")
    address_proof_document: Optional[str] = Field(None, max_length=500)
    
    # Address fields
    district: Optional[str] = Field(None, max_length=100)
    panchayat: Optional[str] = Field(None, max_length=100)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    
    # Location coordinates
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    # Additional fields
    emergency_contact: Optional[str] = Field(None, max_length=20)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)


class AreaCoordinatorProfileCreate(AreaCoordinatorProfileBase):
    region: str = Field(..., max_length=200)
    district: str = Field(..., max_length=200)
    panchayat: str = Field(..., max_length=200)
    address_line1: str = Field(..., max_length=200)
    city: str = Field(..., max_length=200)
    state: str = Field(..., max_length=200)
    postal_code: str = Field(..., max_length=20)


class AreaCoordinatorProfileUpdate(AreaCoordinatorProfileBase):
    pass


class AreaCoordinatorProfileResponse(AreaCoordinatorProfileBase):
    id: int
    bank_details: Optional[BankDetailsResponse] = None
    
    class Config:
        from_attributes = True


# Approval schemas
class AreaCoordinatorApprovalRequest(BaseModel):
    """Request schema for approving/rejecting area coordinators"""
    approval_status: ApprovalStatus = Field(..., description="APPROVED or REJECTED")
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Required when status is REJECTED")


class AreaCoordinatorApprovalResponse(BaseModel):
    """Response schema for approval operations"""
    status: str = "success"
    data: AreaCoordinatorProfileResponse
    message: str


# User schemas
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
    
    # Profile-specific fields based on user_type
    guest_profile: Optional[GuestProfileCreate] = Field(None, description="Required when user_type is GUEST")
    host_profile: Optional[HostProfileCreate] = Field(None, description="Required when user_type is HOST")
    area_coordinator_profile: Optional[AreaCoordinatorProfileCreate] = Field(None, description="Required when user_type is AREA_COORDINATOR")


class UserUpdate(BaseModel):
    auth_provider: Optional[AuthProvider] = None
    user_type: Optional[UserType] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    full_name: Optional[str] = Field(..., min_length=1, max_length=200)
    dob: Optional[date] = None
    profile_image: Optional[str] = Field(None, max_length=500)
    status: Optional[UserStatus] = None
    
    # Profile updates
    guest_profile: Optional[GuestProfileUpdate] = None
    host_profile: Optional[HostProfileUpdate] = None
    area_coordinator_profile: Optional[AreaCoordinatorProfileUpdate] = None


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
    
    # Profile data
    guest_profile: Optional[GuestProfileResponse] = None
    host_profile: Optional[HostProfileResponse] = None
    area_coordinator_profile: Optional[AreaCoordinatorProfileResponse] = None
    
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
    
    # Profile data
    guest_profile: Optional[GuestProfileResponse] = None
    host_profile: Optional[HostProfileResponse] = None
    area_coordinator_profile: Optional[AreaCoordinatorProfileResponse] = None
    
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
    approval_status: Optional[List[ApprovalStatus]] = Field(None, description="Filter area coordinators by approval status (array)")


class UserSearchResponse(BaseModel):
    status: str = "success"
    data: List[UserListResponse]
    pagination: PaginationInfo


# Profile-specific endpoints schemas
class ProfileUpdateRequest(BaseModel):
    """Generic profile update request"""
    profile_data: Union[GuestProfileUpdate, HostProfileUpdate, AreaCoordinatorProfileUpdate]


# Response schemas for profile operations
class ProfileResponse(BaseModel):
    status: str = "success"
    data: Union[GuestProfileResponse, HostProfileResponse, AreaCoordinatorProfileResponse]
    message: str


# Bank Details specific schemas
class BankDetailsCreateRequest(BaseModel):
    bank_details: BankDetailsCreate


class BankDetailsUpdateRequest(BaseModel):
    bank_details: BankDetailsUpdate


class BankDetailsResponseWrapper(BaseModel):
    status: str = "success"
    data: BankDetailsResponse
    message: str

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.models.property import PropertyClassification, PropertyStatus, FacilityCategory, PhotoCategory
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo


# Specific Response Models for proper Swagger documentation
class PropertyCreateAPIResponse(BaseModel):
    """Response schema for property creation"""
    status: str = "success"
    data: 'PropertyProfileResponse'
    message: str = "Property created successfully"


class PropertyGetAPIResponse(BaseModel):
    """Response schema for single property retrieval"""
    status: str = "success"
    data: 'PropertyProfileResponse'
    message: str = "Property retrieved successfully"


class PropertyUpdateAPIResponse(BaseModel):
    """Response schema for property updates"""
    status: str = "success"
    data: 'PropertyProfileResponse'
    message: str = "Property updated successfully"


class PropertyDeleteAPIResponse(BaseModel):
    """Response schema for property deletion"""
    status: str = "success"
    data: dict
    message: str = "Property deleted successfully"


class PropertyStatusUpdateAPIResponse(BaseModel):
    """Response schema for property status updates"""
    status: str = "success"
    data: dict
    message: str


class PropertyTypeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Property type name (e.g., Backwater & Scenic, Hill Stations & Wildlife)")
    description: Optional[str] = Field(None, max_length=500, description="Description of the property type")
    is_active: bool = Field(True, description="Whether this property type is active")


class PropertyTypeCreate(PropertyTypeBase):
    pass


class PropertyTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class PropertyTypeResponse(PropertyTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PropertyTypeListResponse(BaseModel):
    property_types: List[PropertyTypeResponse]
    total: int


class PropertyStatusUpdate(BaseModel):
    status: PropertyStatus = Field(..., description="New property status (ACTIVE, INACTIVE, BLOCKED, DELETED)")


class PropertyBase(BaseModel):
    user_id: int = Field(..., description="ID of the user who owns the property")
    property_name: str = Field(..., min_length=1, max_length=200, description="Name of the property")
    alternate_phone: Optional[str] = Field(None, max_length=20, description="Alternate phone number")
    area_coordinator_id: Optional[int] = Field(None, description="ID of the area coordinator")
    property_type_id: Optional[int] = Field(None, description="ID of the property type")
    id_proof_type: Optional[str] = Field(None, max_length=50, description="Type of ID proof")
    id_proof_url: Optional[str] = Field(None, max_length=500, description="URL of the ID proof document")
    certificate_number: Optional[str] = Field(None, max_length=100, description="Property certificate number")
    trade_license_number: Optional[str] = Field(None, max_length=100, description="Trade license number")
    classification: PropertyClassification = Field(PropertyClassification.SILVER, description="Property classification")
    status: PropertyStatus = Field(PropertyStatus.ACTIVE, description="Property status")
    progress_step: int = Field(1, ge=1, le=10, description="Current progress step")
    is_verified: bool = Field(False, description="Whether the property is verified")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="URL of the property cover image")
    additional_images: Optional[List[str]] = Field([], max_items=20, description="List of URLs for additional property images")


class PropertyCreate(PropertyBase):
    pass


class PropertyProfileCreate(BaseModel):
    user_id: int = Field(..., description="ID of the user who owns this property")
    property_name: str = Field(..., min_length=2, max_length=255)
    alternate_phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    property_type_id: Optional[int] = Field(None, description="ID of the property type")
    id_proof_type: Optional[str] = Field(None, min_length=2, max_length=100)
    id_proof_url: Optional[str] = Field(None, max_length=500)
    certificate_number: Optional[str] = Field(None, max_length=100)
    trade_license_number: Optional[str] = Field(None, max_length=100)
    classification: PropertyClassification = PropertyClassification.SILVER
    status: PropertyStatus = PropertyStatus.ACTIVE
    progress_step: int = Field(1, ge=1, le=9)
    is_verified: bool = False
    cover_image_url: Optional[str] = Field(None, max_length=500, description="URL of the property cover image")
    additional_images: Optional[List[str]] = Field([], max_items=20, description="List of URLs for additional property images")


class PropertyProfileResponse(BaseModel):
    id: int
    property_name: Optional[str]
    alternate_phone: Optional[str]
    area_coordinator_id: Optional[int]
    property_type_id: Optional[int]
    property_type_name: Optional[str]
    classification: PropertyClassification
    status: PropertyStatus
    progress_step: int
    is_verified: bool
    cover_image_url: Optional[str]
    additional_images: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyResponse(BaseModel):
    id: int
    user_id: int
    property_name: Optional[str]
    alternate_phone: Optional[str]
    area_coordinator_id: Optional[int]
    property_type_id: Optional[int]
    property_type_name: Optional[str]
    id_proof_type: Optional[str]
    id_proof_url: Optional[str]
    certificate_number: Optional[str]
    trade_license_number: Optional[str]
    classification: PropertyClassification
    status: PropertyStatus
    progress_step: int
    is_verified: bool
    cover_image_url: Optional[str]
    additional_images: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyListResponse(BaseModel):
    properties: List[PropertyResponse]
    total: int
    skip: int
    limit: int


class PropertyProfileUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="ID of the user who owns this property")
    property_name: Optional[str] = Field(None, min_length=2, max_length=255)
    alternate_phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    property_type_id: Optional[int] = Field(None, description="ID of the property type")
    id_proof_type: Optional[str] = Field(None, min_length=2, max_length=100)
    id_proof_url: Optional[str] = Field(None, max_length=500)
    certificate_number: Optional[str] = Field(None, max_length=100)
    trade_license_number: Optional[str] = Field(None, max_length=100)
    classification: Optional[PropertyClassification] = None
    status: Optional[PropertyStatus] = None
    progress_step: Optional[int] = Field(None, ge=1, le=9)
    is_verified: Optional[bool] = None
    cover_image_url: Optional[str] = Field(None, max_length=500, description="URL of the property cover image")
    additional_images: Optional[List[str]] = Field(None, max_items=20, description="List of URLs for additional property images")


class PropertyDocumentsCreate(BaseModel):
    id_proof_type: str = Field(..., min_length=2, max_length=100)
    certificate_number: Optional[str] = Field(None, max_length=100)
    trade_license_number: Optional[str] = Field(None, max_length=100)


class RoomCreate(BaseModel):
    room_type: str = Field(..., min_length=2, max_length=100)
    count: int = Field(..., ge=1, le=50)
    amenities: Optional[List[str]] = []


class RoomResponse(BaseModel):
    id: int
    room_type: str
    count: int
    amenities: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacilityCreate(BaseModel):
    category: FacilityCategory
    details: Dict[str, Any]

    @validator('details')
    def validate_details(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError('Details must be a non-empty dictionary')
        return v


class FacilityResponse(BaseModel):
    id: int
    category: FacilityCategory
    details: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyPhotoCreate(BaseModel):
    category: PhotoCategory
    image_url: str = Field(..., max_length=500)


class PropertyPhotoResponse(BaseModel):
    id: int
    category: PhotoCategory
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class AboutSpaceCreate(BaseModel):
    description: str = Field(..., min_length=50, max_length=2000)
    house_rules: List[str] = Field(..., min_items=1)
    guest_access: List[str] = []
    interaction_style: str = Field(..., min_length=10, max_length=500)


class LocationCreate(BaseModel):
    address: str = Field(..., min_length=10, max_length=1000)
    google_map_link: Optional[str] = Field(None, max_length=1000)
    floor: Optional[str] = Field(None, max_length=50)
    elderly_friendly: bool = False


class LocationResponse(BaseModel):
    id: int
    address: str
    google_map_link: Optional[str]
    floor: Optional[str]
    elderly_friendly: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AvailabilityCreate(BaseModel):
    available_from: date
    available_to: date
    is_blocked: bool = False

    @validator('available_to')
    def validate_date_range(cls, v, values):
        if 'available_from' in values and v <= values['available_from']:
            raise ValueError('Available to date must be after available from date')
        return v


class AvailabilityResponse(BaseModel):
    id: int
    available_from: date
    available_to: date
    is_blocked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyAgreementCreate(BaseModel):
    owns_property: bool
    agreed_to_rules: bool
    allow_verification: bool
    payout_after_checkout: bool

    @validator('owns_property', 'agreed_to_rules', 'allow_verification', 'payout_after_checkout')
    def must_be_true(cls, v):
        if not v:
            raise ValueError('All agreements must be accepted')
        return v


class PropertyAgreementResponse(BaseModel):
    id: int
    owns_property: bool
    agreed_to_rules: bool
    allow_verification: bool
    payout_after_checkout: bool
    signed_at: datetime

    class Config:
        from_attributes = True


class PropertyOnboardingStatus(BaseModel):
    user_id: int
    property_id: int
    progress_step: int
    is_verified: bool
    completed_steps: Dict[str, bool]

    class Config:
        from_attributes = True


class CoordinatorAssignment(BaseModel):
    property_id: int
    coordinator_id: int


class PropertySearchRequest(BaseModel):
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    property_type_id: Optional[List[int]] = Field(None, description="Filter by property type IDs (array)")
    property_type_name: Optional[List[str]] = Field(None, description="Filter by property type names (array)")
    status: Optional[List[PropertyStatus]] = Field(None, description="Filter by property statuses (array)")
    page: int = Field(1, ge=1, description="Page number (1-based)")
    search_query: Optional[str] = Field(None, description="Search query for property name")
    date_filter: Optional["DateFilter"] = Field(None, description="Date range filter for created_at")
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")


class DateFilter(BaseModel):
    from_date: Optional[int] = Field(None, description="From date in milliseconds")
    to_date: Optional[int] = Field(None, description="To date in milliseconds")


class PaginationInfo(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PropertySearchResponse(BaseModel):
    status: str = "success"
    data: List[PropertyResponse]
    pagination: PaginationInfo 
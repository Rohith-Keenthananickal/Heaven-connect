from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import enum
from app.models.property import PropertyClassification, PropertyStatus, PropertyVerificationStatus, FacilityCategory, PhotoCategory, BedType, RoomView
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
    
    # Tourism certificate fields
    tourism_certificate_number: Optional[str] = Field(None, max_length=100, description="Tourism department certificate number")
    tourism_certificate_issued_by: Optional[str] = Field(None, max_length=200, description="Authority that issued the tourism certificate")
    tourism_certificate_photos: Optional[List[str]] = Field(None, description="Array of URLs to tourism certificate photos")
    
    # Trade license fields
    trade_license_number: Optional[str] = Field(None, max_length=100, description="Trade license number")
    trade_license_images: Optional[List[str]] = Field(None, description="Array of URLs to trade license images")
    
    # Property image fields
    cover_image: Optional[str] = Field(None, max_length=500, description="Main cover image URL for the property")
    exterior_images: Optional[List[str]] = Field(None, description="Array of URLs to exterior images")
    bedroom_images: Optional[List[str]] = Field(None, description="Array of URLs to bedroom images")
    bathroom_images: Optional[List[str]] = Field(None, description="Array of URLs to bathroom images")
    living_dining_images: Optional[List[str]] = Field(None, description="Array of URLs to living and dining room images")
    
    classification: PropertyClassification = Field(PropertyClassification.SILVER, description="Property classification")
    status: PropertyStatus = Field(PropertyStatus.ACTIVE, description="Property status")
    progress_step: int = Field(1, ge=1, le=10, description="Current progress step")
    is_verified: bool = Field(False, description="Whether the property is verified")


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
    
    # Tourism certificate fields
    tourism_certificate_number: Optional[str] = Field(None, max_length=100, description="Tourism department certificate number")
    tourism_certificate_issued_by: Optional[str] = Field(None, max_length=200, description="Authority that issued the tourism certificate")
    tourism_certificate_photos: Optional[List[str]] = Field(None, description="Array of URLs to tourism certificate photos")
    
    # Trade license fields
    trade_license_number: Optional[str] = Field(None, max_length=100, description="Trade license number")
    trade_license_images: Optional[List[str]] = Field(None, description="Array of URLs to trade license images")
    
    # Property image fields
    cover_image: Optional[str] = Field(None, max_length=500, description="Main cover image URL for the property")
    exterior_images: Optional[List[str]] = Field(None, description="Array of URLs to exterior images")
    bedroom_images: Optional[List[str]] = Field(None, description="Array of URLs to bedroom images")
    bathroom_images: Optional[List[str]] = Field(None, description="Array of URLs to bathroom images")
    living_dining_images: Optional[List[str]] = Field(None, description="Array of URLs to living and dining room images")
    
    classification: PropertyClassification = PropertyClassification.SILVER
    status: PropertyStatus = PropertyStatus.ACTIVE
    progress_step: int = Field(1, ge=1, le=9)
    is_verified: bool = False


class PropertyProfileResponse(BaseModel):
    id: int
    property_name: Optional[str]
    alternate_phone: Optional[str]
    area_coordinator_id: Optional[int]
    property_type_id: Optional[int]
    property_type_name: Optional[str]
    classification: PropertyClassification
    status: PropertyStatus
    verification_status: PropertyVerificationStatus
    progress_step: int
    is_verified: bool
    
    # Property image fields
    cover_image: Optional[str]
    exterior_images: Optional[List[str]]
    bedroom_images: Optional[List[str]]
    bathroom_images: Optional[List[str]]
    living_dining_images: Optional[List[str]]
    
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
    
    # Tourism certificate fields
    tourism_certificate_number: Optional[str]
    tourism_certificate_issued_by: Optional[str]
    tourism_certificate_photos: Optional[List[str]]
    
    # Trade license fields
    trade_license_number: Optional[str]
    trade_license_images: Optional[List[str]]
    
    # Property image fields
    cover_image: Optional[str]
    exterior_images: Optional[List[str]]
    bedroom_images: Optional[List[str]]
    bathroom_images: Optional[List[str]]
    living_dining_images: Optional[List[str]]
    
    classification: PropertyClassification
    status: PropertyStatus
    verification_status: PropertyVerificationStatus
    progress_step: int
    is_verified: bool
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
    max_occupancy: int = Field(..., ge=1, le=20, description="Maximum number of guests that can occupy this room")
    bed_type: BedType = Field(..., description="Type of bed in the room")
    view: RoomView = Field(..., description="View from the room")
    amenities: Optional[List[str]] = []


class RoomResponse(BaseModel):
    id: int
    room_type: str
    count: int
    max_occupancy: int
    bed_type: BedType
    view: RoomView
    amenities: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacilityCreate(BaseModel):
    facility_name: str = Field(..., min_length=1, max_length=200, description="Name of the facility")
    facility_description: Optional[str] = Field(None, max_length=1000, description="Description of the facility")
    category: FacilityCategory
    details: Dict[str, Any]

    @validator('details')
    def validate_details(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError('Details must be a non-empty dictionary')
        return v


class FacilityResponse(BaseModel):
    id: int
    facility_name: str
    facility_description: Optional[str]
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
    
    # Nearby places information
    nearby_airport: Optional[str] = Field(None, max_length=200, description="Nearest airport name")
    distance_to_airport: Optional[str] = Field(None, max_length=50, description="Distance to airport (e.g., '25 km', '30 minutes')")
    nearest_railway_station: Optional[str] = Field(None, max_length=200, description="Nearest railway station name")
    distance_to_railway_station: Optional[str] = Field(None, max_length=50, description="Distance to railway station (e.g., '10 km', '15 minutes')")
    nearest_bus_stand: Optional[str] = Field(None, max_length=200, description="Nearest bus stand name")
    distance_to_bus_stand: Optional[str] = Field(None, max_length=50, description="Distance to bus stand (e.g., '2 km', '5 minutes')")


class LocationResponse(BaseModel):
    id: int
    address: str
    google_map_link: Optional[str]
    floor: Optional[str]
    elderly_friendly: bool
    
    # Nearby places information
    nearby_airport: Optional[str]
    distance_to_airport: Optional[str]
    nearest_railway_station: Optional[str]
    distance_to_railway_station: Optional[str]
    nearest_bus_stand: Optional[str]
    distance_to_bus_stand: Optional[str]
    
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
    verification_status: Optional[List[PropertyVerificationStatus]] = Field(None, description="Filter by property verification statuses (array)")
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


# Property Approval Schemas
# Note: Re-export the enum from models for consistency
from app.models.property import VerificationStatus as VerificationTypeEnum


class VerificationType(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class PropertyApprovalCreate(BaseModel):
    property_id: int = Field(..., description="ID of the property to approve/reject")
    atp_id: int = Field(..., description="ID of the Area Coordinator/ATP")
    approval_type: str = Field(..., min_length=1, max_length=100, description="Type of approval (e.g., PERSONAL_DETAILS, DOCUMENTS, PROPERTY_DETAILS)")
    verification_type: VerificationType = Field(..., description="APPROVED or REJECTED")
    note: Optional[str] = Field(None, max_length=1000, description="Notes or comments from the ATP")


class PropertyApprovalResponse(BaseModel):
    id: int
    property_id: int
    atp_id: int
    approval_type: str
    verification_type: VerificationType
    note: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PropertyApprovalAPIResponse(BaseModel):
    status: str = "success"
    data: PropertyApprovalResponse
    message: str


class PropertyApprovalListResponse(BaseModel):
    status: str = "success"
    data: List[PropertyApprovalResponse]
    message: str
    count: int


class PropertyVerificationStatusUpdate(BaseModel):
    verification_status: PropertyVerificationStatus = Field(..., description="New verification status (DRAFT, PENDING, APPROVED, REJECTED)")


class PropertyVerificationStatusAPIResponse(BaseModel):
    status: str = "success"
    data: dict
    message: str 
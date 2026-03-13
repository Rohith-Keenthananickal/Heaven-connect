from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import enum
from app.models.property import PropertyClassification, PropertyStatus, PropertyVerificationStatus, FacilityCategory, PhotoCategory, BedType, RoomView, SegmentStatus, SegmentType
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo
from app.schemas.users import AreaCoordinatorProfileResponse


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


# Segment (master) schemas
class SegmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Segment name")
    description: Optional[str] = Field(None, max_length=500, description="Description of the segment")
    type: SegmentType = Field(SegmentType.PROPERTY, description="Segment type (PROPERTY, EXPERIENCE)")
    status: SegmentStatus = Field(SegmentStatus.ACTIVE, description="Segment status (ACTIVE, INACTIVE)")


class SegmentCreate(SegmentBase):
    pass


class SegmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[SegmentType] = None
    status: Optional[SegmentStatus] = None


class SegmentResponse(SegmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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


# Property Details Schemas (must be defined before PropertyProfileCreate)
class PropertyDetailsBase(BaseModel):
    """Base schema for property details"""
    about_space: Optional[str] = Field(None, max_length=5000, description="Description of the property space")
    host_languages: Optional[List[str]] = Field(None, description="Array of languages the host speaks (e.g., ['English', 'Hindi', 'Malayalam'])")
    other_name: Optional[str] = Field(None, max_length=255, description="Alternate name for the property")
    nearby_activities: Optional[List[str]] = Field(None, description="Array of nearby activities (e.g., ['Beach', 'Trekking', 'Water Sports'])")
    checkin_time: Optional[str] = Field(None, max_length=20, description="Check-in time (e.g., '14:00' or '2:00 PM')")
    checkout_time: Optional[str] = Field(None, max_length=20, description="Check-out time (e.g., '11:00' or '11:00 AM')")
    smoking_allowed: bool = Field(False, description="Whether smoking is allowed")
    pets_allowed: bool = Field(False, description="Whether pets are allowed")
    alcohol_allowed: bool = Field(False, description="Whether alcohol is allowed")
    visitor_policy: Optional[str] = Field(None, max_length=1000, description="Policy regarding visitors")
    quiet_hours: Optional[str] = Field(None, max_length=200, description="Quiet hours policy (e.g., '10:00 PM - 7:00 AM')")
    comfort_services: bool = Field(False, description="Whether comfort services are available")
    meals_available: bool = Field(False, description="Whether meals are available")
    airport_pickup: bool = Field(False, description="Whether airport pickup service is available")
    laundry_service: bool = Field(False, description="Whether laundry service is available")
    housekeeping_frequency: Optional[str] = Field(None, max_length=100, description="Housekeeping frequency (e.g., 'Daily', 'Weekly', 'On Request')")


class PropertyDetailsCreate(PropertyDetailsBase):
    """Schema for creating property details"""
    pass


class PropertyDetailsUpdate(BaseModel):
    """Schema for updating property details - all fields optional"""
    about_space: Optional[str] = Field(None, max_length=5000, description="Description of the property space")
    host_languages: Optional[List[str]] = Field(None, description="Array of languages the host speaks")
    other_name: Optional[str] = Field(None, max_length=255, description="Alternate name for the property")
    nearby_activities: Optional[List[str]] = Field(None, description="Array of nearby activities")
    checkin_time: Optional[str] = Field(None, max_length=20, description="Check-in time")
    checkout_time: Optional[str] = Field(None, max_length=20, description="Check-out time")
    smoking_allowed: Optional[bool] = Field(None, description="Whether smoking is allowed")
    pets_allowed: Optional[bool] = Field(None, description="Whether pets are allowed")
    alcohol_allowed: Optional[bool] = Field(None, description="Whether alcohol is allowed")
    visitor_policy: Optional[str] = Field(None, max_length=1000, description="Policy regarding visitors")
    quiet_hours: Optional[str] = Field(None, max_length=200, description="Quiet hours policy")
    comfort_services: Optional[bool] = Field(None, description="Whether comfort services are available")
    meals_available: Optional[bool] = Field(None, description="Whether meals are available")
    airport_pickup: Optional[bool] = Field(None, description="Whether airport pickup service is available")
    laundry_service: Optional[bool] = Field(None, description="Whether laundry service is available")
    housekeeping_frequency: Optional[str] = Field(None, max_length=100, description="Housekeeping frequency")


class PropertyDetailsResponse(PropertyDetailsBase):
    """Schema for property details response"""
    id: int
    property_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyProfileCreate(BaseModel):
    user_id: int = Field(..., description="ID of the user who owns this property")
    property_name: str = Field(..., min_length=2, max_length=255)
    alternate_phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    atp_id: Optional[int] = Field(None, description="Optional area coordinator (ATP) ID to assign to this property")
    property_type_id: Optional[int] = Field(None, description="ID of the property type")
    segment_id: Optional[int] = Field(None, description="ID of the segment")
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
    
    # Property details (optional during creation)
    property_details: Optional[PropertyDetailsCreate] = Field(None, description="Property operational details, policies, and services")


class PropertyProfileResponse(BaseModel):
    id: int
    property_name: Optional[str] = None
    alternate_phone: Optional[str] = None
    area_coordinator_id: Optional[int] = None
    property_type_id: Optional[int] = None
    property_type_name: Optional[str] = None  # Populated from property_type relationship when building response
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
    
    # Property details
    property_details: Optional[PropertyDetailsResponse] = None
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyResponse(BaseModel):
    id: int
    user_id: int
    property_name: Optional[str] = None
    alternate_phone: Optional[str] = None
    area_coordinator_id: Optional[int] = None
    property_type_id: Optional[int] = None
    property_type_name: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_url: Optional[str] = None
    certificate_number: Optional[str] = None
    
    # Tourism certificate fields
    tourism_certificate_number: Optional[str] = None
    tourism_certificate_issued_by: Optional[str] = None
    tourism_certificate_photos: Optional[List[str]] = None
    
    # Trade license fields
    trade_license_number: Optional[str] = None
    trade_license_images: Optional[List[str]] = None
    
    # Property image fields
    cover_image: Optional[str] = None
    exterior_images: Optional[List[str]] = None
    bedroom_images: Optional[List[str]] = None
    bathroom_images: Optional[List[str]] = None
    living_dining_images: Optional[List[str]] = None
    
    classification: PropertyClassification
    status: PropertyStatus
    verification_status: PropertyVerificationStatus
    progress_step: int
    is_verified: bool
    
    # Property details
    property_details: Optional[PropertyDetailsResponse] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={},
        # Exclude None values when serializing to JSON
        json_schema_extra={
            "example": {}
        }
    )
    
    def model_dump(self, **kwargs):
        """Override model_dump to exclude None values by default"""
        if 'exclude_none' not in kwargs:
            kwargs['exclude_none'] = True
        return super().model_dump(**kwargs)


class PropertyListResponse(BaseModel):
    properties: List[PropertyResponse]
    total: int
    skip: int
    limit: int


class PropertyProfileUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="ID of the user who owns this property")
    property_name: Optional[str] = Field(None, min_length=2, max_length=255)
    alternate_phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    atp_id: Optional[int] = Field(None, description="Optional area coordinator (ATP) ID to assign to this property")
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
    
    # Property details (optional during update)
    property_details: Optional[PropertyDetailsUpdate] = Field(None, description="Property operational details, policies, and services")


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
    facility_master_id: Optional[int] = Field(None, description="ID of the facility master")


class FacilityResponse(BaseModel):
    id: int
    facility_name: Optional[str] = None
    facility_description: Optional[str] = None
    category: FacilityCategory
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
    experience_id: Optional[int]
    property_id: Optional[int]
    
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
    area_coordinator_id: Optional[int] = Field(None, description="Filter by area coordinator ID")
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


class ATPAutoAllocationResponse(BaseModel):
    """Response data for ATP auto-allocation"""
    property_id: int
    area_coordinator_id: int
    atp_uuid: Optional[str]
    distance_km: float
    search_radius_km: int


class ATPAutoAllocationAPIResponse(BaseModel):
    """Response schema for ATP auto-allocation endpoint"""
    status: str = "success"
    data: ATPAutoAllocationResponse
    message: str


class ATPInRangeResponse(BaseModel):
    """Response data for ATP-in-range check"""
    property_id: int
    atp_uuid: str
    radius_km: float
    distance_km: float
    within_range: bool
    atp_details: AreaCoordinatorProfileResponse


class ATPInRangeAPIResponse(BaseModel):
    """Response schema for ATP-in-range check endpoint"""
    status: str = "success"
    data: ATPInRangeResponse
    message: str

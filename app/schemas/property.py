from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.models.property import PropertyClassification, FacilityCategory, PhotoCategory


class PropertyCreate(BaseModel):
    user_id: int = Field(..., description="ID of the user who owns this property")
    property_name: str = Field(..., min_length=2, max_length=255)
    alternate_phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    id_proof_type: Optional[str] = Field(None, min_length=2, max_length=100)
    id_proof_url: Optional[str] = Field(None, max_length=500)
    certificate_number: Optional[str] = Field(None, max_length=100)
    trade_license_number: Optional[str] = Field(None, max_length=100)
    classification: PropertyClassification = PropertyClassification.SILVER
    progress_step: int = Field(1, ge=1, le=9)
    is_verified: bool = False


class PropertyProfileCreate(BaseModel):
    user_id: int = Field(..., description="ID of the user who owns this property")
    property_name: str = Field(..., min_length=2, max_length=255)
    alternate_phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    id_proof_type: Optional[str] = Field(None, min_length=2, max_length=100)
    id_proof_url: Optional[str] = Field(None, max_length=500)
    certificate_number: Optional[str] = Field(None, max_length=100)
    trade_license_number: Optional[str] = Field(None, max_length=100)
    classification: PropertyClassification = PropertyClassification.SILVER
    progress_step: int = Field(1, ge=1, le=9)
    is_verified: bool = False


class PropertyProfileResponse(BaseModel):
    id: int
    property_name: Optional[str]
    alternate_phone: Optional[str]
    area_coordinator_id: Optional[int]
    classification: PropertyClassification
    progress_step: int
    is_verified: bool
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
    id_proof_type: Optional[str]
    id_proof_url: Optional[str]
    certificate_number: Optional[str]
    trade_license_number: Optional[str]
    classification: PropertyClassification
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
    id_proof_type: Optional[str] = Field(None, min_length=2, max_length=100)
    id_proof_url: Optional[str] = Field(None, max_length=500)
    certificate_number: Optional[str] = Field(None, max_length=100)
    trade_license_number: Optional[str] = Field(None, max_length=100)
    classification: Optional[PropertyClassification] = None
    progress_step: Optional[int] = Field(None, ge=1, le=9)
    is_verified: Optional[bool] = None


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
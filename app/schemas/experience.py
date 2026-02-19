from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.experience import DurationUnit, ExperienceStatus, ExperienceApprovalStatus
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo


class ApprovalStatusData(BaseModel):
    experience_id: int
    approval_status: ExperienceApprovalStatus

# Base schemas
class ExperienceBase(BaseModel):
    user_id: int = Field(..., description="ID of the user who owns the experience")
    title: str = Field(..., min_length=1, max_length=255, description="Title of the experience")
    category: Optional[str] = Field(None, max_length=100, description="Category of the experience")
    subcategory: Optional[str] = Field(None, max_length=100, description="Subcategory of the experience")
    duration: Optional[int] = Field(None, ge=1, description="Duration value")
    duration_unit: Optional[DurationUnit] = Field(None, description="Duration unit: MINUTE, HOUR, or DAY")
    group_size: Optional[int] = Field(None, ge=1, description="Maximum group size")
    languages: Optional[List[str]] = Field(None, description="Array of language codes or names")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed description of the experience")
    included: Optional[List[str]] = Field(None, description="Array of items included in the experience")
    photos: Optional[List[str]] = Field(None, description="Array of photo URLs")
    video_url: Optional[str] = Field(None, max_length=500, description="URL to video content")
    safety_items: Optional[List[str]] = Field(None, description="Array of safety items or guidelines")
    price: Optional[float] = Field(None, ge=0, description="Price of the experience")
    is_price_by_guest: bool = Field(True, description="Whether price is per guest (True) or per group (False)")
    included_in_price: Optional[List[str]] = Field(None, description="Array of items included in the price")
    legal_declarations: Optional[List[str]] = Field(None, description="Array of legal declarations or disclaimers")
    area_coordinator_id: Optional[int] = Field(None, description="ID of the area coordinator")
    status: ExperienceStatus = Field(ExperienceStatus.ACTIVE, description="Experience status")
    approval_status: ExperienceApprovalStatus = Field(ExperienceApprovalStatus.DRAFT, description="Approval status")


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    duration: Optional[int] = Field(None, ge=1)
    duration_unit: Optional[DurationUnit] = None
    group_size: Optional[int] = Field(None, ge=1)
    languages: Optional[List[str]] = None
    description: Optional[str] = Field(None, max_length=5000)
    included: Optional[List[str]] = None
    photos: Optional[List[str]] = None
    video_url: Optional[str] = Field(None, max_length=500)
    safety_items: Optional[List[str]] = None
    price: Optional[float] = Field(None, ge=0)
    is_price_by_guest: Optional[bool] = None
    included_in_price: Optional[List[str]] = None
    legal_declarations: Optional[List[str]] = None
    area_coordinator_id: Optional[int] = None
    status: Optional[ExperienceStatus] = None


class ExperienceResponse(BaseModel):
    id: int
    user_id: int
    area_coordinator_id: Optional[int]
    title: str
    category: Optional[str]
    subcategory: Optional[str]
    duration: Optional[int]
    duration_unit: Optional[DurationUnit]
    group_size: Optional[int]
    languages: Optional[List[str]]
    description: Optional[str]
    included: Optional[List[str]]
    photos: Optional[List[str]]
    video_url: Optional[str]
    safety_items: Optional[List[str]]
    price: Optional[float]
    is_price_by_guest: bool
    included_in_price: Optional[List[str]]
    legal_declarations: Optional[List[str]]
    status: ExperienceStatus
    approval_status: ExperienceApprovalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExperienceListResponse(BaseModel):
    experiences: List[ExperienceResponse]
    total: int
    skip: int
    limit: int


class ExperienceStatusUpdate(BaseModel):
    status: ExperienceStatus = Field(..., description="New experience status (ACTIVE, BLOCKED, DELETED)")


class ExperienceApprovalStatusUpdate(BaseModel):
    approval_status: ExperienceApprovalStatus = Field(..., description="New approval status (DRAFT, PENDING, APPROVED, REJECTED)")


class ExperienceSearchRequest(BaseModel):
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    area_coordinator_id: Optional[int] = Field(None, description="Filter by area coordinator ID")
    category: Optional[str] = Field(None, description="Filter by category")
    status: Optional[List[ExperienceStatus]] = Field(None, description="Filter by experience statuses (array)")
    approval_status: Optional[List[ExperienceApprovalStatus]] = Field(None, description="Filter by approval statuses (array)")
    page: int = Field(1, ge=1, description="Page number (1-based)")
    search_query: Optional[str] = Field(None, description="Search query for experience title")
    limit: int = Field(20, ge=1, le=100, description="Number of items per page")


# Use BaseResponse and PaginatedResponse directly
# Type aliases for better type hints in routers
ExperienceCreateAPIResponse = BaseResponse
ExperienceGetAPIResponse = BaseResponse
ExperienceUpdateAPIResponse = BaseResponse
ExperienceDeleteAPIResponse = BaseResponse
ExperienceStatusUpdateAPIResponse = BaseResponse
ExperienceApprovalStatusUpdateAPIResponse = BaseResponse
ExperienceSearchResponse = PaginatedResponse

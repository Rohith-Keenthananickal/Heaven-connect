from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo


# Specific Response Models for proper Swagger documentation
class CorporationCreateAPIResponse(BaseModel):
    """Response schema for corporation creation"""
    status: str = "success"
    data: 'CorporationResponse'
    message: str = "Corporation created successfully"


class CorporationListAPIResponse(BaseModel):
    """Response schema for corporation list endpoints"""
    status: str = "success"
    data: List['CorporationListResponse']
    message: str = "Corporations retrieved successfully"


class CorporationGetAPIResponse(BaseModel):
    """Response schema for single corporation retrieval"""
    status: str = "success"
    data: 'CorporationResponse'
    message: str = "Corporation retrieved successfully"


class CorporationUpdateAPIResponse(BaseModel):
    """Response schema for corporation updates"""
    status: str = "success"
    data: 'CorporationResponse'
    message: str = "Corporation updated successfully"


class CorporationDeleteAPIResponse(BaseModel):
    """Response schema for corporation deletion"""
    status: str = "success"
    data: dict
    message: str = "Corporation deleted successfully"


class CorporationWithDistrictAPIResponse(BaseModel):
    """Response schema for corporation with district"""
    status: str = "success"
    data: 'CorporationWithDistrictResponse'
    message: str = "Corporation with district retrieved successfully"


class CorporationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Name of the corporation")
    district_id: int = Field(..., gt=0, description="ID of the district this corporation belongs to")
    code: Optional[str] = Field(None, max_length=20, description="Official corporation code")
    description: Optional[str] = Field(None, description="Description of the corporation")
    population: Optional[int] = Field(None, gt=0, description="Population of the corporation")
    area_sq_km: Optional[float] = Field(None, gt=0, description="Area of the corporation in square kilometers")
    mayor_name: Optional[str] = Field(None, max_length=100, description="Name of the mayor")
    established_year: Optional[int] = Field(None, ge=1800, le=2030, description="Year when the corporation was established")
    is_active: bool = Field(True, description="Whether the corporation is active")


class CorporationCreate(CorporationBase):
    pass


class CorporationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    district_id: Optional[int] = Field(None, gt=0)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    population: Optional[int] = Field(None, gt=0)
    area_sq_km: Optional[float] = Field(None, gt=0)
    mayor_name: Optional[str] = Field(None, max_length=100)
    established_year: Optional[int] = Field(None, ge=1800, le=2030)
    is_active: Optional[bool] = None


class CorporationResponse(CorporationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CorporationListResponse(BaseModel):
    id: int
    name: str
    district_id: int
    code: Optional[str]
    population: Optional[int]
    area_sq_km: Optional[float]
    mayor_name: Optional[str]
    established_year: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CorporationWithDistrictResponse(CorporationResponse):
    district: "DistrictResponse"


# Import here to avoid circular imports
from .districts import DistrictResponse

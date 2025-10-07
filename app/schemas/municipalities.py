from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo


# Specific Response Models for proper Swagger documentation
class MunicipalityCreateAPIResponse(BaseModel):
    """Response schema for municipality creation"""
    status: str = "success"
    data: 'MunicipalityResponse'
    message: str = "Municipality created successfully"


class MunicipalityListAPIResponse(BaseModel):
    """Response schema for municipality list endpoints"""
    status: str = "success"
    data: List['MunicipalityListResponse']
    message: str = "Municipalities retrieved successfully"


class MunicipalityGetAPIResponse(BaseModel):
    """Response schema for single municipality retrieval"""
    status: str = "success"
    data: 'MunicipalityResponse'
    message: str = "Municipality retrieved successfully"


class MunicipalityUpdateAPIResponse(BaseModel):
    """Response schema for municipality updates"""
    status: str = "success"
    data: 'MunicipalityResponse'
    message: str = "Municipality updated successfully"


class MunicipalityDeleteAPIResponse(BaseModel):
    """Response schema for municipality deletion"""
    status: str = "success"
    data: dict
    message: str = "Municipality deleted successfully"


class MunicipalityWithDistrictAPIResponse(BaseModel):
    """Response schema for municipality with district"""
    status: str = "success"
    data: 'MunicipalityWithDistrictResponse'
    message: str = "Municipality with district retrieved successfully"


class MunicipalityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Name of the municipality")
    district_id: int = Field(..., gt=0, description="ID of the district this municipality belongs to")
    code: Optional[str] = Field(None, max_length=20, description="Official municipality code")
    description: Optional[str] = Field(None, description="Description of the municipality")
    population: Optional[int] = Field(None, gt=0, description="Population of the municipality")
    area_sq_km: Optional[float] = Field(None, gt=0, description="Area of the municipality in square kilometers")
    chairman_name: Optional[str] = Field(None, max_length=100, description="Name of the chairman")
    established_year: Optional[int] = Field(None, ge=1800, le=2030, description="Year when the municipality was established")
    municipality_type: Optional[str] = Field(None, max_length=50, description="Type/grade of the municipality (e.g., Grade A, Grade B, Grade C)")
    is_active: bool = Field(True, description="Whether the municipality is active")


class MunicipalityCreate(MunicipalityBase):
    pass


class MunicipalityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    district_id: Optional[int] = Field(None, gt=0)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    population: Optional[int] = Field(None, gt=0)
    area_sq_km: Optional[float] = Field(None, gt=0)
    chairman_name: Optional[str] = Field(None, max_length=100)
    established_year: Optional[int] = Field(None, ge=1800, le=2030)
    municipality_type: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class MunicipalityResponse(MunicipalityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MunicipalityListResponse(BaseModel):
    id: int
    name: str
    district_id: int
    code: Optional[str]
    population: Optional[int]
    area_sq_km: Optional[float]
    chairman_name: Optional[str]
    established_year: Optional[int]
    municipality_type: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MunicipalityWithDistrictResponse(MunicipalityResponse):
    district: "DistrictResponse"


# Import here to avoid circular imports
from .districts import DistrictResponse

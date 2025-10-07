from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo


# Specific Response Models for proper Swagger documentation
class DistrictCreateAPIResponse(BaseModel):
    """Response schema for district creation"""
    status: str = "success"
    data: 'DistrictResponse'
    message: str = "District created successfully"


class DistrictListAPIResponse(BaseModel):
    """Response schema for district list endpoints"""
    status: str = "success"
    data: List['DistrictListResponse']
    message: str = "Districts retrieved successfully"


class DistrictGetAPIResponse(BaseModel):
    """Response schema for single district retrieval"""
    status: str = "success"
    data: 'DistrictResponse'
    message: str = "District retrieved successfully"


class DistrictUpdateAPIResponse(BaseModel):
    """Response schema for district updates"""
    status: str = "success"
    data: 'DistrictResponse'
    message: str = "District updated successfully"


class DistrictDeleteAPIResponse(BaseModel):
    """Response schema for district deletion"""
    status: str = "success"
    data: dict
    message: str = "District deleted successfully"


class DistrictWithPanchayatsAPIResponse(BaseModel):
    """Response schema for district with panchayats"""
    status: str = "success"
    data: 'DistrictWithPanchayatsResponse'
    message: str = "District with panchayats retrieved successfully"


class DistrictBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Name of the district")
    state: str = Field(..., min_length=2, max_length=100, description="State where the district is located")
    code: Optional[str] = Field(None, max_length=20, description="Official district code")
    description: Optional[str] = Field(None, description="Description of the district")
    is_active: bool = Field(True, description="Whether the district is active")


class DistrictCreate(DistrictBase):
    pass


class DistrictUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DistrictResponse(DistrictBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DistrictListResponse(BaseModel):
    id: int
    name: str
    state: str
    code: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DistrictWithPanchayatsResponse(DistrictResponse):
    grama_panchayats: List["GramaPanchayatResponse"] = []


class DistrictWithAllLocalBodiesResponse(DistrictResponse):
    grama_panchayats: List["GramaPanchayatResponse"] = []
    corporations: List["CorporationResponse"] = []
    municipalities: List["MunicipalityResponse"] = []


# Import here to avoid circular imports
from .grama_panchayats import GramaPanchayatResponse
from .corporations import CorporationResponse
from .municipalities import MunicipalityResponse

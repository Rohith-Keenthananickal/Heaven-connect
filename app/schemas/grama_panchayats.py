from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GramaPanchayatBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Name of the grama panchayat")
    district_id: int = Field(..., gt=0, description="ID of the district this panchayat belongs to")
    code: Optional[str] = Field(None, max_length=20, description="Official panchayat code")
    description: Optional[str] = Field(None, description="Description of the grama panchayat")
    population: Optional[int] = Field(None, gt=0, description="Population of the panchayat")
    area_sq_km: Optional[float] = Field(None, gt=0, description="Area of the panchayat in square kilometers")
    is_active: bool = Field(True, description="Whether the panchayat is active")


class GramaPanchayatCreate(GramaPanchayatBase):
    pass


class GramaPanchayatUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    district_id: Optional[int] = Field(None, gt=0)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    population: Optional[int] = Field(None, gt=0)
    area_sq_km: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class GramaPanchayatResponse(GramaPanchayatBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GramaPanchayatListResponse(BaseModel):
    id: int
    name: str
    district_id: int
    code: Optional[str]
    population: Optional[int]
    area_sq_km: Optional[float]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class GramaPanchayatWithDistrictResponse(GramaPanchayatResponse):
    district: "DistrictResponse"


# Import here to avoid circular imports
from .districts import DistrictResponse

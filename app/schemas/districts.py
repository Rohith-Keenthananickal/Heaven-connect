from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


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


# Import here to avoid circular imports
from .grama_panchayats import GramaPanchayatResponse

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.property import FacilityCategory


class FacilityBase(BaseModel):
    property_id: int
    category: FacilityCategory
    details: Dict[str, Any]
    
    @field_validator('details')
    @classmethod
    def validate_details(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError('Details must be a non-empty dictionary')
        return v


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    category: Optional[FacilityCategory] = None
    details: Optional[Dict[str, Any]] = None
    
    @field_validator('details')
    @classmethod
    def validate_details(cls, v):
        if v is not None and (not v or not isinstance(v, dict)):
            raise ValueError('Details must be a non-empty dictionary')
        return v


class FacilityResponse(FacilityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FacilityListResponse(BaseModel):
    id: int
    property_id: int
    category: FacilityCategory
    created_at: datetime
    
    class Config:
        from_attributes = True

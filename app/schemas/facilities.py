from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.property import FacilityCategory, PropertyClassification


class FacilityBase(BaseModel):
    facility_name: str = Field(..., min_length=1, max_length=200, description="Name of the facility")
    facility_description: Optional[str] = Field(None, max_length=1000, description="Description of the facility")
    property_id: Optional[int] = Field(None, description="Optional property ID for property-specific facilities")
    category: FacilityCategory
    property_classification: Optional[PropertyClassification] = Field(None, description="Property classification this facility applies to (for common facilities)")
    details: Dict[str, Any]
    is_common: bool = Field(False, description="Whether this is a common facility available to all properties")
    
    @field_validator('details')
    @classmethod
    def validate_details(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError('Details must be a non-empty dictionary')
        return v
    
    @model_validator(mode='after')
    def validate_property_or_classification(self):
        # Ensure either property_id or property_classification is provided
        if not self.property_id and not self.property_classification:
            raise ValueError('Either property_id or property_classification must be provided')
        return self


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    facility_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name of the facility")
    facility_description: Optional[str] = Field(None, max_length=1000, description="Description of the facility")
    property_id: Optional[int] = Field(None, description="Optional property ID for property-specific facilities")
    category: Optional[FacilityCategory] = None
    property_classification: Optional[PropertyClassification] = Field(None, description="Property classification this facility applies to (for common facilities)")
    details: Optional[Dict[str, Any]] = None
    is_common: Optional[bool] = Field(None, description="Whether this is a common facility available to all properties")
    
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
    facility_name: str
    facility_description: Optional[str]
    property_id: Optional[int]
    category: FacilityCategory
    property_classification: Optional[PropertyClassification]
    is_common: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

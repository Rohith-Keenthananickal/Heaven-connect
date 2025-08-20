from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date


class AvailabilityBase(BaseModel):
    property_id: int
    available_from: date
    available_to: date
    is_blocked: bool = False
    
    @field_validator('available_to')
    @classmethod
    def validate_date_range(cls, v, info):
        if info.data.get('available_from') and v <= info.data['available_from']:
            raise ValueError('Available to date must be after available from date')
        return v


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    available_from: Optional[date] = None
    available_to: Optional[date] = None
    is_blocked: Optional[bool] = None
    
    @field_validator('available_to')
    @classmethod
    def validate_date_range(cls, v, info):
        if v is not None and info.data.get('available_from') is not None:
            if v <= info.data['available_from']:
                raise ValueError('Available to date must be after available from date')
        return v


class AvailabilityResponse(AvailabilityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AvailabilityListResponse(BaseModel):
    id: int
    property_id: int
    available_from: date
    available_to: date
    is_blocked: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

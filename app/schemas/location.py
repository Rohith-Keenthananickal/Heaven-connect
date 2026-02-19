from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LocationBase(BaseModel):
    property_id: Optional[int] = None
    experience_id: Optional[int] = None
    address: str = Field(..., min_length=5, max_length=1000)
    google_map_link: Optional[str] = Field(None, max_length=1000)
    floor: Optional[str] = Field(None, max_length=50)
    elderly_friendly: bool = False


class LocationCreate(LocationBase):
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)


class LocationUpdate(BaseModel):
    address: Optional[str] = Field(None, min_length=5, max_length=1000)
    google_map_link: Optional[str] = Field(None, max_length=1000)
    floor: Optional[str] = Field(None, max_length=50)
    elderly_friendly: Optional[bool] = None


class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    
    class Config:
        from_attributes = True


class LocationListResponse(BaseModel):
    id: int
    property_id: int
    address: str
    elderly_friendly: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

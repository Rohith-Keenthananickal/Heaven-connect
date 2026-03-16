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
    nearby_airport: Optional[str] = Field(None, max_length=200, description="Nearest airport name")
    distance_to_airport: Optional[str] = Field(None, max_length=50, description="Distance to airport (e.g., '25 km', '30 minutes')")
    nearest_railway_station: Optional[str] = Field(None, max_length=200, description="Nearest railway station name")
    distance_to_railway_station: Optional[str] = Field(None, max_length=50, description="Distance to railway station (e.g., '10 km', '15 minutes')")
    nearest_bus_stand: Optional[str] = Field(None, max_length=200, description="Nearest bus stand name")
    distance_to_bus_stand: Optional[str] = Field(None, max_length=50, description="Distance to bus stand (e.g., '2 km', '5 minutes')")


class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
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

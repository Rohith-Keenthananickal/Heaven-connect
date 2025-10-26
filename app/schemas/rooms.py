from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from app.models.property import BedType, RoomView


class RoomBase(BaseModel):
    property_id: int
    room_type: str = Field(..., min_length=1, max_length=100)
    count: int = Field(..., ge=1, le=50)
    max_occupancy: int = Field(..., ge=1, le=20, description="Maximum number of guests that can occupy this room")
    bed_type: BedType = Field(..., description="Type of bed in the room")
    view: RoomView = Field(..., description="View from the room")
    amenities: Optional[List[Any]] = []


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_type: Optional[str] = Field(None, min_length=1, max_length=100)
    count: Optional[int] = Field(None, ge=1, le=50)
    max_occupancy: Optional[int] = Field(None, ge=1, le=20, description="Maximum number of guests that can occupy this room")
    bed_type: Optional[BedType] = Field(None, description="Type of bed in the room")
    view: Optional[RoomView] = Field(None, description="View from the room")
    amenities: Optional[List[Any]] = None


class RoomResponse(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    id: int
    property_id: int
    room_type: str
    count: int
    max_occupancy: int
    bed_type: BedType
    view: RoomView
    created_at: datetime
    
    class Config:
        from_attributes = True

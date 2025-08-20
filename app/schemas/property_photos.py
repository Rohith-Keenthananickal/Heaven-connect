from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.property import PhotoCategory


class PropertyPhotoBase(BaseModel):
    property_id: int
    category: PhotoCategory
    image_url: str = Field(..., min_length=1, max_length=500)


class PropertyPhotoCreate(PropertyPhotoBase):
    pass


class PropertyPhotoUpdate(BaseModel):
    category: Optional[PhotoCategory] = None
    image_url: Optional[str] = Field(None, min_length=1, max_length=500)


class PropertyPhotoResponse(PropertyPhotoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PropertyPhotoListResponse(BaseModel):
    id: int
    property_id: int
    category: PhotoCategory
    image_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True

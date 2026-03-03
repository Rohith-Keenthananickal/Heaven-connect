from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.property import FacilityMasterType, FacilityMasterStatus
from app.schemas.base import BaseResponse


class FacilityMasterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Display name of the facility")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the facility")
    type: FacilityMasterType = Field(..., description="PROPERTY or ROOM")
    status: FacilityMasterStatus = Field(
        FacilityMasterStatus.ACTIVE,
        description="ACTIVE, BLOCKED, or DELETED",
    )


class FacilityMasterCreate(FacilityMasterBase):
    pass


class FacilityMasterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Display name of the facility")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the facility")
    type: Optional[FacilityMasterType] = None
    status: Optional[FacilityMasterStatus] = None


class FacilityMasterResponse(FacilityMasterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacilityMasterListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    type: FacilityMasterType
    status: FacilityMasterStatus
    created_at: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.property import FacilityCategory
from app.schemas.facility_master import FacilityMasterListResponse


class FacilityBase(BaseModel):
    facility_master_ids: List[int] = Field(..., description="Array of facility master IDs (name, description, type)", min_length=1)
    property_id: Optional[int] = Field(None, description="Optional property ID for property-specific facilities")
    category: FacilityCategory
    is_common: bool = Field(False, description="Whether this is a common facility available to all properties")


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    facility_master_ids: Optional[List[int]] = Field(None, description="Array of facility master IDs", min_length=1)
    property_id: Optional[int] = Field(None, description="Optional property ID for property-specific facilities")
    category: Optional[FacilityCategory] = None
    is_common: Optional[bool] = Field(None, description="Whether this is a common facility available to all properties")


class FacilityResponse(BaseModel):
    id: int
    facility_master_ids: List[int] = Field(default_factory=list, description="Array of facility master IDs")
    facility_masters: List[FacilityMasterListResponse] = Field(default_factory=list, description="Populated master data (name, description, type, status)")
    property_id: Optional[int]
    category: FacilityCategory
    is_common: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacilityListResponse(BaseModel):
    id: int
    facility_master_ids: List[int] = Field(default_factory=list, description="Array of facility master IDs")
    facility_masters: List[FacilityMasterListResponse] = Field(default_factory=list, description="Populated master data")
    property_id: Optional[int]
    category: FacilityCategory
    is_common: bool
    created_at: datetime

    class Config:
        from_attributes = True


def facility_to_response(db_facility) -> FacilityResponse:
    """Build FacilityResponse from ORM with facility_masters populated."""
    masters = []
    master_ids = []
    
    # Get facility_masters from many-to-many relationship
    if hasattr(db_facility, "facility_masters") and db_facility.facility_masters:
        masters = [FacilityMasterListResponse.model_validate(fm) for fm in db_facility.facility_masters]
        master_ids = [fm.id for fm in db_facility.facility_masters]
    # Fallback to old facility_master for backward compatibility during migration
    elif getattr(db_facility, "facility_master", None) is not None:
        masters = [FacilityMasterListResponse.model_validate(db_facility.facility_master)]
        master_ids = [db_facility.facility_master.id]
    
    return FacilityResponse(
        id=db_facility.id,
        facility_master_ids=master_ids,
        facility_masters=masters,
        property_id=db_facility.property_id,
        category=db_facility.category,
        is_common=db_facility.is_common,
        created_at=db_facility.created_at,
        updated_at=db_facility.updated_at,
    )


def facility_to_list_response(db_facility) -> FacilityListResponse:
    """Build FacilityListResponse from ORM with facility_masters populated."""
    masters = []
    master_ids = []
    
    # Get facility_masters from many-to-many relationship
    if hasattr(db_facility, "facility_masters") and db_facility.facility_masters:
        masters = [FacilityMasterListResponse.model_validate(fm) for fm in db_facility.facility_masters]
        master_ids = [fm.id for fm in db_facility.facility_masters]
    # Fallback to old facility_master for backward compatibility during migration
    elif getattr(db_facility, "facility_master", None) is not None:
        masters = [FacilityMasterListResponse.model_validate(db_facility.facility_master)]
        master_ids = [db_facility.facility_master.id]
    
    return FacilityListResponse(
        id=db_facility.id,
        facility_master_ids=master_ids,
        facility_masters=masters,
        property_id=db_facility.property_id,
        category=db_facility.category,
        is_common=db_facility.is_common,
        created_at=db_facility.created_at,
    )

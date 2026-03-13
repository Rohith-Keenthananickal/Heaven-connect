from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.property import FacilityCategory
from app.schemas.facility_master import FacilityMasterListResponse


class FacilityBase(BaseModel):
    facility_master_id: int = Field(..., description="ID of the facility master (name, description, type)")
    property_id: Optional[int] = Field(None, description="Optional property ID for property-specific facilities")
    category: FacilityCategory
    is_common: bool = Field(False, description="Whether this is a common facility available to all properties")


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    facility_master_id: Optional[int] = Field(None, description="ID of the facility master")
    property_id: Optional[int] = Field(None, description="Optional property ID for property-specific facilities")
    category: Optional[FacilityCategory] = None
    is_common: Optional[bool] = Field(None, description="Whether this is a common facility available to all properties")


class FacilityResponse(BaseModel):
    id: int
    facility_master_id: Optional[int]
    facility_master: Optional[FacilityMasterListResponse] = Field(None, description="Populated master data (name, description, type, status)")
    property_id: Optional[int]
    category: FacilityCategory
    is_common: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FacilityListResponse(BaseModel):
    id: int
    facility_master_id: Optional[int]
    facility_master: Optional[FacilityMasterListResponse] = Field(None, description="Populated master data")
    property_id: Optional[int]
    category: FacilityCategory
    is_common: bool
    created_at: datetime

    class Config:
        from_attributes = True


def facility_to_response(db_facility) -> FacilityResponse:
    """Build FacilityResponse from ORM with facility_master populated."""
    master = None
    if getattr(db_facility, "facility_master", None) is not None:
        master = FacilityMasterListResponse.model_validate(db_facility.facility_master)
    return FacilityResponse(
        id=db_facility.id,
        facility_master_id=db_facility.facility_master_id,
        facility_master=master,
        property_id=db_facility.property_id,
        category=db_facility.category,
        is_common=db_facility.is_common,
        created_at=db_facility.created_at,
        updated_at=db_facility.updated_at,
    )


def facility_to_list_response(db_facility) -> FacilityListResponse:
    """Build FacilityListResponse from ORM with facility_master populated."""
    master = None
    if getattr(db_facility, "facility_master", None) is not None:
        master = FacilityMasterListResponse.model_validate(db_facility.facility_master)
    return FacilityListResponse(
        id=db_facility.id,
        facility_master_id=db_facility.facility_master_id,
        facility_master=master,
        property_id=db_facility.property_id,
        category=db_facility.category,
        is_common=db_facility.is_common,
        created_at=db_facility.created_at,
    )

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class PropertyAgreementBase(BaseModel):
    property_id: int
    owns_property: bool
    agreed_to_rules: bool
    allow_verification: bool
    payout_after_checkout: bool


class PropertyAgreementCreate(PropertyAgreementBase):
    @field_validator('owns_property', 'agreed_to_rules', 'allow_verification', 'payout_after_checkout')
    @classmethod
    def must_be_true(cls, v):
        if not v:
            raise ValueError('All agreements must be accepted (set to True)')
        return v


class PropertyAgreementUpdate(BaseModel):
    owns_property: Optional[bool] = None
    agreed_to_rules: Optional[bool] = None
    allow_verification: Optional[bool] = None
    payout_after_checkout: Optional[bool] = None


class PropertyAgreementResponse(PropertyAgreementBase):
    id: int
    signed_at: datetime
    
    class Config:
        from_attributes = True


class PropertyAgreementListResponse(BaseModel):
    id: int
    property_id: int
    owns_property: bool
    agreed_to_rules: bool
    allow_verification: bool
    payout_after_checkout: bool
    signed_at: datetime
    
    class Config:
        from_attributes = True 
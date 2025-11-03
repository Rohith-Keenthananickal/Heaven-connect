from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from app.models.enquiry import Gender, IDCardType, EnquiryStatus
from app.schemas.base import PaginatedResponse, PaginationInfo


# Base Enquiry Schema
class EnquiryBase(BaseModel):
    company_name: Optional[str] = None
    host_name: str
    email: Optional[EmailStr] = None
    phone_number: str
    alternate_phone_number: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    id_card_type: Optional[IDCardType] = None
    id_card_number: Optional[str] = None
    atp_id: Optional[str] = None
    
    @validator('phone_number', 'alternate_phone_number')
    def validate_phone(cls, v):
        if v is not None and (not v.isdigit() or len(v) < 8 or len(v) > 15):
            raise ValueError('Phone number must be between 8 and 15 digits')
        return v


# Schema for creating a new enquiry
class EnquiryCreate(EnquiryBase):
    pass


# Schema for updating an enquiry
class EnquiryUpdate(BaseModel):
    company_name: Optional[str] = None
    host_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    alternate_phone_number: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    id_card_type: Optional[IDCardType] = None
    id_card_number: Optional[str] = None
    atp_id: Optional[str] = None
    status: Optional[EnquiryStatus] = None
    remarks: Optional[str] = None
    
    @validator('phone_number', 'alternate_phone_number')
    def validate_phone(cls, v):
        if v is not None and (not v.isdigit() or len(v) < 8 or len(v) > 15):
            raise ValueError('Phone number must be between 8 and 15 digits')
        return v


# Schema for returning an enquiry
class EnquiryResponse(EnquiryBase):
    id: int
    status: EnquiryStatus
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True


# Schema for updating status of an enquiry
class EnquiryStatusUpdate(BaseModel):
    status: EnquiryStatus
    remarks: Optional[str] = None


# Schema for search params
class EnquirySearchRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    status: Optional[EnquiryStatus] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    host_name: Optional[str] = None
    company_name: Optional[str] = None
    id_card_number: Optional[str] = None
    atp_id: Optional[str] = None


# Schema for search response
class EnquirySearchResponse(BaseModel):
    status: str = "success"
    data: List[EnquiryResponse]
    pagination: PaginationInfo


# API Response Models
class EnquiryCreateAPIResponse(BaseModel):
    """Response schema for enquiry creation"""
    status: str = "success"
    data: EnquiryResponse
    message: str = "Enquiry created successfully"


class EnquiryListAPIResponse(BaseModel):
    """Response schema for enquiry list endpoints"""
    status: str = "success"
    data: List[EnquiryResponse]
    message: str = "Enquiries retrieved successfully"


class EnquiryGetAPIResponse(BaseModel):
    """Response schema for single enquiry retrieval"""
    status: str = "success"
    data: EnquiryResponse
    message: str = "Enquiry retrieved successfully"


class EnquiryUpdateAPIResponse(BaseModel):
    """Response schema for enquiry updates"""
    status: str = "success"
    data: EnquiryResponse
    message: str = "Enquiry updated successfully"


class EnquiryDeleteAPIResponse(BaseModel):
    """Response schema for enquiry deletion"""
    status: str = "success"
    data: Dict[str, Any]
    message: str = "Enquiry deleted successfully"


class EnquiryStatusUpdateAPIResponse(BaseModel):
    """Response schema for enquiry status updates"""
    class EnquiryStatusData(BaseModel):
        enquiry: EnquiryResponse
        new_status: EnquiryStatus
        
        class Config:
            from_attributes = True
    
    status: str = "success"
    data: EnquiryStatusData
    message: str

from sqlalchemy import Integer, String, DateTime, Date, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base
import enum

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class IDCardType(str, enum.Enum):
    AADHAR = "AADHAR"
    PAN = "PAN"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    VOTER_ID = "VOTER_ID"
    PASSPORT = "PASSPORT"
    OTHER = "OTHER"

class EnquiryStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    REJECTED = "REJECTED"
    CONVERTED = "CONVERTED"  # Converted to a registration/user

class Enquiry(Base):
    __tablename__ = "enquiries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    host_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    alternate_phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    dob: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender), nullable=True)
    id_card_type: Mapped[Optional[IDCardType]] = mapped_column(Enum(IDCardType), nullable=True)
    id_card_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    atp_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True, index=True)
    
    # Status tracking
    status: Mapped[EnquiryStatus] = mapped_column(
        Enum(EnquiryStatus), 
        default=EnquiryStatus.PENDING, 
        nullable=False,
        index=True
    )
    
    # Notes and remarks
    remarks: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

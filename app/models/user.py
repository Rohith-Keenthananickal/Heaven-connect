from sqlalchemy import Integer, String, DateTime, Boolean, Date, Enum, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base
import enum

from app.models.property import Property
from app.models.location import District, GramaPanchayat, Corporation, Municipality


class AuthProvider(str, enum.Enum):
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"
    MOBILE = "MOBILE"


class UserType(str, enum.Enum):
    ADMIN = "ADMIN"
    GUEST = "GUEST"
    HOST = "HOST"
    AREA_COORDINATOR = "AREA_COORDINATOR"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    auth_provider: Mapped[AuthProvider] = mapped_column(Enum(AuthProvider), nullable=False)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), default=UserType.GUEST, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(5), nullable=True, comment="Country code like +91, +1, etc.")
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    dob: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    profile_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property_profile: Mapped[Optional["Property"]] = relationship("Property", foreign_keys="Property.user_id", back_populates="user", uselist=False)
    coordinated_properties: Mapped[list["Property"]] = relationship("Property", foreign_keys="Property.area_coordinator_id", back_populates="area_coordinator")
    
    # Type-specific profile relationships
    guest_profile: Mapped[Optional["Guest"]] = relationship("Guest", back_populates="user", uselist=False)
    host_profile: Mapped[Optional["Host"]] = relationship("Host", back_populates="user", uselist=False)
    area_coordinator_profile: Mapped[Optional["AreaCoordinator"]] = relationship(
        "AreaCoordinator", 
        back_populates="user", 
        uselist=False,
        foreign_keys="AreaCoordinator.id"
    )
    
    # Issue relationships
    created_issues: Mapped[list["Issue"]] = relationship("Issue", foreign_keys="Issue.created_by_id", back_populates="created_by")
    assigned_issues: Mapped[list["Issue"]] = relationship("Issue", foreign_keys="Issue.assigned_to_id", back_populates="assigned_to")


class Guest(Base):
    __tablename__ = "guests"
    
    # Primary key is also foreign key to users table
    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    
    # Guest-specific fields
    passport_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="guest_profile")


class Host(Base):
    __tablename__ = "hosts"
    
    # Primary key is also foreign key to users table
    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    
    # Host-specific fields
    id_proof_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Aadhar, PAN, Driving License, etc.")
    id_proof_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    id_proof_images: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="Array of URLs to ID proof images")
    experience_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="host_profile")


class AreaCoordinator(Base):
    __tablename__ = "area_coordinators"
    
    # Primary key is also foreign key to users table
    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    
    # Basic Area Coordinator fields
    atp_uuid: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True, index=True, comment="ATP UUID in format ATP-01234")
    application_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True, comment="Application number for the coordinator")
    region: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    assigned_properties: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    
    # Approval status
    approval_status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, index=True)
    approval_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, comment="Admin user ID who approved/rejected")
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Reason for rejection if applicable")
    
    # ID Proof and Verification fields
    id_proof_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Aadhar, PAN, Driving License, etc.")
    id_proof_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    pancard_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    
    # Photo and Document fields
    passport_size_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="URL to passport size photo")
    id_proof_document: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="Array of URLs to ID proof documents")
    pancard_images: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="Array of URLs to PAN card images")
    address_proof_document: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="URL to address proof document")
    
    # Address fields
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    panchayat: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    address_line1: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Location coordinates
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Business information
    business_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="Business name of the area coordinator")
    
    # Local body information - connected to existing location tables
    local_body_district_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("districts.id"), nullable=True, comment="Reference to districts table")
    local_body_grama_panchayat_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("grama_panchayats.id"), nullable=True, comment="Reference to grama_panchayats table")
    local_body_corporation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("corporations.id"), nullable=True, comment="Reference to corporations table")
    local_body_municipality_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("municipalities.id"), nullable=True, comment="Reference to municipalities table")
    local_body_ward: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Local body ward")
    
    # Additional fields
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="area_coordinator_profile", foreign_keys=[id])
    bank_details: Mapped[Optional["BankDetails"]] = relationship("BankDetails", back_populates="area_coordinator", uselist=False)
    admin_approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    
    # Local body relationships
    local_body_district: Mapped[Optional["District"]] = relationship("District", foreign_keys=[local_body_district_id])
    local_body_grama_panchayat: Mapped[Optional["GramaPanchayat"]] = relationship("GramaPanchayat", foreign_keys=[local_body_grama_panchayat_id])
    local_body_corporation: Mapped[Optional["Corporation"]] = relationship("Corporation", foreign_keys=[local_body_corporation_id])
    local_body_municipality: Mapped[Optional["Municipality"]] = relationship("Municipality", foreign_keys=[local_body_municipality_id])


class BankDetails(Base):
    __tablename__ = "bank_details"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign key to area coordinator
    area_coordinator_id: Mapped[int] = mapped_column(Integer, ForeignKey("area_coordinators.id"), nullable=False, unique=True)
    
    # Bank account details
    bank_name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_holder_name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ifsc_code: Mapped[str] = mapped_column(String(20), nullable=False)
    branch_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    branch_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Account type and status
    account_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Savings, Current, etc.")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Document proof
    bank_passbook_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="URL to bank passbook image")
    cancelled_cheque_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="URL to cancelled cheque image")
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship back to Area Coordinator
    area_coordinator: Mapped["AreaCoordinator"] = relationship("AreaCoordinator", back_populates="bank_details")


class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    otp: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

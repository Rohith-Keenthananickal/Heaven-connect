from sqlalchemy import Integer, String, DateTime, Boolean, Date, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Optional, Any, Dict, List
import enum


class PropertyClassification(str, enum.Enum):
    SILVER = "SILVER"
    GOLD = "GOLD" 
    DIAMOND = "DIAMOND"


class PropertyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"


class FacilityCategory(str, enum.Enum):
    GENERAL = "GENERAL"
    BEDROOM = "BEDROOM"
    BATHROOM = "BATHROOM"
    DINING = "DINING"


class PhotoCategory(str, enum.Enum):
    EXTERIOR = "EXTERIOR"
    BEDROOM = "BEDROOM"
    BATHROOM = "BATHROOM"
    LIVING_ROOM = "LIVING_ROOM"
    KITCHEN = "KITCHEN"
    DINING = "DINING"
    COMMON_AREA = "COMMON_AREA"
    AMENITIES = "AMENITIES"


class PropertyType(Base):
    __tablename__ = "property_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    properties: Mapped[List["Property"]] = relationship("Property", back_populates="property_type")


class Property(Base):
    __tablename__ = "properties"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    property_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    alternate_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    area_coordinator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    property_type_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("property_types.id"), nullable=True)
    id_proof_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    id_proof_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    certificate_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    trade_license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    classification: Mapped[PropertyClassification] = mapped_column(Enum(PropertyClassification), default=PropertyClassification.SILVER)
    status: Mapped[PropertyStatus] = mapped_column(Enum(PropertyStatus), default=PropertyStatus.ACTIVE)
    progress_step: Mapped[int] = mapped_column(Integer, default=1)  # Current onboarding step (1-9)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="property_profile")
    area_coordinator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[area_coordinator_id], back_populates="coordinated_properties")
    property_type: Mapped[Optional["PropertyType"]] = relationship("PropertyType", back_populates="properties")
    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="property", cascade="all, delete-orphan")
    facilities: Mapped[List["Facility"]] = relationship("Facility", back_populates="property", cascade="all, delete-orphan")
    property_photos: Mapped[List["PropertyPhoto"]] = relationship("PropertyPhoto", back_populates="property", cascade="all, delete-orphan")
    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="property", uselist=False, cascade="all, delete-orphan")
    availability: Mapped[List["Availability"]] = relationship("Availability", back_populates="property", cascade="all, delete-orphan")
    agreements: Mapped[Optional["PropertyAgreement"]] = relationship("PropertyAgreement", back_populates="property", uselist=False, cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("properties.id"), nullable=False)
    room_type: Mapped[str] = mapped_column(String(100), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    amenities: Mapped[Optional[List[Any]]] = mapped_column(JSON, nullable=True)  # Store as JSON array
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="rooms")


class Facility(Base):
    __tablename__ = "facilities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("properties.id"), nullable=False)
    category: Mapped[FacilityCategory] = mapped_column(Enum(FacilityCategory), nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)  # Store facility details as JSON
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="facilities")


class PropertyPhoto(Base):
    __tablename__ = "property_photos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("properties.id"), nullable=False)
    category: Mapped[PhotoCategory] = mapped_column(Enum(PhotoCategory), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="property_photos")


class Location(Base):
    __tablename__ = "location"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("properties.id"), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(1000), nullable=False)
    google_map_link: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    elderly_friendly: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="location")


class Availability(Base):
    __tablename__ = "availability"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("properties.id"), nullable=False)
    available_from: Mapped[Date] = mapped_column(Date, nullable=False)
    available_to: Mapped[Date] = mapped_column(Date, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="availability")


class PropertyAgreement(Base):
    __tablename__ = "property_agreements"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("properties.id"), unique=True, nullable=False)
    owns_property: Mapped[bool] = mapped_column(Boolean, nullable=False)
    agreed_to_rules: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allow_verification: Mapped[bool] = mapped_column(Boolean, nullable=False)
    payout_after_checkout: Mapped[bool] = mapped_column(Boolean, nullable=False)
    signed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="agreements") 
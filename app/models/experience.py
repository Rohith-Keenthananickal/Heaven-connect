from sqlalchemy import Integer, String, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Optional, List, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from app.models.user import User


class DurationUnit(str, enum.Enum):
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"


class ExperienceStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"


class ExperienceApprovalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Experience(Base):
    __tablename__ = "experiences"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    area_coordinator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Basic information
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Duration information
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Duration value")
    duration_unit: Mapped[Optional[DurationUnit]] = mapped_column(Enum(DurationUnit), nullable=True, comment="Duration unit: MINUTE, HOUR, or DAY")
    
    # Group and language information
    group_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Maximum group size")
    languages: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, comment="Array of language codes or names")
    
    # Description and content
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True, comment="Detailed description of the experience")
    included: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, comment="Array of items included in the experience")
    photos: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, comment="Array of photo URLs")
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="URL to video content")
    safety_items: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, comment="Array of safety items or guidelines")
    
    # Pricing information
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="Price of the experience")
    is_price_by_guest: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Whether price is per guest (True) or per group (False)")
    included_in_price: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, comment="Array of items included in the price")
    
    # Legal and compliance
    legal_declarations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, comment="Array of legal declarations or disclaimers")
    
    # Status fields
    status: Mapped[ExperienceStatus] = mapped_column(Enum(ExperienceStatus), default=ExperienceStatus.ACTIVE, nullable=False, index=True)
    approval_status: Mapped[ExperienceApprovalStatus] = mapped_column(Enum(ExperienceApprovalStatus), default=ExperienceApprovalStatus.DRAFT, nullable=False, index=True, comment="Approval status: DRAFT, PENDING, APPROVED, REJECTED")
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="experiences")
    area_coordinator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[area_coordinator_id], back_populates="coordinated_experiences")

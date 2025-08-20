from sqlalchemy import Integer, String, DateTime, Boolean, Date, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Optional
import enum


class AuthProvider(str, enum.Enum):
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"
    MOBILE = "MOBILE"


class UserType(str, enum.Enum):
    ADMIN = "ADMIN"
    GUEST = "GUEST"
    HOST = "HOST"


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    auth_provider: Mapped[AuthProvider] = mapped_column(Enum(AuthProvider), nullable=False)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), default=UserType.GUEST, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    dob: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    profile_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property_profile: Mapped[Optional["Property"]] = relationship("Property", foreign_keys="Property.user_id", back_populates="user", uselist=False)
    coordinated_properties: Mapped[list["Property"]] = relationship("Property", foreign_keys="Property.area_coordinator_id", back_populates="area_coordinator")


class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    otp: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

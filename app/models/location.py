from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Optional, List


class District(Base):
    __tablename__ = "districts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    grama_panchayats: Mapped[List["GramaPanchayat"]] = relationship("GramaPanchayat", back_populates="district", cascade="all, delete-orphan")


class GramaPanchayat(Base):
    __tablename__ = "grama_panchayats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area_sq_km: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    district: Mapped["District"] = relationship("District", back_populates="grama_panchayats")

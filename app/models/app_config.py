from sqlalchemy import Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from typing import Optional, Dict, Any


class AppConfig(Base):
    __tablename__ = "app_configs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, default="default", comment="Config name identifier")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True, comment="Whether this config is currently active")
    
    # Store the entire config as JSON
    config_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, comment="Complete app configuration JSON")
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="User ID who created this config")
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="User ID who last updated this config")

from sqlalchemy import Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Optional, List
import enum


class ContentType(str, enum.Enum):
    TEXT = "TEXT"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    QUIZ = "QUIZ"


class TrainingStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TrainingModule(Base):
    __tablename__ = "training_modules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    module_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="Order of module in sequence")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Estimated time to complete in minutes")
    
    # Metadata
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="Admin who created this module")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    contents: Mapped[List["TrainingContent"]] = relationship("TrainingContent", back_populates="module", cascade="all, delete-orphan", order_by="TrainingContent.content_order")
    progress_records: Mapped[List["TrainingProgress"]] = relationship("TrainingProgress", back_populates="module", cascade="all, delete-orphan")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])


class TrainingContent(Base):
    __tablename__ = "training_contents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_modules.id"), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Text content or video/document URL")
    content_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="Order within the module")
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Whether this content is required to complete the module")
    
    # For video content
    video_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Duration in seconds for video content")
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Thumbnail URL for video content")
    
    # For quiz content
    quiz_questions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="Quiz questions and answers in JSON format")
    passing_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Minimum score required to pass (percentage)")
    
    # Metadata
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    module: Mapped["TrainingModule"] = relationship("TrainingModule", back_populates="contents")
    progress_records: Mapped[List["TrainingProgress"]] = relationship("TrainingProgress", back_populates="content", cascade="all, delete-orphan")


class TrainingProgress(Base):
    __tablename__ = "training_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="Area Coordinator user ID")
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_modules.id"), nullable=False)
    content_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("training_contents.id"), nullable=True, comment="Specific content progress (optional)")
    
    # Progress tracking
    status: Mapped[TrainingStatus] = mapped_column(Enum(TrainingStatus), default=TrainingStatus.NOT_STARTED, nullable=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Progress percentage (0-100)")
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Time spent in seconds")
    
    # For quiz content
    quiz_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Quiz score (percentage)")
    quiz_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Number of quiz attempts")
    
    # Completion tracking
    started_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_accessed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    module: Mapped["TrainingModule"] = relationship("TrainingModule", back_populates="progress_records")
    content: Mapped[Optional["TrainingContent"]] = relationship("TrainingContent", back_populates="progress_records")

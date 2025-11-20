from sqlalchemy import Integer, String, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from app.database import Base
import enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.property import Property


class IssueType(str, enum.Enum):
    COMPLAINT = "COMPLAINT"
    SUPPORT = "SUPPORT"


class IssueStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class IssueStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"


class Priority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class EscalationLevel(str, enum.Enum):
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"


class ActivityType(str, enum.Enum):
    CREATED = "CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    ASSIGNED = "ASSIGNED"
    UPDATED = "UPDATED"
    COMMENT_ADDED = "COMMENT_ADDED"
    ESCALATED = "ESCALATED"
    ATTACHMENT_ADDED = "ATTACHMENT_ADDED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"


class Issue(Base):
    __tablename__ = "issues"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    issue: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[IssueType] = mapped_column(Enum(IssueType), nullable=False, index=True)
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus), 
        default=IssueStatus.ACTIVE, 
        nullable=False,
        index=True
    )
    issue_status: Mapped[IssueStatusEnum] = mapped_column(
        Enum(IssueStatusEnum), 
        default=IssueStatusEnum.OPEN, 
        nullable=False,
        index=True
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority), 
        default=Priority.MEDIUM, 
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    property_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    attachments: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, default=list)
    created_on: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id], back_populates="created_issues")
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_issues")
    property: Mapped[Optional["Property"]] = relationship("Property", back_populates="issues")
    activities: Mapped[List["IssueActivity"]] = relationship("IssueActivity", back_populates="issue", cascade="all, delete-orphan")
    escalations: Mapped[List["IssueEscalation"]] = relationship("IssueEscalation", back_populates="issue", cascade="all, delete-orphan")


class IssueActivity(Base):
    __tablename__ = "issue_activities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type: Mapped[ActivityType] = mapped_column(Enum(ActivityType), nullable=False, index=True)
    performed_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    old_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activity_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    issue: Mapped["Issue"] = relationship("Issue", back_populates="activities")
    performed_by: Mapped["User"] = relationship("User", foreign_keys=[performed_by_id])


class IssueEscalation(Base):
    __tablename__ = "issue_escalations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    escalation_level: Mapped[EscalationLevel] = mapped_column(Enum(EscalationLevel), nullable=False, index=True)
    escalated_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    escalated_to_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    resolved_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    issue: Mapped["Issue"] = relationship("Issue", back_populates="escalations")
    escalated_by: Mapped["User"] = relationship("User", foreign_keys=[escalated_by_id])
    escalated_to: Mapped["User"] = relationship("User", foreign_keys=[escalated_to_id])
    resolved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[resolved_by_id])


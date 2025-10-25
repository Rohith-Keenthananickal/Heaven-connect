from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class EmailStatus(str, enum.Enum):
    """Email status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class EmailType(str, enum.Enum):
    """Email type enumeration"""
    FORGOT_PASSWORD = "forgot_password"
    LOGIN_OTP = "login_otp"
    WELCOME = "welcome"
    VERIFICATION = "verification"
    NOTIFICATION = "notification"
    MARKETING = "marketing"


class EmailTemplate(Base):
    """Email template model for storing email templates"""
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    email_type = Column(Enum(EmailType), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True)  # User ID who created the template


class EmailLog(Base):
    """Email log model for tracking sent emails"""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_name = Column(String(100), nullable=True)
    subject = Column(String(255), nullable=False)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    email_type = Column(Enum(EmailType), nullable=False)
    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING)
    template_id = Column(Integer, nullable=True)  # Reference to email template
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    external_id = Column(String(100), nullable=True)  # External service ID (Zoho)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)  # User ID who triggered the email



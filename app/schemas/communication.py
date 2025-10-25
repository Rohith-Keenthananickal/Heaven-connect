from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.communication import EmailStatus, EmailType


class EmailSendRequest(BaseModel):
    """Schema for sending email"""
    recipient_email: EmailStr
    recipient_name: Optional[str] = None
    subject: str
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    email_type: EmailType
    template_id: Optional[int] = None
    template_variables: Optional[Dict[str, Any]] = None  # For template variable substitution


class EmailSendResponse(BaseModel):
    """Schema for email send response"""
    id: int
    status: EmailStatus
    message: str


class EmailLogResponse(BaseModel):
    """Schema for email log response"""
    id: int
    recipient_email: str
    recipient_name: Optional[str] = None
    subject: str
    email_type: EmailType
    status: EmailStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class ForgotPasswordEmailRequest(BaseModel):
    """Schema for forgot password email request"""
    email: EmailStr
    reset_token: str
    user_name: Optional[str] = None


class LoginOTPEmailRequest(BaseModel):
    """Schema for login OTP email request"""
    email: EmailStr
    otp_code: str
    user_name: Optional[str] = None
    expires_in_minutes: int = 10


class WelcomeEmailRequest(BaseModel):
    """Schema for welcome email request"""
    email: EmailStr
    user_name: str
    login_url: Optional[str] = None


class EmailLogListResponse(BaseModel):
    """Schema for email log list response"""
    logs: List[EmailLogResponse]
    total: int

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request schema"""
    auth_provider: str = Field(..., description="Authentication provider: EMAIL, GOOGLE, or MOBILE")
    email: Optional[EmailStr] = Field(None, description="Email for email-based login")
    phone_number: Optional[str] = Field(None, description="Phone number for mobile-based login")
    password: Optional[str] = Field(None, description="Password for email-based login (will be safely truncated if it exceeds 72 bytes when encoded)")
    google_token: Optional[str] = Field(None, description="Google OAuth token for Google-based login")
    otp: Optional[str] = Field(None, description="OTP code for mobile-based login")


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict = Field(..., description="Complete user data including profile information")


class LoginResponse(BaseModel):
    """Login response schema"""
    status: str = "success"
    message: str = "Login successful"
    data: TokenResponse


class GoogleLoginRequest(BaseModel):
    """Google OAuth login request"""
    id_token: str = Field(..., description="Google ID token")


class MobileOTPLoginRequest(BaseModel):
    """Mobile OTP login request"""
    phone_number: str = Field(..., description="Phone number")
    otp: str = Field(..., description="OTP code")


class EmailLoginRequest(BaseModel):
    """Email-based login request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password (will be safely truncated if it exceeds 72 bytes when encoded)")

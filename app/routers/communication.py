from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.schemas.communication import (
    EmailSendRequest,
    EmailSendResponse,
    EmailLogResponse,
    EmailLogListResponse,
    ForgotPasswordEmailRequest,
    LoginOTPEmailRequest,
    WelcomeEmailRequest
)
from app.services.email_service import email_service
from app.models.communication import EmailType, EmailStatus
from app.utils.error_handler import (
    create_http_exception,
    extract_request_info
)
from app.schemas.errors import ErrorCodes

router = APIRouter(prefix="/communication", tags=["Communication"])


# Email Sending Endpoints
@router.post("/send", response_model=EmailSendResponse)
async def send_email(
    request: Request,
    email_data: EmailSendRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send email"""
    try:
        request_info = extract_request_info(request)
        
        # Use the new email service for custom emails
        success = await email_service.send_custom_email(
            db=db,
            email=email_data.recipient_email,
            subject=email_data.subject,
            body_html=email_data.body_html,
            body_text=email_data.body_text,
            user_name=email_data.recipient_name,
            email_type=email_data.email_type
        )
        
        # Create a mock email log response
        email_log = type('EmailLog', (), {
            'id': 1,
            'status': EmailStatus.SENT if success else EmailStatus.FAILED
        })()
        
        return EmailSendResponse(
            id=email_log.id,
            status=email_log.status,
            message="Email sent successfully" if email_log.status == EmailStatus.SENT else "Email failed to send"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to send email: {str(e)}",
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


@router.post("/send/forgot-password", response_model=EmailSendResponse)
async def send_forgot_password_email(
    request: Request,
    email_data: ForgotPasswordEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send forgot password email"""
    try:
        request_info = extract_request_info(request)
        
        success = await email_service.send_forgot_password_email(
            db=db,
            email=email_data.email,
            reset_token=email_data.reset_token,
            user_name=email_data.user_name
        )
        
        # Create a mock email log response
        email_log = type('EmailLog', (), {
            'id': 1,
            'status': EmailStatus.SENT if success else EmailStatus.FAILED
        })()
        
        return EmailSendResponse(
            id=email_log.id,
            status=email_log.status,
            message="Forgot password email sent successfully" if email_log.status == EmailStatus.SENT else "Email failed to send"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to send forgot password email: {str(e)}",
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


@router.post("/send/login-otp", response_model=EmailSendResponse)
async def send_login_otp_email(
    request: Request,
    email_data: LoginOTPEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send login OTP email"""
    try:
        request_info = extract_request_info(request)
        
        success = await email_service.send_login_otp_email(
            db=db,
            email=email_data.email,
            otp_code=email_data.otp_code,
            user_name=email_data.user_name,
            expires_in_minutes=email_data.expires_in_minutes
        )
        
        # Create a mock email log response
        email_log = type('EmailLog', (), {
            'id': 1,
            'status': EmailStatus.SENT if success else EmailStatus.FAILED
        })()
        
        return EmailSendResponse(
            id=email_log.id,
            status=email_log.status,
            message="Login OTP email sent successfully" if email_log.status == EmailStatus.SENT else "Email failed to send"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to send login OTP email: {str(e)}",
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


@router.post("/send/welcome", response_model=EmailSendResponse)
async def send_welcome_email(
    request: Request,
    email_data: WelcomeEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send welcome email"""
    try:
        request_info = extract_request_info(request)
        
        success = await email_service.send_welcome_email(
            db=db,
            email=email_data.email,
            user_name=email_data.user_name,
            login_url=email_data.login_url
        )
        
        # Create a mock email log response
        email_log = type('EmailLog', (), {
            'id': 1,
            'status': EmailStatus.SENT if success else EmailStatus.FAILED
        })()
        
        return EmailSendResponse(
            id=email_log.id,
            status=email_log.status,
            message="Welcome email sent successfully" if email_log.status == EmailStatus.SENT else "Email failed to send"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to send welcome email: {str(e)}",
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


# Email Log Endpoints
@router.get("/logs", response_model=EmailLogListResponse)
async def get_email_logs(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    email_type: Optional[EmailType] = Query(None),
    status: Optional[EmailStatus] = Query(None),
    recipient_email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get email logs with filters"""
    try:
        request_info = extract_request_info(request)
        
        # Since we're using the simplified email service, we'll return empty logs for now
        # In a production system, you might want to implement proper email logging
        logs = []
        
        return EmailLogListResponse(
            logs=logs,
            total=len(logs)
        )
        
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to get email logs: {str(e)}",
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


@router.get("/logs/{log_id}", response_model=EmailLogResponse)
async def get_email_log(
    request: Request,
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get email log by ID"""
    try:
        request_info = extract_request_info(request)
        
        # Since we're using the simplified email service, we'll return a mock log for now
        # In a production system, you might want to implement proper email logging
        raise create_http_exception(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Email log not found",
            error_code=ErrorCodes.RESOURCE_NOT_FOUND,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to get email log: {str(e)}",
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )
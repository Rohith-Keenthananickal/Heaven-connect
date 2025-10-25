"""
Email Service for internal use by other modules
Simple methods that other modules can call directly
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from app.models.communication import EmailLog, EmailStatus, EmailType
from app.core.config import settings
from app.services.template_loader import template_loader

logger = logging.getLogger(__name__)


class EmailService:
    """Simple email service for internal use by other modules"""
    
    def __init__(self):
        self.smtp_server = settings.ZOHO_SMTP_SERVER
        self.smtp_port = settings.ZOHO_SMTP_PORT
        self.smtp_username = settings.ZOHO_EMAIL
        self.smtp_password = settings.ZOHO_APP_PASSWORD
        self.from_email = settings.ZOHO_EMAIL
        self.from_name = settings.ZOHO_FROM_NAME

    async def send_forgot_password_email(
        self, 
        db: AsyncSession,
        email: str,
        reset_token: str,
        user_name: Optional[str] = None
    ) -> bool:
        """Send forgot password email"""
        try:
            subject = "Reset Your Password - Heaven Connect"
            
            # Load templates from files
            variables = {
                "user_name": user_name or "User",
                "reset_link": f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            }
            
            html_body = template_loader.render_template("forgot_password", variables, "html")
            text_body = template_loader.render_template("forgot_password", variables, "txt")
            
            return await self._send_email(
                db=db,
                recipient_email=email,
                recipient_name=user_name,
                subject=subject,
                body_html=html_body,
                body_text=text_body,
                email_type=EmailType.FORGOT_PASSWORD
            )
            
        except Exception as e:
            logger.error(f"Failed to send forgot password email: {str(e)}")
            return False

    async def send_login_otp_email(
        self, 
        db: AsyncSession,
        email: str,
        otp_code: str,
        user_name: Optional[str] = None,
        expires_in_minutes: int = 10
    ) -> bool:
        """Send login OTP email"""
        try:
            subject = "Your Login OTP - Heaven Connect"
            
            # Load templates from files
            variables = {
                "user_name": user_name or "User",
                "otp_code": otp_code,
                "expires_in_minutes": expires_in_minutes
            }
            
            html_body = template_loader.render_template("login_otp", variables, "html")
            text_body = template_loader.render_template("login_otp", variables, "txt")
            
            return await self._send_email(
                db=db,
                recipient_email=email,
                recipient_name=user_name,
                subject=subject,
                body_html=html_body,
                body_text=text_body,
                email_type=EmailType.LOGIN_OTP
            )
            
        except Exception as e:
            logger.error(f"Failed to send login OTP email: {str(e)}")
            return False

    async def send_welcome_email(
        self, 
        db: AsyncSession,
        email: str,
        user_name: str,
        login_url: Optional[str] = None
    ) -> bool:
        """Send welcome email"""
        try:
            subject = "Welcome to Heaven Connect!"
            
            # Load templates from files
            login_link_html = f'<div style="text-align: center; margin: 30px 0;"><a href="{login_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Login to your account</a></div>' if login_url else ""
            login_link_text = f"Login to your account: {login_url}" if login_url else ""
            
            variables = {
                "user_name": user_name,
                "login_link_html": login_link_html,
                "login_link_text": login_link_text
            }
            
            html_body = template_loader.render_template("welcome", variables, "html")
            text_body = template_loader.render_template("welcome", variables, "txt")
            
            return await self._send_email(
                db=db,
                recipient_email=email,
                recipient_name=user_name,
                subject=subject,
                body_html=html_body,
                body_text=text_body,
                email_type=EmailType.WELCOME
            )
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False

    async def send_booking_confirmation(
        self, 
        db: AsyncSession,
        email: str,
        user_name: str,
        booking_details: Dict[str, Any]
    ) -> bool:
        """Send booking confirmation email"""
        try:
            subject = "Booking Confirmation - Heaven Connect"
            
            # Load templates from files
            variables = {
                "user_name": user_name,
                "property_name": booking_details.get('property_name', 'N/A'),
                "check_in": booking_details.get('check_in', 'N/A'),
                "check_out": booking_details.get('check_out', 'N/A'),
                "guests": booking_details.get('guests', 'N/A'),
                "total_amount": booking_details.get('total_amount', 'N/A')
            }
            
            html_body = template_loader.render_template("booking_confirmation", variables, "html")
            text_body = template_loader.render_template("booking_confirmation", variables, "txt")
            
            return await self._send_email(
                db=db,
                recipient_email=email,
                recipient_name=user_name,
                subject=subject,
                body_html=html_body,
                body_text=text_body,
                email_type=EmailType.NOTIFICATION
            )
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation email: {str(e)}")
            return False

    async def send_property_approval_email(
        self, 
        db: AsyncSession,
        email: str,
        user_name: str,
        property_name: str,
        is_approved: bool
    ) -> bool:
        """Send property approval/rejection email"""
        try:
            if is_approved:
                subject = "Property Approved - Heaven Connect"
                status_text = "approved"
                message = "Congratulations! Your property has been approved and is now live on our platform."
            else:
                subject = "Property Review Update - Heaven Connect"
                status_text = "requires changes"
                message = "Your property listing requires some changes before it can be approved."
            
            # Load templates from files
            variables = {
                "user_name": user_name,
                "property_name": property_name,
                "status_text": status_text,
                "message": message
            }
            
            html_body = template_loader.render_template("property_approval", variables, "html")
            text_body = template_loader.render_template("property_approval", variables, "txt")
            
            return await self._send_email(
                db=db,
                recipient_email=email,
                recipient_name=user_name,
                subject=subject,
                body_html=html_body,
                body_text=text_body,
                email_type=EmailType.NOTIFICATION
            )
            
        except Exception as e:
            logger.error(f"Failed to send property approval email: {str(e)}")
            return False

    async def send_custom_email(
        self, 
        db: AsyncSession,
        email: str,
        subject: str,
        body_html: str,
        body_text: str,
        user_name: Optional[str] = None,
        email_type: EmailType = EmailType.NOTIFICATION
    ) -> bool:
        """Send custom email"""
        try:
            return await self._send_email(
                db=db,
                recipient_email=email,
                recipient_name=user_name,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                email_type=email_type
            )
            
        except Exception as e:
            logger.error(f"Failed to send custom email: {str(e)}")
            return False

    async def _send_email(
        self,
        db: AsyncSession,
        recipient_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        recipient_name: Optional[str] = None,
        email_type: EmailType = EmailType.NOTIFICATION
    ) -> bool:
        """Internal method to send email and log it"""
        try:
            # Create email log entry
            email_log = EmailLog(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                email_type=email_type,
                status=EmailStatus.PENDING
            )
            
            db.add(email_log)
            await db.flush()  # Flush to get the ID but don't commit yet
            await db.refresh(email_log)
            
            # Send email via SMTP
            success = await self._send_email_via_smtp(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=subject,
                body_html=body_html,
                body_text=body_text
            )
            
            # Update email log status
            if success:
                email_log.status = EmailStatus.SENT
                email_log.sent_at = datetime.utcnow()
            else:
                email_log.status = EmailStatus.FAILED
                email_log.failed_at = datetime.utcnow()
                email_log.error_message = "Failed to send email via SMTP"
            
            await db.commit()
            return success
            
        except Exception as e:
            logger.error(f"Error in _send_email: {str(e)}")
            return False

    async def _send_email_via_smtp(
        self,
        recipient_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        recipient_name: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if body_text:
                text_part = MIMEText(body_text, 'plain')
                msg.attach(text_part)
            
            if body_html:
                html_part = MIMEText(body_html, 'html')
                msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {str(e)}")
            return False


# Create service instance
email_service = EmailService()

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import logging

from app.models.communication import EmailTemplate, EmailLog, EmailStatus, EmailType
from app.schemas.communication import (
    EmailTemplateCreate, 
    EmailTemplateUpdate,
    EmailSendRequest,
    ForgotPasswordEmailRequest,
    LoginOTPEmailRequest,
    WelcomeEmailRequest
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class CommunicationService:
    """Service for handling email communications"""
    
    def __init__(self):
        self.smtp_server = settings.ZOHO_SMTP_SERVER
        self.smtp_port = settings.ZOHO_SMTP_PORT
        self.smtp_username = settings.ZOHO_EMAIL
        self.smtp_password = settings.ZOHO_APP_PASSWORD
        self.from_email = settings.ZOHO_EMAIL
        self.from_name = settings.ZOHO_FROM_NAME

    async def create_email_template(
        self, 
        db: AsyncSession, 
        template_data: EmailTemplateCreate,
        created_by: Optional[int] = None
    ) -> EmailTemplate:
        """Create a new email template"""
        try:
            # Check if template name already exists
            existing_template = await db.execute(
                select(EmailTemplate).where(EmailTemplate.name == template_data.name)
            )
            if existing_template.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Template name already exists"
                )
            
            template = EmailTemplate(
                name=template_data.name,
                subject=template_data.subject,
                body_html=template_data.body_html,
                body_text=template_data.body_text,
                email_type=template_data.email_type,
                is_active=template_data.is_active,
                created_by=created_by
            )
            
            db.add(template)
            await db.commit()
            await db.refresh(template)
            return template
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating email template: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create email template: {str(e)}"
            )

    async def get_email_template(
        self, 
        db: AsyncSession, 
        template_id: int
    ) -> Optional[EmailTemplate]:
        """Get email template by ID"""
        result = await db.execute(
            select(EmailTemplate).where(EmailTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_email_template_by_name(
        self, 
        db: AsyncSession, 
        name: str
    ) -> Optional[EmailTemplate]:
        """Get email template by name"""
        result = await db.execute(
            select(EmailTemplate).where(EmailTemplate.name == name)
        )
        return result.scalar_one_or_none()

    async def get_email_templates(
        self, 
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        email_type: Optional[EmailType] = None,
        is_active: Optional[bool] = None
    ) -> List[EmailTemplate]:
        """Get email templates with filters"""
        query = select(EmailTemplate)
        
        if email_type:
            query = query.where(EmailTemplate.email_type == email_type)
        if is_active is not None:
            query = query.where(EmailTemplate.is_active == is_active)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update_email_template(
        self, 
        db: AsyncSession, 
        template_id: int,
        template_data: EmailTemplateUpdate
    ) -> Optional[EmailTemplate]:
        """Update email template"""
        try:
            template = await self.get_email_template(db, template_id)
            if not template:
                return None
                
            update_data = template_data.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(template, field, value)
                
                await db.commit()
                await db.refresh(template)
            
            return template
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating email template: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update email template: {str(e)}"
            )

    async def delete_email_template(
        self, 
        db: AsyncSession, 
        template_id: int
    ) -> bool:
        """Delete email template"""
        try:
            template = await self.get_email_template(db, template_id)
            if not template:
                return False
                
            await db.delete(template)
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting email template: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete email template: {str(e)}"
            )

    def _substitute_template_variables(
        self, 
        template: str, 
        variables: Dict[str, Any]
    ) -> str:
        """Substitute variables in template string"""
        if not variables:
            return template
            
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return template
        except Exception as e:
            logger.error(f"Error substituting template variables: {e}")
            return template

    async def send_email(
        self, 
        db: AsyncSession,
        email_data: EmailSendRequest,
        created_by: Optional[int] = None
    ) -> EmailLog:
        """Send email and log the attempt"""
        try:
            # Create email log entry
            email_log = EmailLog(
                recipient_email=email_data.recipient_email,
                recipient_name=email_data.recipient_name,
                subject=email_data.subject,
                body_html=email_data.body_html,
                body_text=email_data.body_text,
                email_type=email_data.email_type,
                template_id=email_data.template_id,
                status=EmailStatus.PENDING,
                created_by=created_by
            )
            
            db.add(email_log)
            await db.commit()
            await db.refresh(email_log)
            
            # Send email
            success = await self._send_email_via_smtp(email_data)
            
            if success:
                email_log.status = EmailStatus.SENT
                email_log.sent_at = datetime.utcnow()
            else:
                email_log.status = EmailStatus.FAILED
                email_log.failed_at = datetime.utcnow()
                email_log.error_message = "Failed to send email via SMTP"
            
            await db.commit()
            await db.refresh(email_log)
            return email_log
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending email: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {str(e)}"
            )

    async def _send_email_via_smtp(self, email_data: EmailSendRequest) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = email_data.recipient_email
            msg['Subject'] = email_data.subject
            
            # Add text and HTML parts
            if email_data.body_text:
                text_part = MIMEText(email_data.body_text, 'plain')
                msg.attach(text_part)
            
            if email_data.body_html:
                html_part = MIMEText(email_data.body_html, 'html')
                msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {email_data.recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    async def send_forgot_password_email(
        self, 
        db: AsyncSession,
        email_data: ForgotPasswordEmailRequest,
        created_by: Optional[int] = None
    ) -> EmailLog:
        """Send forgot password email"""
        # Get or create forgot password template
        template = await self.get_email_template_by_name(db, "forgot_password")
        if not template:
            # Create default template if it doesn't exist
            template_data = EmailTemplateCreate(
                name="forgot_password",
                subject="Reset Your Password - Heaven Connect",
                body_html="""
                <html>
                <body>
                    <h2>Password Reset Request</h2>
                    <p>Hello {user_name},</p>
                    <p>You have requested to reset your password. Click the link below to reset your password:</p>
                    <p><a href="{reset_link}">Reset Password</a></p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <p>Best regards,<br>Heaven Connect Team</p>
                </body>
                </html>
                """,
                body_text="""
                Password Reset Request
                
                Hello {user_name},
                
                You have requested to reset your password. Click the link below to reset your password:
                {reset_link}
                
                This link will expire in 24 hours.
                
                If you didn't request this, please ignore this email.
                
                Best regards,
                Heaven Connect Team
                """,
                email_type=EmailType.FORGOT_PASSWORD
            )
            template = await self.create_email_template(db, template_data, created_by)
        
        # Prepare email content
        variables = {
            "user_name": email_data.user_name or "User",
            "reset_link": f"{settings.FRONTEND_URL}/reset-password?token={email_data.reset_token}"
        }
        
        subject = self._substitute_template_variables(template.subject, variables)
        body_html = self._substitute_template_variables(template.body_html, variables)
        body_text = self._substitute_template_variables(template.body_text, variables)
        
        # Send email
        email_request = EmailSendRequest(
            recipient_email=email_data.email,
            recipient_name=email_data.user_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            email_type=EmailType.FORGOT_PASSWORD,
            template_id=template.id
        )
        
        return await self.send_email(db, email_request, created_by)

    async def send_login_otp_email(
        self, 
        db: AsyncSession,
        email_data: LoginOTPEmailRequest,
        created_by: Optional[int] = None
    ) -> EmailLog:
        """Send login OTP email"""
        # Get or create login OTP template
        template = await self.get_email_template_by_name(db, "login_otp")
        if not template:
            # Create default template if it doesn't exist
            template_data = EmailTemplateCreate(
                name="login_otp",
                subject="Your Login OTP - Heaven Connect",
                body_html="""
                <html>
                <body>
                    <h2>Login OTP</h2>
                    <p>Hello {user_name},</p>
                    <p>Your login OTP is: <strong>{otp_code}</strong></p>
                    <p>This OTP will expire in {expires_in_minutes} minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <p>Best regards,<br>Heaven Connect Team</p>
                </body>
                </html>
                """,
                body_text="""
                Login OTP
                
                Hello {user_name},
                
                Your login OTP is: {otp_code}
                
                This OTP will expire in {expires_in_minutes} minutes.
                
                If you didn't request this, please ignore this email.
                
                Best regards,
                Heaven Connect Team
                """,
                email_type=EmailType.LOGIN_OTP
            )
            template = await self.create_email_template(db, template_data, created_by)
        
        # Prepare email content
        variables = {
            "user_name": email_data.user_name or "User",
            "otp_code": email_data.otp_code,
            "expires_in_minutes": email_data.expires_in_minutes
        }
        
        subject = self._substitute_template_variables(template.subject, variables)
        body_html = self._substitute_template_variables(template.body_html, variables)
        body_text = self._substitute_template_variables(template.body_text, variables)
        
        # Send email
        email_request = EmailSendRequest(
            recipient_email=email_data.email,
            recipient_name=email_data.user_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            email_type=EmailType.LOGIN_OTP,
            template_id=template.id
        )
        
        return await self.send_email(db, email_request, created_by)

    async def send_welcome_email(
        self, 
        db: AsyncSession,
        email_data: WelcomeEmailRequest,
        created_by: Optional[int] = None
    ) -> EmailLog:
        """Send welcome email"""
        # Get or create welcome template
        template = await self.get_email_template_by_name(db, "welcome")
        if not template:
            # Create default template if it doesn't exist
            template_data = EmailTemplateCreate(
                name="welcome",
                subject="Welcome to Heaven Connect!",
                body_html="""
                <html>
                <body>
                    <h2>Welcome to Heaven Connect!</h2>
                    <p>Hello {user_name},</p>
                    <p>Welcome to Heaven Connect! We're excited to have you on board.</p>
                    <p>You can now access your account and start exploring our platform.</p>
                    {login_link}
                    <p>If you have any questions, feel free to contact our support team.</p>
                    <p>Best regards,<br>Heaven Connect Team</p>
                </body>
                </html>
                """,
                body_text="""
                Welcome to Heaven Connect!
                
                Hello {user_name},
                
                Welcome to Heaven Connect! We're excited to have you on board.
                
                You can now access your account and start exploring our platform.
                {login_link}
                
                If you have any questions, feel free to contact our support team.
                
                Best regards,
                Heaven Connect Team
                """,
                email_type=EmailType.WELCOME
            )
            template = await self.create_email_template(db, template_data, created_by)
        
        # Prepare email content
        login_link_html = ""
        login_link_text = ""
        if email_data.login_url:
            login_link_html = f'<p><a href="{email_data.login_url}">Login to your account</a></p>'
            login_link_text = f"Login to your account: {email_data.login_url}"
        
        variables = {
            "user_name": email_data.user_name,
            "login_link": login_link_html if email_data.login_url else "",
            "login_link_text": login_link_text if email_data.login_url else ""
        }
        
        subject = self._substitute_template_variables(template.subject, variables)
        body_html = self._substitute_template_variables(template.body_html, variables)
        body_text = self._substitute_template_variables(template.body_text, variables)
        
        # Send email
        email_request = EmailSendRequest(
            recipient_email=email_data.email,
            recipient_name=email_data.user_name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            email_type=EmailType.WELCOME,
            template_id=template.id
        )
        
        return await self.send_email(db, email_request, created_by)

    async def get_email_logs(
        self, 
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        email_type: Optional[EmailType] = None,
        status: Optional[EmailStatus] = None,
        recipient_email: Optional[str] = None
    ) -> List[EmailLog]:
        """Get email logs with filters"""
        query = select(EmailLog)
        
        if email_type:
            query = query.where(EmailLog.email_type == email_type)
        if status:
            query = query.where(EmailLog.status == status)
        if recipient_email:
            query = query.where(EmailLog.recipient_email.ilike(f"%{recipient_email}%"))
            
        query = query.order_by(EmailLog.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_email_log(
        self, 
        db: AsyncSession, 
        log_id: int
    ) -> Optional[EmailLog]:
        """Get email log by ID"""
        result = await db.execute(
            select(EmailLog).where(EmailLog.id == log_id)
        )
        return result.scalar_one_or_none()


# Create service instance
communication_service = CommunicationService()



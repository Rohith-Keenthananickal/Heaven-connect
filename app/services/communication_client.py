import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class CommunicationClient:
    """Client for the external communication server."""

    def __init__(self) -> None:
        self.base_url = settings.COMMUNICATION_SERVER_BASE_URL.rstrip("/")
        self.timeout = settings.COMMUNICATION_TIMEOUT_SECONDS

    async def send_login_otp(
        self,
        *,
        email: str,
        otp_code: str,
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Dispatch a login/confirmation OTP through the communication server.

        Args:
            email: Recipient email address.
            otp_code: Generated OTP code.
            purpose: Reason for the OTP (confirmation, etc.).
            metadata: Optional metadata sent along with the request.
        """
        endpoint = f"{self.base_url}/api/v1/email-otp"
        payload = {
            "email": email,
            "otp_code": otp_code,
            "purpose": purpose,
            "metadata": metadata or {},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload)
            if response.is_success:
                return True

            logger.error(
                "Communication server rejected email OTP request: %s %s",
                response.status_code,
                response.text,
            )
            return False
        except httpx.HTTPError as exc:
            logger.error("Failed to contact communication server", exc_info=exc)
            return False

    async def send_password_reset_email(
        self,
        *,
        email: str,
        user_name: str,
        otp_code: str,
        expiry_minutes: int,
    ) -> bool:
        """
        Dispatch a password reset email via the communication server.

        Args:
            email: Recipient email address.
            user_name: Friendly user name shown in template.
            reset_link: Link the user should follow to reset password.
            otp_code: OTP or token embedded in the template.
            expiry_minutes: Validity window for the OTP.
        """
        endpoint = f"{self.base_url}/api/email/send"
        payload = {
            "to": [email],
            "template_type": "password_reset",
            "template_context": {
                "user_name": user_name,
                "otp_code": otp_code,
                "expiry_minutes": expiry_minutes,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload)
            if response.is_success:
                return True

            logger.error(
                "Communication server rejected password reset email: %s %s",
                response.status_code,
                response.text,
            )
            return False
        except httpx.HTTPError as exc:
            logger.error("Failed to contact communication server", exc_info=exc)
            return False


communication_client = CommunicationClient()


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

    async def send_template_email(
        self,
        *,
        email: str,
        template_type: str,
        template_context: Dict[str, Any],
    ) -> bool:
        """
        Dispatch a template-based email via the communication server.

        Args:
            email: Recipient email address.
            template_type: Email template type (e.g., "EMAIL_VERIFICATION", "WELCOME").
            template_context: Context variables for the template.
        """
        # Use the non-versioned endpoint (confirmed: /api/email/send)
        endpoints = [
            f"{self.base_url}/api/email/send",
            f"{self.base_url}/api/v1/email/send",  # Fallback to v1 if needed
        ]
        
        payload = {
            "to": [email],
            "template_type": template_type,
            "template_context": template_context,
        }

        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug(
                    "Sending template email to %s: template_type=%s, email=%s",
                    endpoint,
                    template_type,
                    email
                )
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(endpoint, json=payload)
                
                if response.is_success:
                    logger.info(
                        "Successfully sent template email (%s) to %s via %s",
                        template_type,
                        email,
                        endpoint
                    )
                    return True

                # If 404, try next endpoint; otherwise log and return
                if response.status_code == 404 and endpoint != endpoints[-1]:
                    logger.debug(
                        "Endpoint %s returned 404, trying next endpoint",
                        endpoint
                    )
                    continue

                # Log detailed error information
                try:
                    error_response = response.json()
                    error_message = error_response.get("message", response.text)
                    error_details = error_response.get("details", None)
                except Exception:
                    error_message = response.text
                    error_details = None

                logger.error(
                    "Communication server rejected template email (%s) at %s: status=%s, message=%s, details=%s, payload=%s",
                    template_type,
                    endpoint,
                    response.status_code,
                    error_message,
                    error_details,
                    payload,
                )
                last_error = f"{response.status_code}: {error_message}"
                
            except httpx.TimeoutException as exc:
                logger.warning(
                    "Timeout contacting communication server at %s: %s",
                    endpoint,
                    str(exc)
                )
                last_error = f"Timeout: {str(exc)}"
                if endpoint == endpoints[-1]:
                    break
                continue
            except httpx.HTTPError as exc:
                logger.warning(
                    "Failed to contact communication server at %s: %s",
                    endpoint,
                    str(exc)
                )
                last_error = str(exc)
                if endpoint == endpoints[-1]:
                    logger.error(
                        "All endpoints failed for template email (%s) to %s. Last error: %s",
                        template_type,
                        email,
                        last_error,
                        exc_info=exc
                    )
                continue
        
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
        return await self.send_template_email(
            email=email,
            template_type="PASSWORD_RESET",
            template_context={
                "user_name": user_name,
                "otp_code": otp_code,
                "expiry_minutes": expiry_minutes,
            },
        )


communication_client = CommunicationClient()


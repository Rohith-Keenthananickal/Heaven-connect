from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
import json
from app.database import get_db
from app.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    TokenResponse,
    EmailLoginRequest,
    MobileOTPLoginRequest,
    GoogleLoginRequest
)
from pydantic import BaseModel, EmailStr
from app.services.users_service import users_service
from app.utils.auth import create_access_token
from app.utils.error_handler import (
    create_http_exception,
    create_authentication_http_exception,
    extract_request_info
)
from app.models.user import AuthProvider, UserStatus
from app.schemas.errors import ErrorCodes, ErrorMessages
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Email OTP Schemas
class EmailOTPRequest(BaseModel):
    """Request schema for sending email OTP"""
    email: EmailStr


class EmailOTPVerifyRequest(BaseModel):
    """Request schema for verifying email OTP"""
    email: EmailStr
    otp_code: str


class EmailOTPResponse(BaseModel):
    """Response schema for email OTP operations"""
    message: str
    email: str
    expires_in_minutes: int


class EmailOTPLoginResponse(BaseModel):
    """Response schema for email OTP login"""
    status: str = "success"
    data: TokenResponse
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user with different authentication methods"""
    try:
        user = None
        request_info = extract_request_info(request)
        
        if login_data.auth_provider == AuthProvider.EMAIL:
            if not login_data.email or not login_data.password:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Email and password are required for email authentication",
                    error_code=ErrorCodes.BAD_REQUEST,
                    path=request_info["path"],
                    method=request_info["method"],
                    trace_id=request_info["trace_id"]
                )
            user = await users_service.authenticate_user(
                db, 
                AuthProvider.EMAIL, 
                login_data.email, 
                login_data.password
            )
            
        elif login_data.auth_provider == AuthProvider.MOBILE:
            if not login_data.phone_number or not login_data.otp:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Phone number and OTP are required for mobile authentication",
                    error_code=ErrorCodes.BAD_REQUEST,
                    path=request_info["path"],
                    method=request_info["method"],
                    trace_id=request_info["trace_id"]
                )
            user = await users_service.authenticate_with_otp(
                db, 
                login_data.phone_number, 
                login_data.otp
            )
            
        elif login_data.auth_provider == AuthProvider.GOOGLE:
            if not login_data.google_token:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Google token is required for Google authentication",
                    error_code=ErrorCodes.BAD_REQUEST,
                    path=request_info["path"],
                    method=request_info["method"],
                    trace_id=request_info["trace_id"]
                )
            # TODO: Verify Google token and extract email
            # For now, we'll use a placeholder
            if login_data.email:
                user = await users_service.get_by_email(db, login_data.email)
            else:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Email is required for Google authentication",
                    error_code=ErrorCodes.BAD_REQUEST,
                    path=request_info["path"],
                    method=request_info["method"],
                    trace_id=request_info["trace_id"]
                )
        
        else:
            raise create_http_exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Unsupported authentication provider: {login_data.auth_provider}",
                error_code=ErrorCodes.BAD_REQUEST,
                path=request_info["path"],
                method=request_info["method"],
                trace_id=request_info["trace_id"]
            )
        
        if not user:
            raise create_authentication_http_exception(
                message="Invalid credentials",
                auth_type="credentials",
                path=request_info["path"],
                method=request_info["method"],
                trace_id=request_info["trace_id"]
            )
        
        if not user["status"] == UserStatus.ACTIVE:
            raise create_authentication_http_exception(
                message="User account is deactivated",
                auth_type="account_status",
                path=request_info["path"],
                method=request_info["method"],
                trace_id=request_info["trace_id"]
            )
        
        # Create access token
        token_data = {
            "sub": str(user["id"]),
            "user_type": user["user_type"].value,
            "auth_provider": user["auth_provider"].value
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)  # 30 minutes expiry
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            expires_in=30 * 60,  # 30 minutes in seconds
            user=user
        )
        
        return LoginResponse(data=token_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Login failed: {str(e)}",
            error_code=ErrorCodes.AUTHENTICATION_FAILED,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


@router.post("/login/email", response_model=LoginResponse)
async def login_with_email(
    request: Request,
    login_data: EmailLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user with email and password"""
    try:
        # Log request details for debugging
        print(f"DEBUG: Login request received for email: {login_data.email}")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        print(f"DEBUG: Content-Type: {request.headers.get('content-type', 'Not set')}")
        
        # Check request body
        try:
            body = await request.body()
            print(f"DEBUG: Request body size: {len(body) if body else 0}")
            if body:
                print(f"DEBUG: Request body preview: {body[:200]}")
                try:
                    # Try to parse as JSON to see if it's valid
                    json_data = json.loads(body)
                    print(f"DEBUG: JSON parsed successfully: {json_data}")
                except json.JSONDecodeError as json_error:
                    print(f"DEBUG: JSON decode error: {json_error}")
                    print(f"DEBUG: Invalid JSON at position: {json_error.pos}")
                    print(f"DEBUG: Invalid character: {body[json_error.pos:json_error.pos+10] if json_error.pos < len(body) else 'End of body'}")
                    
                    # Try to fix common JSON issues
                    try:
                        # Remove trailing commas
                        fixed_body = body.decode('utf-8').replace(',}', '}').replace(',]', ']')
                        json_data = json.loads(fixed_body)
                        print(f"DEBUG: JSON fixed and parsed successfully: {json_data}")
                    except:
                        print("DEBUG: Could not fix JSON automatically")
            else:
                print("DEBUG: Request body is empty!")
        except Exception as body_error:
            print(f"DEBUG: Error reading request body: {body_error}")
        
        user = await users_service.authenticate_user(
            db, 
            AuthProvider.EMAIL, 
            login_data.email, 
            login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user["status"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        # Create access token
        token_data = {
            "sub": str(user["id"]),
            "user_type": user["user_type"].value,
            "auth_provider": user["auth_provider"].value
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            expires_in=30 * 60,
            user=user
        )
        
        return LoginResponse(data=token_response)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email login failed: {str(e)}"
        )


@router.post("/login/mobile", response_model=LoginResponse)
async def login_with_mobile(
    login_data: MobileOTPLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user with mobile number and OTP"""
    try:
        user = await users_service.authenticate_with_otp(
            db, 
            login_data.phone_number, 
            login_data.otp
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or OTP"
            )
        
        if not user["status"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        # Create access token
        token_data = {
            "sub": str(user["id"]),
            "user_type": user["user_type"].value,
            "auth_provider": user["auth_provider"].value
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            expires_in=30 * 60,
            user=user
        )
        
        return LoginResponse(data=token_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mobile login failed: {str(e)}"
        )


@router.post("/login/google", response_model=LoginResponse)
async def login_with_google(
    login_data: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user with Google OAuth"""
    try:
        # TODO: Verify Google ID token and extract user information
        # For now, this is a placeholder implementation
        
        # In production, you would:
        # 1. Verify the Google ID token
        # 2. Extract user email and other details
        # 3. Find or create user in your database
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth login is not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google login failed: {str(e)}"
        )


# Email OTP Authentication Endpoints
@router.post("/send-email-otp", response_model=EmailOTPResponse)
async def send_email_otp(
    request: Request,
    otp_request: EmailOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send OTP to user's email for login"""
    try:
        request_info = extract_request_info(request)
        
        result = await users_service.send_email_otp(db, otp_request.email)
        
        return EmailOTPResponse(
            message=result["message"],
            email=result["email"],
            expires_in_minutes=result["expires_in_minutes"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to send email OTP: {str(e)}",
            error_code=ErrorCodes.OTP_SEND_FAILED,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


@router.post("/verify-email-otp", response_model=EmailOTPLoginResponse)
async def verify_email_otp(
    request: Request,
    verify_request: EmailOTPVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify email OTP and login user"""
    try:
        request_info = extract_request_info(request)
        
        # Verify OTP and get user
        user = await users_service.verify_email_otp(
            db, 
            verify_request.email, 
            verify_request.otp_code
        )
        
        if not user:
            raise create_authentication_http_exception(
                message="Invalid or expired OTP",
                auth_type="otp",
                path=request_info["path"],
                method=request_info["method"],
                trace_id=request_info["trace_id"]
            )
        
        # Create access token
        token_data = {
            "sub": str(user["id"]),
            "user_type": user["user_type"].value,
            "auth_provider": user["auth_provider"].value
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)  # 30 minutes expiry
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            expires_in=30 * 60,  # 30 minutes in seconds
            user=user
        )
        
        return EmailOTPLoginResponse(
            data=token_response,
            message="Login successful with email OTP"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to verify email OTP: {str(e)}",
            error_code=ErrorCodes.OTP_VERIFICATION_FAILED,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


@router.post("/resend-email-otp", response_model=EmailOTPResponse)
async def resend_email_otp(
    request: Request,
    otp_request: EmailOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resend OTP to user's email"""
    try:
        request_info = extract_request_info(request)
        
        result = await users_service.resend_email_otp(db, otp_request.email)
        
        return EmailOTPResponse(
            message=result["message"],
            email=result["email"],
            expires_in_minutes=result["expires_in_minutes"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        request_info = extract_request_info(request)
        raise create_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to resend email OTP: {str(e)}",
            error_code=ErrorCodes.OTP_RESEND_FAILED,
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )

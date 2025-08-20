from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    TokenResponse,
    EmailLoginRequest,
    MobileOTPLoginRequest,
    GoogleLoginRequest
)
from app.services.users_service import users_service
from app.utils.auth import create_access_token
from app.utils.error_handler import (
    create_http_exception,
    create_authentication_http_exception,
    create_server_error_http_exception,
    extract_request_info
)
from app.models.user import AuthProvider
from app.schemas.errors import ErrorCodes, ErrorMessages
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
        
        if not user.status:
            raise create_authentication_http_exception(
                message="User account is deactivated",
                auth_type="account_status",
                path=request_info["path"],
                method=request_info["method"],
                trace_id=request_info["trace_id"]
            )
        
        # Create access token
        token_data = {
            "sub": str(user.id),
            "user_type": user.user_type.value,
            "auth_provider": user.auth_provider.value
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)  # 30 minutes expiry
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            expires_in=30 * 60,  # 30 minutes in seconds
            user_id=user.id,
            user_type=user.user_type.value,
            full_name=user.full_name
        )
        
        return LoginResponse(data=token_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise create_server_error_http_exception(
            message=f"Login failed: {str(e)}",
            component="authentication",
            path=request_info["path"],
            method=request_info["method"],
            trace_id=request_info["trace_id"]
        )


@router.post("/login/email", response_model=LoginResponse)
async def login_with_email(
    login_data: EmailLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user with email and password"""
    try:
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
        
        if not user.status:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        # Create access token
        token_data = {
            "sub": str(user.id),
            "user_type": user.user_type.value,
            "auth_provider": user.auth_provider.value
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            expires_in=30 * 60,
            user_id=user.id,
            user_type=user.user_type.value,
            full_name=user.full_name
        )
        
        return LoginResponse(data=token_response)
        
    except HTTPException:
        raise
    except Exception as e:
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
        
        if not user.status:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        # Create access token
        token_data = {
            "sub": str(user.id),
            "user_type": user.user_type.value,
            "auth_provider": user.auth_provider.value
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            expires_in=30 * 60,
            user_id=user.id,
            user_type=user.user_type.value,
            full_name=user.full_name
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

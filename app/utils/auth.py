from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.database import get_db
from app.models.user import User

# Create a CryptContext with settings to handle bcrypt's limitations
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,  # Don't raise error on truncation
    bcrypt__max_rounds=12  # Reasonable work factor
)

# Security scheme for JWT
security = HTTPBearer()


def truncate_password_for_bcrypt(password: str) -> str:
    """
    Truncate a password to 72 bytes for bcrypt compliance.
    This function handles UTF-8 character boundaries safely.
    
    Args:
        password: The password string to truncate
        
    Returns:
        A truncated password string that encodes to <= 72 bytes
    """
    # Convert to bytes for accurate length measurement
    password_bytes = password.encode('utf-8')
    
    # If under 72 bytes, no need to truncate
    if len(password_bytes) <= 72:
        return password
        
    # Truncate to 72 bytes or less
    truncated = password_bytes[:72]
    
    # Make sure we end at a valid UTF-8 character boundary
    # Remove any incomplete UTF-8 sequences at the end
    while truncated and (truncated[-1] & 0x80) and not (truncated[-1] & 0x40):
        truncated = truncated[:-1]
    
    # Convert back to string
    result = truncated.decode('utf-8', errors='replace')
    
    # Final safety check - in case decoding produces something > 72 bytes
    while result and len(result.encode('utf-8')) > 72:
        result = result[:-1]
        
    return result


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash with bcrypt 72-byte limit handling
    
    This function safely truncates passwords longer than 72 bytes before
    verification, which is bcrypt's limit.
    """
    # Truncate plain password if needed
    if plain_password and len(plain_password.encode('utf-8')) > 72:
        plain_password = truncate_password_for_bcrypt(plain_password)
    
    # Use standard pwd_context for verification
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt 72-byte limit handling
    
    bcrypt has a maximum password length of 72 bytes. This function safely
    truncates passwords longer than 72 bytes before hashing.
    """
    # Truncate password if needed
    if password and len(password.encode('utf-8')) > 72:
        password = truncate_password_for_bcrypt(password)
        
    # Use standard pwd_context for hashing
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    from app.services.users_service import users_service  # Import here to avoid circular import
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify and decode the token
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        # Extract user ID from payload
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except (JWTError, ValueError):
        raise credentials_exception
    
    # Get user from database
    user = await users_service.get(db, id=user_id)
    if user is None:
        raise credentials_exception
        
    return user

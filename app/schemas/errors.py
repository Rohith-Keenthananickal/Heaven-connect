from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import datetime


class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = Field(None, description="Field name where error occurred")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code for programmatic handling")
    value: Optional[Any] = Field(None, description="Value that caused the error")


class ErrorResponse(BaseModel):
    """Standard error response format for all APIs"""
    status: str = Field("error", description="Response status - always 'error' for error responses")
    message: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(None, description="Application-specific error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the error occurred")
    path: Optional[str] = Field(None, description="API endpoint path where error occurred")
    method: Optional[str] = Field(None, description="HTTP method used")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    trace_id: Optional[str] = Field(None, description="Unique trace ID for debugging")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    def dict(self, *args, **kwargs):
        """Override dict method to handle datetime serialization"""
        d = super().dict(*args, **kwargs)
        # Convert datetime to ISO string for JSON serialization
        if isinstance(d.get('timestamp'), datetime):
            d['timestamp'] = d['timestamp'].isoformat()
        return d


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field-specific details"""
    details: List[ErrorDetail] = Field(..., description="Validation error details for each field")


class NotFoundErrorResponse(ErrorResponse):
    """Not found error response"""
    resource: Optional[str] = Field(None, description="Type of resource that was not found")
    resource_id: Optional[str] = Field(None, description="ID of the resource that was not found")


class AuthenticationErrorResponse(ErrorResponse):
    """Authentication error response"""
    auth_type: Optional[str] = Field(None, description="Type of authentication that failed")
    required_scopes: Optional[List[str]] = Field(None, description="Required permissions/scopes")


class RateLimitErrorResponse(ErrorResponse):
    """Rate limit exceeded error response"""
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    limit: Optional[int] = Field(None, description="Rate limit that was exceeded")
    window: Optional[str] = Field(None, description="Time window for the rate limit")


class ServerErrorResponse(ErrorResponse):
    """Server error response"""
    error_id: Optional[str] = Field(None, description="Internal error ID for support team")
    component: Optional[str] = Field(None, description="System component where error occurred")


# Common error messages
class ErrorMessages:
    """Common error message constants"""
    # General errors
    INTERNAL_SERVER_ERROR = "An internal server error occurred"
    VALIDATION_ERROR = "Validation error occurred"
    NOT_FOUND = "Resource not found"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Access denied"
    BAD_REQUEST = "Invalid request"
    CONFLICT = "Resource conflict"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
    
    # User-related errors
    USER_NOT_FOUND = "User not found"
    USER_ALREADY_EXISTS = "User already exists"
    INVALID_CREDENTIALS = "Invalid credentials"
    ACCOUNT_DEACTIVATED = "Account is deactivated"
    INVALID_TOKEN = "Invalid or expired token"
    
    # Property-related errors
    PROPERTY_NOT_FOUND = "Property not found"
    PROPERTY_ALREADY_EXISTS = "Property already exists"
    INVALID_PROPERTY_DATA = "Invalid property data"
    
    # File-related errors
    FILE_TOO_LARGE = "File size exceeds maximum allowed size"
    INVALID_FILE_TYPE = "Invalid file type"
    FILE_UPLOAD_FAILED = "File upload failed"
    
    # Image-related errors
    INVALID_IMAGE_TYPE = "Invalid image type"
    INVALID_FILE_FORMAT = "Invalid file format"
    INVALID_FILENAME = "Invalid filename"
    IMAGE_UPLOAD_FAILED = "Image upload failed"
    IMAGE_PROCESSING_FAILED = "Image processing failed"
    IMAGE_DELETION_FAILED = "Image deletion failed"
    
    # Database errors
    DATABASE_CONNECTION_ERROR = "Database connection error"
    DATABASE_QUERY_ERROR = "Database query error"
    
    # OTP errors
    OTP_EXPIRED = "OTP has expired"
    OTP_INVALID = "Invalid OTP"
    OTP_ALREADY_USED = "OTP has already been used"
    
    # Area Coordinator errors
    AREA_COORDINATOR_NOT_FOUND = "Area coordinator not found"
    ALREADY_APPROVED = "Already approved"
    ALREADY_REJECTED = "Already rejected"
    APPROVAL_FAILED = "Approval failed"
    REJECTION_FAILED = "Rejection failed"
    
    # Bank Details errors
    BANK_DETAILS_ALREADY_EXISTS = "Bank details already exist"
    BANK_DETAILS_NOT_FOUND = "Bank details not found"
    BANK_DETAILS_CREATION_FAILED = "Bank details creation failed"
    BANK_DETAILS_UPDATE_FAILED = "Bank details update failed"
    BANK_DETAILS_VERIFICATION_FAILED = "Bank details verification failed"
    
    # Profile errors
    PROFILE_NOT_FOUND = "Profile not found"
    PROFILE_UPDATE_FAILED = "Profile update failed"
    INVALID_USER_TYPE = "Invalid user type"
    
    # Search errors
    SEARCH_FAILED = "Search operation failed"


# Common error codes
class ErrorCodes:
    """Common error code constants"""
    # General errors
    INTERNAL_SERVER_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    BAD_REQUEST = "BAD_REQUEST"
    CONFLICT = "CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # User-related errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # Property-related errors
    PROPERTY_NOT_FOUND = "PROPERTY_NOT_FOUND"
    PROPERTY_ALREADY_EXISTS = "PROPERTY_ALREADY_EXISTS"
    INVALID_PROPERTY_DATA = "INVALID_PROPERTY_DATA"
    
    # File-related errors
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    
    # Image-related errors
    INVALID_IMAGE_TYPE = "INVALID_IMAGE_TYPE"
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    INVALID_FILENAME = "INVALID_FILENAME"
    IMAGE_UPLOAD_FAILED = "IMAGE_UPLOAD_FAILED"
    IMAGE_PROCESSING_FAILED = "IMAGE_PROCESSING_FAILED"
    IMAGE_DELETION_FAILED = "IMAGE_DELETION_FAILED"
    
    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    
    # OTP errors
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_INVALID = "OTP_INVALID"
    OTP_ALREADY_USED = "OTP_ALREADY_USED"
    
    # Area Coordinator errors
    AREA_COORDINATOR_NOT_FOUND = "AREA_COORDINATOR_NOT_FOUND"
    ALREADY_APPROVED = "ALREADY_APPROVED"
    ALREADY_REJECTED = "ALREADY_REJECTED"
    APPROVAL_FAILED = "APPROVAL_FAILED"
    REJECTION_FAILED = "REJECTION_FAILED"
    
    # Bank Details errors
    BANK_DETAILS_ALREADY_EXISTS = "BANK_DETAILS_ALREADY_EXISTS"
    BANK_DETAILS_NOT_FOUND = "BANK_DETAILS_NOT_FOUND"
    BANK_DETAILS_CREATION_FAILED = "BANK_DETAILS_CREATION_FAILED"
    BANK_DETAILS_UPDATE_FAILED = "BANK_DETAILS_UPDATE_FAILED"
    BANK_DETAILS_VERIFICATION_FAILED = "BANK_DETAILS_VERIFICATION_FAILED"
    
    # Profile errors
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    PROFILE_UPDATE_FAILED = "PROFILE_UPDATE_FAILED"
    INVALID_USER_TYPE = "INVALID_USER_TYPE"
    
    # Search errors
    SEARCH_FAILED = "SEARCH_FAILED"

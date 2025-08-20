import uuid
from typing import Optional, List, Any
from fastapi import Request, HTTPException, status
from app.schemas.errors import (
    ErrorResponse, 
    ValidationErrorResponse, 
    NotFoundErrorResponse,
    AuthenticationErrorResponse,
    RateLimitErrorResponse,
    ServerErrorResponse,
    ErrorDetail,
    ErrorMessages,
    ErrorCodes
)


def generate_trace_id() -> str:
    """Generate a unique trace ID for error tracking"""
    return str(uuid.uuid4())


def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[List[ErrorDetail]] = None,
    trace_id: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None
) -> ErrorResponse:
    """Create a standard error response"""
    return ErrorResponse(
        message=message,
        error_code=error_code,
        details=details,
        trace_id=trace_id or generate_trace_id(),
        path=path,
        method=method
    )


def create_validation_error_response(
    errors: List[dict],
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> ValidationErrorResponse:
    """Create a validation error response from Pydantic validation errors"""
    error_details = []
    
    for error in errors:
        field = error.get("loc", [None])[-1] if error.get("loc") else None
        error_details.append(ErrorDetail(
            field=str(field) if field else None,
            message=error.get("msg", "Validation error"),
            code=error.get("type", "validation_error"),
            value=error.get("input")
        ))
    
    return ValidationErrorResponse(
        message=ErrorMessages.VALIDATION_ERROR,
        error_code=ErrorCodes.VALIDATION_ERROR,
        details=error_details,
        trace_id=trace_id or generate_trace_id(),
        path=path,
        method=method
    )


def create_not_found_error_response(
    resource: str,
    resource_id: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> NotFoundErrorResponse:
    """Create a not found error response"""
    return NotFoundErrorResponse(
        message=f"{resource} not found",
        error_code=ErrorCodes.NOT_FOUND,
        resource=resource,
        resource_id=resource_id,
        trace_id=trace_id or generate_trace_id(),
        path=path,
        method=method
    )


def create_authentication_error_response(
    message: str = ErrorMessages.UNAUTHORIZED,
    auth_type: Optional[str] = None,
    required_scopes: Optional[List[str]] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> AuthenticationErrorResponse:
    """Create an authentication error response"""
    return AuthenticationErrorResponse(
        message=message,
        error_code=ErrorCodes.UNAUTHORIZED,
        auth_type=auth_type,
        required_scopes=required_scopes,
        trace_id=trace_id or generate_trace_id(),
        path=path,
        method=method
    )


def create_server_error_response(
    message: str = ErrorMessages.INTERNAL_SERVER_ERROR,
    error_id: Optional[str] = None,
    component: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> ServerErrorResponse:
    """Create a server error response"""
    return ServerErrorResponse(
        message=message,
        error_id=error_id or generate_trace_id(),
        component=component,
        trace_id=trace_id or generate_trace_id(),
        path=path,
        method=method
    )


def create_rate_limit_error_response(
    retry_after: int,
    limit: Optional[int] = None,
    window: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> RateLimitErrorResponse:
    """Create a rate limit error response"""
    return RateLimitErrorResponse(
        message=ErrorMessages.RATE_LIMIT_EXCEEDED,
        error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
        retry_after=retry_after,
        limit=limit,
        window=window,
        trace_id=trace_id or generate_trace_id(),
        path=path,
        method=method
    )


def extract_request_info(request: Request) -> dict:
    """Extract relevant information from FastAPI request"""
    return {
        "path": str(request.url.path),
        "method": request.method,
        "trace_id": generate_trace_id()
    }


def create_http_exception(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[List[ErrorDetail]] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> HTTPException:
    """Create an HTTPException with standardized error response"""
    error_response = create_error_response(
        message=message,
        error_code=error_code,
        details=details,
        path=path,
        method=method,
        trace_id=trace_id
    )
    
    # Convert to dict and handle datetime serialization
    error_dict = error_response.dict()
    
    return HTTPException(
        status_code=status_code,
        detail=error_dict
    )


def create_validation_http_exception(
    errors: List[dict],
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> HTTPException:
    """Create an HTTPException for validation errors"""
    error_response = create_validation_error_response(
        errors=errors,
        path=path,
        method=method,
        trace_id=trace_id
    )
    
    # Convert to dict and handle datetime serialization
    error_dict = error_response.dict()
    
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=error_dict
    )


def create_not_found_http_exception(
    resource: str,
    resource_id: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> HTTPException:
    """Create an HTTPException for not found errors"""
    error_response = create_not_found_error_response(
        resource=resource,
        resource_id=resource_id,
        path=path,
        method=method,
        trace_id=trace_id
    )
    
    # Convert to dict and handle datetime serialization
    error_dict = error_response.dict()
    
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=error_dict
    )


def create_authentication_http_exception(
    message: str = ErrorMessages.UNAUTHORIZED,
    auth_type: Optional[str] = None,
    required_scopes: Optional[List[str]] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> HTTPException:
    """Create an HTTPException for authentication errors"""
    error_response = create_authentication_error_response(
        message=message,
        auth_type=auth_type,
        required_scopes=required_scopes,
        path=path,
        method=method,
        trace_id=trace_id
    )
    
    # Convert to dict and handle datetime serialization
    error_dict = error_response.dict()
    
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_dict
    )


def create_server_error_http_exception(
    message: str = ErrorMessages.INTERNAL_SERVER_ERROR,
    error_id: Optional[str] = None,
    component: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    trace_id: Optional[str] = None
) -> HTTPException:
    """Create an HTTPException for server errors"""
    error_response = create_server_error_response(
        message=message,
        error_id=error_id,
        component=component,
        path=path,
        method=method,
        trace_id=trace_id
    )
    
    # Convert to dict and handle datetime serialization
    error_dict = error_response.dict()
    
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=error_dict
    )

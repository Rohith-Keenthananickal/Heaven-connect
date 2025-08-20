from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import traceback
import logging
from app.utils.error_handler import (
    create_validation_error_response,
    create_server_error_response,
    create_error_response,
    extract_request_info,
    generate_trace_id
)
from app.schemas.errors import ErrorCodes, ErrorMessages

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    request_info = extract_request_info(request)
    
    error_response = create_validation_error_response(
        errors=exc.errors(),
        path=request_info["path"],
        method=request_info["method"],
        trace_id=request_info["trace_id"]
    )
    
    logger.warning(f"Validation error: {error_response.dict()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.dict()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    request_info = extract_request_info(request)
    
    # Check if the exception already has a formatted error response
    if isinstance(exc.detail, dict) and "status" in exc.detail:
        # Already formatted, return as is
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # Create standardized error response
    error_response = create_error_response(
        message=str(exc.detail) if exc.detail else "HTTP error occurred",
        error_code=ErrorCodes.BAD_REQUEST if exc.status_code == 400 else None,
        path=request_info["path"],
        method=request_info["method"],
        trace_id=request_info["trace_id"]
    )
    
    logger.warning(f"HTTP exception: {error_response.dict()}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors"""
    request_info = extract_request_info(request)
    trace_id = request_info["trace_id"]
    
    # Log the full error for debugging
    logger.error(f"Database error (trace_id: {trace_id}): {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    error_response = create_server_error_response(
        message=ErrorMessages.DATABASE_QUERY_ERROR,
        component="database",
        path=request_info["path"],
        method=request_info["method"],
        trace_id=trace_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors from models"""
    request_info = extract_request_info(request)
    
    error_response = create_validation_error_response(
        errors=exc.errors(),
        path=request_info["path"],
        method=request_info["method"],
        trace_id=request_info["trace_id"]
    )
    
    logger.warning(f"Pydantic validation error: {error_response.dict()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions"""
    request_info = extract_request_info(request)
    trace_id = request_info["trace_id"]
    
    # Log the full error for debugging
    logger.error(f"Unhandled exception (trace_id: {trace_id}): {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    error_response = create_server_error_response(
        message=ErrorMessages.INTERNAL_SERVER_ERROR,
        component="application",
        path=request_info["path"],
        method=request_info["method"],
        trace_id=trace_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

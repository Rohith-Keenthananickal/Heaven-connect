# Error Handling System

This document describes the standardized error handling system implemented across all APIs in the Heaven Connect application.

## Overview

The error handling system provides:
- **Consistent error response format** across all endpoints
- **Unique trace IDs** for debugging and support
- **Structured error details** with field-specific information
- **Global exception handling** for unhandled errors
- **Standardized error codes** for programmatic handling

## Error Response Format

All error responses follow this structure:

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "error_code": "APPLICATION_ERROR_CODE",
  "timestamp": "2025-08-21T01:30:00.000Z",
  "path": "/api/v1/users",
  "method": "POST",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format",
      "code": "value_error.email",
      "value": "invalid-email"
    }
  ],
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Error Response Types

### 1. General Error Response
- **Class**: `ErrorResponse`
- **Use**: General application errors

### 2. Validation Error Response
- **Class**: `ValidationErrorResponse`
- **Use**: Pydantic validation errors
- **Features**: Field-specific error details

### 3. Not Found Error Response
- **Class**: `NotFoundErrorResponse`
- **Use**: Resource not found errors
- **Features**: Resource type and ID information

### 4. Authentication Error Response
- **Class**: `AuthenticationErrorResponse`
- **Use**: Authentication and authorization errors
- **Features**: Auth type and required scopes

### 5. Rate Limit Error Response
- **Class**: `RateLimitErrorResponse`
- **Use**: Rate limiting errors
- **Features**: Retry after time and limits

### 6. Server Error Response
- **Class**: `ServerErrorResponse`
- **Use**: Internal server errors
- **Features**: Error ID and component information

## Error Codes

### General Errors
- `INTERNAL_ERROR` - Internal server error
- `VALIDATION_ERROR` - Validation error
- `NOT_FOUND` - Resource not found
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Access denied
- `BAD_REQUEST` - Invalid request
- `CONFLICT` - Resource conflict
- `RATE_LIMIT_EXCEEDED` - Rate limit exceeded

### User-Related Errors
- `USER_NOT_FOUND` - User not found
- `USER_ALREADY_EXISTS` - User already exists
- `INVALID_CREDENTIALS` - Invalid credentials
- `ACCOUNT_DEACTIVATED` - Account is deactivated
- `INVALID_TOKEN` - Invalid or expired token

### Property-Related Errors
- `PROPERTY_NOT_FOUND` - Property not found
- `PROPERTY_ALREADY_EXISTS` - Property already exists
- `INVALID_PROPERTY_DATA` - Invalid property data

### File-Related Errors
- `FILE_TOO_LARGE` - File size exceeds maximum
- `INVALID_FILE_TYPE` - Invalid file type
- `FILE_UPLOAD_FAILED` - File upload failed

### Database Errors
- `DATABASE_CONNECTION_ERROR` - Database connection error
- `DATABASE_QUERY_ERROR` - Database query error

### OTP Errors
- `OTP_EXPIRED` - OTP has expired
- `OTP_INVALID` - Invalid OTP
- `OTP_ALREADY_USED` - OTP has already been used

## Usage Examples

### 1. Creating Custom Errors

```python
from app.utils.error_handler import create_http_exception
from app.schemas.errors import ErrorCodes

# Create a custom HTTP exception
raise create_http_exception(
    status_code=400,
    message="Custom error message",
    error_code=ErrorCodes.BAD_REQUEST
)
```

### 2. Validation Errors

```python
from app.utils.error_handler import create_validation_http_exception

# Create validation error from Pydantic errors
raise create_validation_http_exception(
    errors=validation_errors,
    path="/api/v1/users",
    method="POST"
)
```

### 3. Not Found Errors

```python
from app.utils.error_handler import create_not_found_http_exception

# Create not found error
raise create_not_found_http_exception(
    resource="User",
    resource_id="123",
    path="/api/v1/users/123",
    method="GET"
)
```

### 4. Authentication Errors

```python
from app.utils.error_handler import create_authentication_http_exception

# Create authentication error
raise create_authentication_http_exception(
    message="Invalid credentials",
    auth_type="password",
    required_scopes=["read:users"]
)
```

### 5. Server Errors

```python
from app.utils.error_handler import create_server_error_http_exception

# Create server error
raise create_server_error_http_exception(
    message="Database operation failed",
    component="database",
    error_id="db_001"
)
```

## Global Exception Handling

The system automatically handles:

1. **Pydantic Validation Errors** - Converts to structured validation responses
2. **HTTP Exceptions** - Formats with standard error structure
3. **SQLAlchemy Errors** - Database-specific error handling
4. **General Exceptions** - Catches all unhandled errors

## Benefits

1. **Consistency**: All APIs return errors in the same format
2. **Debugging**: Unique trace IDs for error tracking
3. **User Experience**: Clear, actionable error messages
4. **Monitoring**: Structured error data for analytics
5. **Support**: Detailed error information for troubleshooting

## Best Practices

1. **Use appropriate error codes** for different error types
2. **Provide clear, actionable error messages**
3. **Include relevant context** in error details
4. **Log errors with trace IDs** for debugging
5. **Use specific error types** when available

## Testing

To test the error handling:

1. Send invalid data to endpoints
2. Try to access non-existent resources
3. Use invalid authentication tokens
4. Trigger validation errors
5. Check that all errors follow the standard format

## Monitoring

Monitor error responses for:
- Error frequency by type
- Response times for error cases
- User impact of different errors
- System health indicators

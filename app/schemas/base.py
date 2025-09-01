from pydantic import BaseModel
from typing import Any, Optional, List


class BaseResponse(BaseModel):
    """Base response schema with status, data, and message fields"""
    status: str = "success"
    data: Any
    message: Optional[str] = None


class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    """Paginated response schema with status, data, message, and pagination"""
    status: str = "success"
    data: List[Any]
    message: Optional[str] = None
    pagination: PaginationInfo


class ErrorResponse(BaseModel):
    """Error response schema"""
    status: str = "error"
    detail: str
    

class MessageResponse(BaseModel):
    """Message response schema"""
    message: str

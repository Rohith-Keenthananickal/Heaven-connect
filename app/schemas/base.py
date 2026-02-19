from pydantic import BaseModel
from typing import Any, Optional, List
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseResponse(BaseModel,Generic[T]):
    """Base response schema with status, data, and message fields"""
    status: str = "success"
    data: T
    message: Optional[str] = None


class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel,Generic[T]):
    """Paginated response schema with status, data, message, and pagination"""
    status: str = "success"
    data: List[T]
    message: Optional[str] = None
    pagination: PaginationInfo


class ErrorResponse(BaseModel,Generic[T]):
    """Error response schema"""
    status: str = "error"
    detail: T
    

class MessageResponse(BaseModel,Generic[T]):
    """Message response schema"""
    message: T

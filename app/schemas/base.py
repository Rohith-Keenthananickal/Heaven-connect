from pydantic import BaseModel
from typing import Any, Optional


class BaseResponse(BaseModel):
    """Base response schema with status and data fields"""
    status: str = "success"
    data: Any


class ErrorResponse(BaseModel):
    """Error response schema"""
    status: str = "error"
    detail: str
    

class MessageResponse(BaseModel):
    """Message response schema"""
    message: str

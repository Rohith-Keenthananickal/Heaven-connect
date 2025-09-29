from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ImageUploadRequest(BaseModel):
    """Request schema for image upload"""
    image_type: str = Field(..., description="Type of image (user, property, room, document, bank, profile)")


class ImageUploadResponse(BaseModel):
    """Response schema for successful image upload"""
    status: str = "success"
    message: str = "Image uploaded successfully"
    data: Dict[str, Any] = Field(..., description="Upload result data")


class MultipleImageUploadResponse(BaseModel):
    """Response schema for multiple image uploads"""
    status: str = "success"
    message: str = "Images uploaded successfully"
    data: List[Dict[str, Any]] = Field(..., description="List of upload results")
    total_uploaded: int = Field(..., description="Total number of successfully uploaded images")
    total_failed: int = Field(..., description="Total number of failed uploads")


class ImageInfo(BaseModel):
    """Schema for image information"""
    s3_key: str = Field(..., description="S3 key (path) of the uploaded file")
    file_name: str = Field(..., description="Name of the uploaded file")
    file_size: int = Field(..., description="Size of the file in bytes")
    file_type: str = Field(..., description="File extension/type")
    image_type: str = Field(..., description="Type of image uploaded")
    url: str = Field(..., description="Public URL for the image")
    uploaded_at: str = Field(..., description="Upload timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional file metadata")


class ImageTypeInfo(BaseModel):
    """Schema for image type configuration information"""
    max_size_mb: int = Field(..., description="Maximum file size in MB")
    allowed_formats: List[str] = Field(..., description="Allowed file formats")
    max_dimensions: tuple = Field(..., description="Maximum image dimensions (width, height)")


class ImageTypesResponse(BaseModel):
    """Response schema for getting allowed image types"""
    status: str = "success"
    message: str = "Image types retrieved successfully"
    data: Dict[str, ImageTypeInfo] = Field(..., description="Available image types and their configurations")


class ImageDeleteResponse(BaseModel):
    """Response schema for image deletion"""
    status: str = "success"
    message: str = "Image deleted successfully"
    data: Dict[str, Any] = Field(..., description="Deletion result")


class ImageUploadError(BaseModel):
    """Schema for upload errors"""
    error: str = Field(..., description="Error message")
    file_name: str = Field(..., description="Name of the file that failed")
    success: bool = Field(False, description="Upload success status")


class BulkUploadResult(BaseModel):
    """Schema for bulk upload results"""
    successful: List[ImageInfo] = Field(..., description="Successfully uploaded images")
    failed: List[ImageUploadError] = Field(..., description="Failed uploads")
    total_uploaded: int = Field(..., description="Total successful uploads")
    total_failed: int = Field(..., description="Total failed uploads")

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
from app.models.property import PhotoCategory


def validate_file_type(file: UploadFile) -> bool:
    """Validate uploaded file type"""
    if not file.filename:
        return False
    
    file_extension = Path(file.filename).suffix.lower()
    return file_extension in settings.get_allowed_extensions()


def validate_file_size(file: UploadFile) -> bool:
    """Validate uploaded file size"""
    # FastAPI doesn't provide file size directly, so we'll check during save
    return True


async def save_uploaded_file(
    file: UploadFile, 
    property_id: int, 
    category: str,
    subfolder: Optional[str] = None
) -> str:
    """Save uploaded file and return the file path"""
    
    # Validate file type
    if not validate_file_type(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.get_allowed_extensions())}"
        )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create directory path
    if subfolder:
        directory = Path(settings.UPLOAD_DIR) / str(property_id) / category / subfolder
    else:
        directory = Path(settings.UPLOAD_DIR) / str(property_id) / category
    
    directory.mkdir(parents=True, exist_ok=True)
    
    # Full file path
    file_path = directory / unique_filename
    
    try:
        # Read and save file
        contents = await file.read()
        
        # Check file size
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Return relative path for storing in database
        relative_path = str(file_path.relative_to(Path(settings.UPLOAD_DIR).parent))
        return relative_path
        
    except Exception as e:
        # Clean up file if it was created
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


def delete_file(file_path: str) -> bool:
    """Delete a file from storage"""
    try:
        full_path = Path(file_path)
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception:
        return False


def get_file_url(file_path: str) -> str:
    """Get full URL for a file (placeholder for production URL generation)"""
    # In production, this would generate proper URLs for CDN or file server
    return f"/uploads/{file_path}"


async def save_profile_image(file: UploadFile, user_id: int) -> str:
    """Save user profile image"""
    return await save_uploaded_file(file, user_id, "profile", None)


async def save_id_proof(file: UploadFile, property_id: int) -> str:
    """Save property ID proof document"""
    return await save_uploaded_file(file, property_id, "documents", "id_proof")


async def save_property_photo(file: UploadFile, property_id: int, category: PhotoCategory) -> str:
    """Save property photo"""
    return await save_uploaded_file(file, property_id, "photos", category.value)

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
import os
from app.services.image_service import image_service
from app.schemas.images import (
    ImageUploadResponse, MultipleImageUploadResponse, ImageTypesResponse,
    ImageDeleteResponse, ImageInfo
)

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_single_image(
    file: UploadFile = File(..., description="Image file to upload"),
    image_type: str = Form(..., description="Type of image (user, property, room, document, bank, profile)"),
    user_id: Optional[int] = Form(None, description="User ID for user-specific uploads")
):
    """
    Upload a single image file
    
    - **file**: The image file to upload
    - **image_type**: Type of image (user, property, room, document, bank, profile)
    - **user_id**: Optional user ID for user-specific uploads (required for user/profile types)
    """
    try:
        # Validate user_id for user-specific uploads
        if image_type in ["user", "profile"] and not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required for user and profile image uploads"
            )
        
        # Upload the image
        result = await image_service.upload_image(file, image_type, user_id)
        
        # Generate public URL
        public_url = image_service.get_image_url(result["file_path"])
        result["public_url"] = public_url
        
        return ImageUploadResponse(
            message="Image uploaded successfully",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/upload/multiple", response_model=MultipleImageUploadResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(..., description="Multiple image files to upload"),
    image_type: str = Form(..., description="Type of image (user, property, room, document, bank, profile)"),
    user_id: Optional[int] = Form(None, description="User ID for user-specific uploads")
):
    """
    Upload multiple image files of the same type
    
    - **files**: List of image files to upload
    - **image_type**: Type of image (user, property, room, document, bank, profile)
    - **user_id**: Optional user ID for user-specific uploads (required for user/profile types)
    """
    try:
        # Validate user_id for user-specific uploads
        if image_type in ["user", "profile"] and not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required for user and profile image uploads"
            )
        
        # Validate number of files
        if len(files) > 10:  # Limit to 10 files at once
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files can be uploaded at once"
            )
        
        # Upload multiple images
        results = await image_service.upload_multiple_images(files, image_type, user_id)
        
        # Separate successful and failed uploads
        successful = []
        failed = []
        
        for result in results:
            if "error" not in result:
                # Generate public URL for successful uploads
                public_url = image_service.get_image_url(result["file_path"])
                result["public_url"] = public_url
                successful.append(result)
            else:
                failed.append(result)
        
        return MultipleImageUploadResponse(
            message=f"Uploaded {len(successful)} out of {len(files)} images successfully",
            data=results,
            total_uploaded=len(successful),
            total_failed=len(failed)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload images: {str(e)}"
        )


@router.get("/types", response_model=ImageTypesResponse)
async def get_image_types():
    """
    Get information about allowed image types and their configurations
    
    Returns details about:
    - Allowed file formats
    - Maximum file sizes
    - Maximum dimensions
    - Upload folders
    """
    try:
        types_info = image_service.get_allowed_types()
        return ImageTypesResponse(
            message="Image types retrieved successfully",
            data=types_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve image types: {str(e)}"
        )


@router.delete("/delete", response_model=ImageDeleteResponse)
async def delete_image(
    file_path: str = Query(..., description="Path to the file to delete")
):
    """
    Delete an uploaded image file
    
    - **file_path**: Path to the file to delete (relative to uploads directory)
    """
    try:
        # Validate file path (prevent directory traversal)
        if ".." in file_path or file_path.startswith("/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )
        
        # Construct full path
        full_path = os.path.join("uploads", file_path.lstrip("uploads/"))
        
        # Delete the file
        success = await image_service.delete_image(full_path)
        
        if success:
            return ImageDeleteResponse(
                message="Image deleted successfully",
                data={"deleted": True, "file_path": file_path}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or already deleted"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )


@router.get("/serve/{file_path:path}")
async def serve_image(file_path: str):
    """
    Serve an uploaded image file
    
    - **file_path**: Path to the image file relative to uploads directory
    """
    try:
        # Validate file path (prevent directory traversal)
        if ".." in file_path or file_path.startswith("/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )
        
        # Construct full path
        full_path = os.path.join("uploads", file_path.lstrip("uploads/"))
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Return the file
        return FileResponse(full_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve image: {str(e)}"
        )


@router.get("/info/{file_path:path}")
async def get_image_info(file_path: str):
    """
    Get information about an uploaded image file
    
    - **file_path**: Path to the image file relative to uploads directory
    """
    try:
        # Validate file path (prevent directory traversal)
        if ".." in file_path or file_path.startswith("/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )
        
        # Construct full path
        full_path = os.path.join("uploads", file_path.lstrip("uploads/"))
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Get file stats
        stat = os.stat(full_path)
        
        # Generate public URL
        public_url = image_service.get_image_url(full_path)
        
        # Get file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Determine image type from path
        path_parts = file_path.split("/")
        image_type = path_parts[1] if len(path_parts) > 1 else "unknown"
        
        return {
            "status": "success",
            "message": "Image information retrieved successfully",
            "data": {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": stat.st_size,
                "file_type": file_extension.lstrip("."),
                "image_type": image_type,
                "uploaded_at": stat.st_mtime,
                "public_url": public_url,
                "metadata": {
                    "exists": True,
                    "readable": os.access(full_path, os.R_OK)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get image info: {str(e)}"
        )

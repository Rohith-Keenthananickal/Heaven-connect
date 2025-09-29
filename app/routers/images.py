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
    image_type: str = Form(..., description="Type of image (user, property, room, document, bank, profile)")
):
    """
    Upload a single image file
    
    - **file**: The image file to upload
    - **image_type**: Type of image (user, property, room, document, bank, profile)
    """
    try:
        # Upload the image to S3
        result = await image_service.upload_image(file, image_type)
        
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
    image_type: str = Form(..., description="Type of image (user, property, room, document, bank, profile)")
):
    """
    Upload multiple image files of the same type
    
    - **files**: List of image files to upload
    - **image_type**: Type of image (user, property, room, document, bank, profile)
    """
    try:
        # Validate number of files
        if len(files) > 10:  # Limit to 10 files at once
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files can be uploaded at once"
            )
        
        # Upload multiple images
        results = await image_service.upload_multiple_images(files, image_type)
        
        # Separate successful and failed uploads
        successful = []
        failed = []
        
        for result in results:
            if "error" not in result:
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
    s3_key: str = Query(..., description="S3 key (path) of the file to delete")
):
    """
    Delete an uploaded image file from S3
    
    - **s3_key**: S3 key (path) of the file to delete
    """
    try:
        # Delete the file from S3
        success = await image_service.delete_image(s3_key)
        
        if success:
            return ImageDeleteResponse(
                message="Image deleted successfully",
                data={"deleted": True, "s3_key": s3_key}
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


@router.get("/url/{s3_key:path}")
async def get_image_url(
    s3_key: str,
    expires_in: int = Query(3600, ge=60, le=86400, description="URL expiration time in seconds (60-86400)")
):
    """
    Get public or presigned URL for an image
    
    - **s3_key**: S3 key (path) of the image file
    - **expires_in**: URL expiration time in seconds (default: 1 hour, max: 24 hours)
    """
    try:
        # Get public URL (no expiration)
        public_url = image_service.get_image_url(s3_key)
        
        # Get presigned URL (with expiration)
        presigned_url = image_service.get_presigned_url(s3_key, expires_in)
        
        return {
            "status": "success",
            "data": {
                "s3_key": s3_key,
                "public_url": public_url,
                "presigned_url": presigned_url,
                "expires_in": expires_in
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate URL: {str(e)}"
        )


@router.get("/download/{s3_key:path}")
async def download_image(s3_key: str):
    """
    Download image content from S3
    
    - **s3_key**: S3 key (path) of the image file
    """
    try:
        # Download image content
        content = await image_service.download_image(s3_key)
        
        # Get file metadata to determine content type
        metadata = await image_service.get_image_metadata(s3_key)
        content_type = metadata.get("content_type", "application/octet-stream")
        
        # Return file content
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={s3_key.split('/')[-1]}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download image: {str(e)}"
        )


@router.get("/exists/{s3_key:path}")
async def check_image_exists(s3_key: str):
    """
    Check if an image exists in S3
    
    - **s3_key**: S3 key (path) of the image file
    """
    try:
        exists = await image_service.image_exists(s3_key)
        
        return {
            "status": "success",
            "data": {
                "s3_key": s3_key,
                "exists": exists
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check image existence: {str(e)}"
        )


@router.get("/metadata/{s3_key:path}")
async def get_image_metadata(s3_key: str):
    """
    Get image metadata from S3
    
    - **s3_key**: S3 key (path) of the image file
    """
    try:
        metadata = await image_service.get_image_metadata(s3_key)
        
        return {
            "status": "success",
            "data": {
                "s3_key": s3_key,
                "metadata": metadata
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get image metadata: {str(e)}"
        )



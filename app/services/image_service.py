import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io
from app.utils.error_handler import create_http_exception
from app.schemas.errors import ErrorCodes
from app.services.s3_service import s3_service


class ImageService:
    def __init__(self):
        # Allowed image types and their configurations
        self.allowed_types = {
            "user": {
                "max_size_mb": 5,
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "max_dimensions": (800, 800),
                "quality": 85
            },
            "property": {
                "max_size_mb": 10,
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "max_dimensions": (1920, 1080),
                "quality": 90
            },
            "room": {
                "max_size_mb": 8,
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "max_dimensions": (1600, 1200),
                "quality": 90
            },
            "document": {
                "max_size_mb": 15,
                "allowed_formats": ["jpg", "jpeg", "png", "pdf"],
                "max_dimensions": (1200, 1600),
                "quality": 85
            },
            "bank": {
                "max_size_mb": 8,
                "allowed_formats": ["jpg", "jpeg", "png", "pdf"],
                "max_dimensions": (1200, 1600),
                "quality": 85
            },
            "profile": {
                "max_size_mb": 3,
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "max_dimensions": (400, 400),
                "quality": 80
            }
        }

    async def upload_image(self, file: UploadFile, image_type: str) -> dict:
        """
        Upload and process an image file to S3
        
        Args:
            file: The uploaded file
            image_type: Type of image (user, property, room, etc.)
            
        Returns:
            dict: Contains s3_key, file_name, file_size, url, and metadata
        """
        try:
            # Validate image type
            if image_type not in self.allowed_types:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Invalid image type: {image_type}. Allowed types: {', '.join(self.allowed_types.keys())}",
                    error_code=ErrorCodes.INVALID_IMAGE_TYPE
                )
            
            config = self.allowed_types[image_type]
            
            # Validate file size
            await self._validate_file_size(file, config["max_size_mb"])
            
            # Validate file format
            file_extension = self._get_file_extension(file.filename)
            if file_extension.lower() not in config["allowed_formats"]:
                raise create_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Invalid file format. Allowed formats: {', '.join(config['allowed_formats'])}",
                    error_code=ErrorCodes.INVALID_FILE_FORMAT
                )
            
            # Generate unique filename
            unique_filename = self._generate_unique_filename(file_extension)
            
            # Generate S3 key
            s3_key = s3_service.generate_s3_key(image_type, unique_filename)
            
            # Process and upload image to S3
            file_info = await self._process_and_upload_to_s3(file, s3_key, config)
            
            # Generate public URL
            public_url = s3_service.get_public_url(s3_key)
            
            # Return file information
            return {
                "s3_key": s3_key,
                "file_name": unique_filename,
                "file_size": file_info["file_size"],
                "file_type": file_extension.lower(),
                "image_type": image_type,
                "url": public_url,
                "uploaded_at": datetime.utcnow().isoformat(),
                "metadata": file_info.get("metadata", {})
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to upload image: {str(e)}",
                error_code=ErrorCodes.IMAGE_UPLOAD_FAILED
            )

    async def upload_multiple_images(self, files: List[UploadFile], image_type: str) -> List[dict]:
        """
        Upload multiple images of the same type
        
        Args:
            files: List of uploaded files
            image_type: Type of image
            
        Returns:
            List of upload results
        """
        results = []
        for file in files:
            try:
                result = await self.upload_image(file, image_type)
                results.append(result)
            except Exception as e:
                # Log error but continue with other files
                results.append({
                    "error": str(e),
                    "file_name": file.filename,
                    "success": False
                })
        
        return results

    async def delete_image(self, s3_key: str) -> bool:
        """
        Delete an uploaded image file from S3
        
        Args:
            s3_key: S3 key (path) of the file to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            return await s3_service.delete_file(s3_key)
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to delete image: {str(e)}",
                error_code=ErrorCodes.IMAGE_DELETION_FAILED
            )

    async def _validate_file_size(self, file: UploadFile, max_size_mb: int):
        """Validate file size"""
        # Read first chunk to check size
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            raise create_http_exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)",
                error_code=ErrorCodes.FILE_TOO_LARGE
            )
        
        # Reset file pointer
        await file.seek(0)

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        if not filename or '.' not in filename:
            raise create_http_exception(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid filename",
                error_code=ErrorCodes.INVALID_FILENAME
            )
        return filename.rsplit('.', 1)[1]

    def _generate_unique_filename(self, extension: str) -> str:
        """Generate unique filename with timestamp and UUID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}.{extension}"

    async def _process_and_upload_to_s3(self, file: UploadFile, s3_key: str, config: dict) -> dict:
        """Process and upload the image file to S3"""
        try:
            content = await file.read()
            
            # For PDFs, upload directly
            if file.filename.lower().endswith('.pdf'):
                content_type = "application/pdf"
                metadata = {"type": "pdf"}
                
                await s3_service.upload_file(
                    file_content=content,
                    s3_key=s3_key,
                    content_type=content_type,
                    metadata=metadata
                )
                
                return {
                    "file_size": len(content),
                    "metadata": metadata
                }
            
            # For images, process and optimize
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if dimensions exceed maximum
            if image.size[0] > config["max_dimensions"][0] or image.size[1] > config["max_dimensions"][1]:
                image.thumbnail(config["max_dimensions"], Image.Resampling.LANCZOS)
            
            # Save optimized image to bytes
            output = io.BytesIO()
            if s3_key.lower().endswith('.webp'):
                image.save(output, 'WEBP', quality=config["quality"])
                content_type = "image/webp"
            else:
                image.save(output, 'JPEG', quality=config["quality"])
                content_type = "image/jpeg"
            
            processed_content = output.getvalue()
            
            # Upload to S3
            metadata = {
                "dimensions": f"{image.size[0]}x{image.size[1]}",
                "format": image.format or "JPEG",
                "mode": image.mode,
                "original_filename": file.filename
            }
            
            await s3_service.upload_file(
                file_content=processed_content,
                s3_key=s3_key,
                content_type=content_type,
                metadata=metadata
            )
            
            return {
                "file_size": len(processed_content),
                "metadata": metadata
            }
            
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to process and upload image: {str(e)}",
                error_code=ErrorCodes.IMAGE_PROCESSING_FAILED
            )


    def get_image_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """
        Generate public URL for the uploaded image from S3
        
        Args:
            s3_key: S3 key (path) of the image file
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: Public URL for the image
        """
        return s3_service.get_public_url(s3_key)
    
    def get_presigned_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """
        Generate presigned URL for the uploaded image from S3
        
        Args:
            s3_key: S3 key (path) of the image file
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: Presigned URL for the image
        """
        return s3_service.get_file_url(s3_key, expires_in)

    def get_allowed_types(self) -> dict:
        """Get information about allowed image types"""
        return {
            image_type: {
                "max_size_mb": config["max_size_mb"],
                "allowed_formats": config["allowed_formats"],
                "max_dimensions": config["max_dimensions"]
            }
            for image_type, config in self.allowed_types.items()
        }
    
    async def download_image(self, s3_key: str) -> bytes:
        """
        Download image content from S3
        
        Args:
            s3_key: S3 key (path) of the image file
            
        Returns:
            bytes: Image content
        """
        try:
            return await s3_service.download_file(s3_key)
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to download image: {str(e)}",
                error_code=ErrorCodes.S3_DOWNLOAD_FAILED
            )
    
    async def image_exists(self, s3_key: str) -> bool:
        """
        Check if image exists in S3
        
        Args:
            s3_key: S3 key (path) of the image file
            
        Returns:
            bool: True if image exists
        """
        try:
            return await s3_service.file_exists(s3_key)
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to check image existence: {str(e)}",
                error_code=ErrorCodes.S3_DOWNLOAD_FAILED
            )
    
    async def get_image_metadata(self, s3_key: str) -> dict:
        """
        Get image metadata from S3
        
        Args:
            s3_key: S3 key (path) of the image file
            
        Returns:
            dict: Image metadata
        """
        try:
            return await s3_service.get_file_metadata(s3_key)
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to get image metadata: {str(e)}",
                error_code=ErrorCodes.S3_DOWNLOAD_FAILED
            )


# Service instance
image_service = ImageService()

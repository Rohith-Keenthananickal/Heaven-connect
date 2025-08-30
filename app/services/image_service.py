import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io
from app.utils.error_handler import create_http_exception
from app.schemas.errors import ErrorCodes


class ImageService:
    def __init__(self):
        # Base upload directory
        self.base_upload_dir = "uploads"
        
        # Allowed image types and their configurations
        self.allowed_types = {
            "user": {
                "folder": "users",
                "max_size_mb": 5,
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "max_dimensions": (800, 800),
                "quality": 85
            },
            "property": {
                "folder": "properties",
                "max_size_mb": 10,
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "max_dimensions": (1920, 1080),
                "quality": 90
            },
            "room": {
                "folder": "rooms",
                "max_size_mb": 8,
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "max_dimensions": (1600, 1200),
                "quality": 90
            },
            "document": {
                "folder": "documents",
                "max_size_mb": 15,
                "allowed_formats": ["jpg", "jpeg", "png", "pdf"],
                "max_dimensions": (1200, 1600),
                "quality": 85
            },
            "bank": {
                "folder": "bank_documents",
                "max_size_mb": 8,
                "allowed_formats": ["jpg", "jpeg", "png", "pdf"],
                "max_dimensions": (1200, 1600),
                "quality": 85
            },
            "profile": {
                "folder": "profiles",
                "max_size_mb": 3,
                "allowed_formats": ["jpg", "jpeg", "png", "webp"],
                "max_dimensions": (400, 400),
                "quality": 80
            }
        }
        
        # Create base upload directory if it doesn't exist
        os.makedirs(self.base_upload_dir, exist_ok=True)
        
        # Create subdirectories for each type
        for config in self.allowed_types.values():
            os.makedirs(os.path.join(self.base_upload_dir, config["folder"]), exist_ok=True)

    async def upload_image(self, file: UploadFile, image_type: str, user_id: Optional[int] = None) -> dict:
        """
        Upload and process an image file
        
        Args:
            file: The uploaded file
            image_type: Type of image (user, property, room, etc.)
            user_id: Optional user ID for user-specific uploads
            
        Returns:
            dict: Contains file_path, file_name, file_size, and metadata
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
            
            # Determine upload path
            upload_path = self._get_upload_path(image_type, unique_filename, user_id)
            
            # Process and save image
            file_info = await self._process_and_save_image(file, upload_path, config)
            
            # Return file information
            return {
                "file_path": file_info["file_path"],
                "file_name": file_info["file_name"],
                "file_size": file_info["file_size"],
                "file_type": file_extension.lower(),
                "image_type": image_type,
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

    async def upload_multiple_images(self, files: List[UploadFile], image_type: str, user_id: Optional[int] = None) -> List[dict]:
        """
        Upload multiple images of the same type
        
        Args:
            files: List of uploaded files
            image_type: Type of image
            user_id: Optional user ID for user-specific uploads
            
        Returns:
            List of upload results
        """
        results = []
        for file in files:
            try:
                result = await self.upload_image(file, image_type, user_id)
                results.append(result)
            except Exception as e:
                # Log error but continue with other files
                results.append({
                    "error": str(e),
                    "file_name": file.filename,
                    "success": False
                })
        
        return results

    async def delete_image(self, file_path: str) -> bool:
        """
        Delete an uploaded image file
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
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

    def _get_upload_path(self, image_type: str, filename: str, user_id: Optional[int] = None) -> str:
        """Generate upload path for the image"""
        config = self.allowed_types[image_type]
        folder = config["folder"]
        
        if user_id and image_type in ["user", "profile"]:
            # User-specific folder structure
            user_folder = os.path.join(folder, str(user_id))
            os.makedirs(os.path.join(self.base_upload_dir, user_folder), exist_ok=True)
            return os.path.join(self.base_upload_dir, user_folder, filename)
        else:
            # General folder structure
            return os.path.join(self.base_upload_dir, folder, filename)

    async def _process_and_save_image(self, file: UploadFile, upload_path: str, config: dict) -> dict:
        """Process and save the image file"""
        try:
            content = await file.read()
            
            # For PDFs, save directly
            if file.filename.lower().endswith('.pdf'):
                with open(upload_path, "wb") as f:
                    f.write(content)
                
                return {
                    "file_path": upload_path,
                    "file_name": os.path.basename(upload_path),
                    "file_size": len(content),
                    "metadata": {"type": "pdf"}
                }
            
            # For images, process and optimize
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if dimensions exceed maximum
            if image.size[0] > config["max_dimensions"][0] or image.size[1] > config["max_dimensions"][1]:
                image.thumbnail(config["max_dimensions"], Image.Resampling.LANCZOS)
            
            # Save optimized image
            if upload_path.lower().endswith('.webp'):
                image.save(upload_path, 'WEBP', quality=config["quality"])
            else:
                image.save(upload_path, 'JPEG', quality=config["quality"])
            
            return {
                "file_path": upload_path,
                "file_name": os.path.basename(upload_path),
                "file_size": os.path.getsize(upload_path),
                "metadata": {
                    "dimensions": image.size,
                    "format": image.format,
                    "mode": image.mode
                }
            }
            
        except Exception as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to process image: {str(e)}",
                error_code=ErrorCodes.IMAGE_PROCESSING_FAILED
            )

    def get_image_url(self, file_path: str, base_url: str = "") -> str:
        """
        Generate public URL for the uploaded image
        
        Args:
            file_path: Path to the image file
            base_url: Base URL of your application
            
        Returns:
            str: Public URL for the image
        """
        if not base_url:
            base_url = "http://localhost:8000"
        
        # Convert file path to URL path
        url_path = file_path.replace("\\", "/").replace("uploads/", "static/uploads/")
        return f"{base_url}/{url_path}"

    def get_allowed_types(self) -> dict:
        """Get information about allowed image types"""
        return {
            image_type: {
                "folder": config["folder"],
                "max_size_mb": config["max_size_mb"],
                "allowed_formats": config["allowed_formats"],
                "max_dimensions": config["max_dimensions"]
            }
            for image_type, config in self.allowed_types.items()
        }


# Service instance
image_service = ImageService()

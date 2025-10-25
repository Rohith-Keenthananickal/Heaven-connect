import boto3
import io
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, status
from app.core.config import settings
from app.utils.error_handler import create_http_exception
from app.schemas.errors import ErrorCodes


class S3Service:
    def __init__(self):
        """Initialize S3 service with configuration from settings"""
        self.bucket_name = settings.S3_BUCKET_NAME
        self.region = settings.AWS_REGION
        self.s3_client = None
        self.is_available = False
        
        # Check if S3 is configured
        if not self._is_s3_configured():
            print("Warning: S3 not configured. File uploads will be disabled.")
            return
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.region,
                endpoint_url=settings.S3_ENDPOINT_URL if settings.S3_ENDPOINT_URL else None,
                use_ssl=settings.S3_USE_SSL,
                config=boto3.session.Config(signature_version=settings.S3_SIGNATURE_VERSION)
            )
            
            # Test connection by checking if bucket exists
            self._verify_bucket_exists()
            self.is_available = True
            print(f"S3 service initialized successfully with bucket: {self.bucket_name}")
            
        except NoCredentialsError:
            print("Warning: AWS credentials not found. S3 service disabled.")
        except Exception as e:
            print(f"Warning: Failed to initialize S3 client: {str(e)}. S3 service disabled.")
    
    def _is_s3_configured(self) -> bool:
        """Check if S3 is properly configured"""
        return (
            settings.AWS_ACCESS_KEY_ID and 
            settings.AWS_SECRET_ACCESS_KEY and 
            settings.S3_BUCKET_NAME and
            settings.AWS_REGION
        )

    def _verify_bucket_exists(self):
        """Verify that the S3 bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"Warning: S3 bucket '{self.bucket_name}' not found. S3 service disabled.")
                self.is_available = False
                return
            elif error_code == '403':
                print(f"Warning: Access denied to S3 bucket '{self.bucket_name}'. S3 service disabled.")
                print("Please check your AWS credentials and IAM permissions.")
                self.is_available = False
                return
            else:
                print(f"Warning: Error accessing S3 bucket: {str(e)}. S3 service disabled.")
                self.is_available = False
                return

    async def upload_file(
        self, 
        file_content: bytes, 
        s3_key: str, 
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file content to S3
        
        Args:
            file_content: File content as bytes
            s3_key: S3 object key (path)
            content_type: MIME type of the file
            metadata: Optional metadata to attach to the object
            
        Returns:
            Dict containing upload information
        """
        if not self.is_available:
            raise create_http_exception(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="S3 service is not available",
                error_code=ErrorCodes.S3_CONNECTION_FAILED
            )
        
        try:
            extra_args = {
                'ContentType': content_type
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                **extra_args
            )
            
            return {
                "s3_key": s3_key,
                "bucket": self.bucket_name,
                "content_type": content_type,
                "size": len(file_content),
                "metadata": metadata or {}
            }
            
        except ClientError as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to upload file to S3: {str(e)}",
                error_code=ErrorCodes.S3_UPLOAD_FAILED
            )

    async def download_file(self, s3_key: str) -> bytes:
        """
        Download file content from S3
        
        Args:
            s3_key: S3 object key (path)
            
        Returns:
            File content as bytes
        """
        if not self.is_available:
            raise create_http_exception(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="S3 service is not available",
                error_code=ErrorCodes.S3_CONNECTION_FAILED
            )
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message=f"File not found: {s3_key}",
                    error_code=ErrorCodes.NOT_FOUND
                )
            else:
                raise create_http_exception(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Failed to download file from S3: {str(e)}",
                    error_code=ErrorCodes.S3_DOWNLOAD_FAILED
                )

    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3
        
        Args:
            s3_key: S3 object key (path)
            
        Returns:
            True if deleted successfully
        """
        if not self.is_available:
            raise create_http_exception(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="S3 service is not available",
                error_code=ErrorCodes.S3_CONNECTION_FAILED
            )
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
            
        except ClientError as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to delete file from S3: {str(e)}",
                error_code=ErrorCodes.S3_DELETE_FAILED
            )

    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned URL for file access
        
        Args:
            s3_key: S3 object key (path)
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL for file access
        """
        if not self.is_available:
            raise create_http_exception(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="S3 service is not available",
                error_code=ErrorCodes.S3_CONNECTION_FAILED
            )
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
            
        except ClientError as e:
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to generate file URL: {str(e)}",
                error_code=ErrorCodes.S3_DOWNLOAD_FAILED
            )

    def get_public_url(self, s3_key: str) -> str:
        """
        Generate a public URL for file access (for public files)
        
        Args:
            s3_key: S3 object key (path)
            
        Returns:
            Public URL for file access
        """
        if settings.S3_ENDPOINT_URL:
            # Custom S3-compatible service
            return f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{self.bucket_name}/{s3_key}"
        else:
            # Standard AWS S3
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

    async def file_exists(self, s3_key: str) -> bool:
        """
        Check if file exists in S3
        
        Args:
            s3_key: S3 object key (path)
            
        Returns:
            True if file exists, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise create_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Error checking file existence: {str(e)}",
                error_code=ErrorCodes.S3_DOWNLOAD_FAILED
            )

    async def get_file_metadata(self, s3_key: str) -> Dict[str, Any]:
        """
        Get file metadata from S3
        
        Args:
            s3_key: S3 object key (path)
            
        Returns:
            File metadata dictionary
        """
        if not self.is_available:
            raise create_http_exception(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="S3 service is not available",
                error_code=ErrorCodes.S3_CONNECTION_FAILED
            )
        
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                "content_type": response.get('ContentType'),
                "content_length": response.get('ContentLength'),
                "last_modified": response.get('LastModified'),
                "etag": response.get('ETag'),
                "metadata": response.get('Metadata', {})
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise create_http_exception(
                    status_code=status.HTTP_404_NOT_FOUND,
                    message=f"File not found: {s3_key}",
                    error_code=ErrorCodes.NOT_FOUND
                )
            else:
                raise create_http_exception(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Failed to get file metadata: {str(e)}",
                    error_code=ErrorCodes.S3_DOWNLOAD_FAILED
                )

    def generate_s3_key(self, image_type: str, filename: str) -> str:
        """
        Generate S3 key (path) for file storage
        
        Args:
            image_type: Type of image (user, property, room, etc.)
            filename: Generated filename
            
        Returns:
            S3 key (path) for the file
        """
        # Simple folder structure based on image type only
        return f"{image_type}s/{filename}"


    def is_s3_available(self) -> bool:
        """Check if S3 service is available"""
        return self.is_available


# Service instance
s3_service = S3Service()

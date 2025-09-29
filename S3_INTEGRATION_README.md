# S3 Integration for Heaven Connect Image Service

This document describes the S3 integration implemented for the Heaven Connect image service, replacing local file storage with Amazon S3 or S3-compatible storage.

## Overview

The image service has been updated to use S3 for storing and retrieving images instead of local file storage. This provides better scalability, reliability, and performance for image handling.

## Features

- ✅ **S3 Upload**: Upload images directly to S3 with automatic processing and optimization
- ✅ **S3 Download**: Download images from S3
- ✅ **S3 Delete**: Delete images from S3
- ✅ **URL Generation**: Generate public URLs and presigned URLs for images
- ✅ **File Existence Check**: Check if files exist in S3
- ✅ **Metadata Retrieval**: Get file metadata from S3
- ✅ **Error Handling**: Comprehensive error handling for S3 operations
- ✅ **S3-Compatible**: Works with AWS S3 and S3-compatible services (MinIO, DigitalOcean Spaces, etc.)

## Configuration

### Environment Variables

Add these environment variables to your `.env` file:

```bash
# AWS S3 Settings
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
S3_ENDPOINT_URL=  # Optional, for custom S3-compatible services
S3_USE_SSL=True
S3_SIGNATURE_VERSION=s3v4
```

### S3 Bucket Setup

1. Create an S3 bucket in your AWS account
2. Configure bucket permissions for public read access (for public URLs)
3. Set up CORS policy if needed for web applications
4. Ensure your AWS credentials have the following permissions:
   - `s3:PutObject`
   - `s3:GetObject`
   - `s3:DeleteObject`
   - `s3:HeadObject`
   - `s3:ListBucket`

## File Structure

```
app/services/
├── s3_service.py          # S3 service for direct S3 operations
├── image_service.py       # Updated image service using S3
└── ...

app/core/
└── config.py              # Updated with S3 configuration

app/schemas/
└── errors.py              # Updated with S3 error codes
```

## API Changes

### ImageService Methods

The `ImageService` class has been updated with the following changes:

#### Upload Response Format

**Before (Local Storage):**
```json
{
  "file_path": "uploads/users/123/image.jpg",
  "file_name": "image.jpg",
  "file_size": 245760,
  "file_type": "jpg",
  "image_type": "user",
  "uploaded_at": "2024-12-01T14:30:22.123456",
  "metadata": {...}
}
```

**After (S3 Storage):**
```json
{
  "s3_key": "users/123/20241201_143022_a1b2c3d4.jpg",
  "file_name": "20241201_143022_a1b2c3d4.jpg",
  "file_size": 245760,
  "file_type": "jpg",
  "image_type": "user",
  "url": "https://your-bucket.s3.us-east-1.amazonaws.com/users/123/20241201_143022_a1b2c3d4.jpg",
  "uploaded_at": "2024-12-01T14:30:22.123456",
  "metadata": {...}
}
```

#### New Methods

- `download_image(s3_key: str) -> bytes`: Download image content from S3
- `image_exists(s3_key: str) -> bool`: Check if image exists in S3
- `get_image_metadata(s3_key: str) -> dict`: Get image metadata from S3
- `get_presigned_url(s3_key: str, expires_in: int) -> str`: Generate presigned URL

#### Updated Methods

- `upload_image()`: Now uploads to S3 and returns S3 key and URL
- `delete_image()`: Now deletes from S3 using S3 key
- `get_image_url()`: Now generates S3 public URL

## Usage Examples

### Basic Upload

```python
from fastapi import UploadFile
from app.services.image_service import image_service

# Upload an image
async def upload_user_image(file: UploadFile, user_id: int):
    result = await image_service.upload_image(
        file=file,
        image_type="user",
        user_id=user_id
    )
    
    # Result contains:
    # - s3_key: S3 object key
    # - url: Public URL for the image
    # - file_name: Generated filename
    # - file_size: File size in bytes
    # - metadata: Image metadata
    
    return result
```

### Generate URLs

```python
# Get public URL (no expiration)
public_url = image_service.get_image_url(s3_key)

# Get presigned URL (with expiration)
presigned_url = image_service.get_presigned_url(s3_key, expires_in=3600)
```

### Check File Existence

```python
# Check if file exists in S3
exists = await image_service.image_exists(s3_key)
```

### Download File

```python
# Download file content
file_content = await image_service.download_image(s3_key)
```

### Delete File

```python
# Delete file from S3
success = await image_service.delete_image(s3_key)
```

## S3 Key Structure

Files are stored in S3 with the following key structure:

```
{image_type}s/{user_id}/{filename}     # For user-specific uploads
{image_type}s/{filename}               # For general uploads
```

Examples:
- `users/123/20241201_143022_a1b2c3d4.jpg`
- `properties/20241201_143022_e5f6g7h8.jpg`
- `rooms/20241201_143022_i9j0k1l2.png`

## Error Handling

The integration includes comprehensive error handling for S3 operations:

- `S3_CONNECTION_FAILED`: Failed to connect to S3
- `S3_UPLOAD_FAILED`: Failed to upload file to S3
- `S3_DOWNLOAD_FAILED`: Failed to download file from S3
- `S3_DELETE_FAILED`: Failed to delete file from S3
- `S3_BUCKET_NOT_FOUND`: S3 bucket not found
- `S3_ACCESS_DENIED`: Access denied to S3 bucket
- `S3_INVALID_CREDENTIALS`: Invalid AWS credentials

## Migration from Local Storage

If you're migrating from local storage to S3:

1. **Update Database Records**: Update any database records that store file paths to store S3 keys instead
2. **Update API Responses**: Update API responses to return S3 URLs instead of local file paths
3. **Update Frontend**: Update frontend code to use S3 URLs for displaying images
4. **Migrate Existing Files**: Consider migrating existing local files to S3

## Testing

Run the example script to test the S3 integration:

```bash
python s3_integration_example.py
```

Make sure to set up your environment variables before running the test.

## Dependencies

The S3 integration requires the following additional dependency:

```
boto3==1.35.36
```

This is automatically added to `requirements.txt`.

## Security Considerations

1. **Access Control**: Ensure your S3 bucket has appropriate access controls
2. **Credentials**: Store AWS credentials securely (use IAM roles in production)
3. **CORS**: Configure CORS policy if serving images to web applications
4. **Presigned URLs**: Use presigned URLs for sensitive images that shouldn't be publicly accessible

## Performance Considerations

1. **CDN**: Consider using CloudFront or similar CDN for better performance
2. **Image Optimization**: Images are automatically optimized before upload
3. **Caching**: S3 provides built-in caching capabilities
4. **Concurrent Uploads**: The service supports concurrent uploads for multiple images

## Troubleshooting

### Common Issues

1. **Credentials Not Found**: Ensure AWS credentials are properly configured
2. **Bucket Not Found**: Verify the bucket name and region are correct
3. **Access Denied**: Check IAM permissions for S3 operations
4. **CORS Issues**: Configure CORS policy for web applications

### Debug Mode

Enable debug mode in your environment to see detailed error messages:

```bash
DEBUG=True
```

## Support

For issues related to S3 integration, check:

1. AWS CloudTrail logs for S3 API calls
2. Application logs for detailed error messages
3. S3 bucket access logs
4. IAM policy permissions

## Future Enhancements

Potential future enhancements:

- [ ] Automatic image resizing for different sizes
- [ ] Image format conversion (WebP optimization)
- [ ] Batch operations for multiple files
- [ ] Image processing pipeline with AWS Lambda
- [ ] Integration with CloudFront for CDN
- [ ] Backup and versioning strategies

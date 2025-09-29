# S3 Image Upload API Documentation

This document describes the updated image upload APIs that now use S3 storage instead of local file storage.

## Base URL
```
http://localhost:8000/images
```

## Authentication
All endpoints require proper authentication (if configured in your application).

## API Endpoints

### 1. Upload Single Image

**POST** `/images/upload`

Upload a single image file to S3.

#### Request
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` (file, required): Image file to upload
  - `image_type` (string, required): Type of image (`user`, `property`, `room`, `document`, `bank`, `profile`)

#### Response
```json
{
  "status": "success",
  "message": "Image uploaded successfully",
  "data": {
    "s3_key": "users/20241201_143022_a1b2c3d4.jpg",
    "file_name": "20241201_143022_a1b2c3d4.jpg",
    "file_size": 245760,
    "file_type": "jpg",
    "image_type": "user",
    "url": "https://your-bucket.s3.us-east-1.amazonaws.com/users/20241201_143022_a1b2c3d4.jpg",
    "uploaded_at": "2024-12-01T14:30:22.123456",
    "metadata": {
      "dimensions": "800x600",
      "format": "JPEG",
      "mode": "RGB",
      "original_filename": "profile.jpg"
    }
  }
}
```

#### Example cURL
```bash
curl -X POST "http://localhost:8000/images/upload" \
  -F "file=@profile.jpg" \
  -F "image_type=user"
```

### 2. Upload Multiple Images

**POST** `/images/upload/multiple`

Upload multiple image files of the same type to S3.

#### Request
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `files` (array of files, required): Multiple image files to upload (max 10)
  - `image_type` (string, required): Type of image

#### Response
```json
{
  "status": "success",
  "message": "Uploaded 3 out of 3 images successfully",
  "data": [
    {
      "s3_key": "properties/20241201_143022_a1b2c3d4.jpg",
      "file_name": "20241201_143022_a1b2c3d4.jpg",
      "file_size": 245760,
      "file_type": "jpg",
      "image_type": "property",
      "url": "https://your-bucket.s3.us-east-1.amazonaws.com/properties/20241201_143022_a1b2c3d4.jpg",
      "uploaded_at": "2024-12-01T14:30:22.123456",
      "metadata": {...}
    }
  ],
  "total_uploaded": 3,
  "total_failed": 0
}
```

### 3. Get Image Types

**GET** `/images/types`

Get information about allowed image types and their configurations.

#### Response
```json
{
  "status": "success",
  "message": "Image types retrieved successfully",
  "data": {
    "user": {
      "max_size_mb": 5,
      "allowed_formats": ["jpg", "jpeg", "png", "webp"],
      "max_dimensions": [800, 800]
    },
    "property": {
      "max_size_mb": 10,
      "allowed_formats": ["jpg", "jpeg", "png", "webp"],
      "max_dimensions": [1920, 1080]
    }
  }
}
```

### 4. Delete Image

**DELETE** `/images/delete`

Delete an image file from S3.

#### Request
- **Parameters**:
  - `s3_key` (string, required): S3 key (path) of the file to delete

#### Response
```json
{
  "status": "success",
  "message": "Image deleted successfully",
  "data": {
    "deleted": true,
    "s3_key": "users/123/20241201_143022_a1b2c3d4.jpg"
  }
}
```

#### Example cURL
```bash
curl -X DELETE "http://localhost:8000/images/delete?s3_key=users/123/20241201_143022_a1b2c3d4.jpg"
```

### 5. Get Image URL

**GET** `/images/url/{s3_key}`

Get public and presigned URLs for an image.

#### Request
- **Parameters**:
  - `s3_key` (string, required): S3 key (path) of the image file
  - `expires_in` (integer, optional): URL expiration time in seconds (60-86400, default: 3600)

#### Response
```json
{
  "status": "success",
  "data": {
    "s3_key": "users/20241201_143022_a1b2c3d4.jpg",
    "public_url": "https://your-bucket.s3.us-east-1.amazonaws.com/users/123/20241201_143022_a1b2c3d4.jpg",
    "presigned_url": "https://your-bucket.s3.us-east-1.amazonaws.com/users/123/20241201_143022_a1b2c3d4.jpg?AWSAccessKeyId=...",
    "expires_in": 3600
  }
}
```

### 6. Download Image

**GET** `/images/download/{s3_key}`

Download image content from S3.

#### Request
- **Parameters**:
  - `s3_key` (string, required): S3 key (path) of the image file

#### Response
- **Content-Type**: Image content type (e.g., `image/jpeg`, `image/png`)
- **Content-Disposition**: `attachment; filename=image.jpg`
- **Body**: Binary image content

### 7. Check Image Exists

**GET** `/images/exists/{s3_key}`

Check if an image exists in S3.

#### Request
- **Parameters**:
  - `s3_key` (string, required): S3 key (path) of the image file

#### Response
```json
{
  "status": "success",
  "data": {
    "s3_key": "users/20241201_143022_a1b2c3d4.jpg",
    "exists": true
  }
}
```

### 8. Get Image Metadata

**GET** `/images/metadata/{s3_key}`

Get image metadata from S3.

#### Request
- **Parameters**:
  - `s3_key` (string, required): S3 key (path) of the image file

#### Response
```json
{
  "status": "success",
  "data": {
    "s3_key": "users/20241201_143022_a1b2c3d4.jpg",
    "metadata": {
      "content_type": "image/jpeg",
      "content_length": 245760,
      "last_modified": "2024-12-01T14:30:22.000Z",
      "etag": "\"d41d8cd98f00b204e9800998ecf8427e\"",
      "metadata": {
        "dimensions": "800x600",
        "format": "JPEG",
        "mode": "RGB",
        "original_filename": "profile.jpg"
      }
    }
  }
}
```

## Image Types and Configurations

| Type | Max Size | Allowed Formats | Max Dimensions | Quality |
|------|----------|-----------------|----------------|---------|
| user | 5 MB | jpg, jpeg, png, webp | 800x800 | 85% |
| property | 10 MB | jpg, jpeg, png, webp | 1920x1080 | 90% |
| room | 8 MB | jpg, jpeg, png, webp | 1600x1200 | 90% |
| document | 15 MB | jpg, jpeg, png, pdf | 1200x1600 | 85% |
| bank | 8 MB | jpg, jpeg, png, pdf | 1200x1600 | 85% |
| profile | 3 MB | jpg, jpeg, png, webp | 400x400 | 80% |

## S3 Key Structure

Files are stored in S3 with the following key structure:

```
{image_type}s/{filename}
```

Examples:
- `users/20241201_143022_a1b2c3d4.jpg`
- `properties/20241201_143022_e5f6g7h8.jpg`
- `rooms/20241201_143022_i9j0k1l2.png`

## Error Responses

All endpoints return consistent error responses:

```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-12-01T14:30:22.123456",
  "path": "/images/upload",
  "method": "POST",
  "details": null,
  "trace_id": "unique-trace-id"
}
```

### Common Error Codes

- `INVALID_IMAGE_TYPE`: Invalid image type specified
- `INVALID_FILE_FORMAT`: File format not allowed
- `FILE_TOO_LARGE`: File size exceeds maximum allowed
- `S3_UPLOAD_FAILED`: Failed to upload to S3
- `S3_DOWNLOAD_FAILED`: Failed to download from S3
- `S3_DELETE_FAILED`: Failed to delete from S3
- `S3_CONNECTION_FAILED`: Failed to connect to S3

## Usage Examples

### Frontend JavaScript

```javascript
// Upload single image
const uploadImage = async (file, imageType) => {
const formData = new FormData();
formData.append('file', file);
formData.append('image_type', imageType);

const response = await fetch('/images/upload', {
  method: 'POST',
  body: formData
});

  return await response.json();
};

// Get image URL
const getImageUrl = async (s3Key) => {
  const response = await fetch(`/images/url/${s3Key}`);
  const data = await response.json();
  return data.data.public_url;
};

// Delete image
const deleteImage = async (s3Key) => {
  const response = await fetch(`/images/delete?s3_key=${s3Key}`, {
    method: 'DELETE'
  });
  return await response.json();
};
```

### Python Client

```python
import requests

# Upload image
def upload_image(file_path, image_type):
    url = "http://localhost:8000/images/upload"
    files = {"file": open(file_path, "rb")}
    data = {"image_type": image_type}
    
    response = requests.post(url, files=files, data=data)
    return response.json()

# Get image URL
def get_image_url(s3_key):
    url = f"http://localhost:8000/images/url/{s3_key}"
    response = requests.get(url)
    return response.json()["data"]["public_url"]

# Delete image
def delete_image(s3_key):
    url = "http://localhost:8000/images/delete"
    params = {"s3_key": s3_key}
    response = requests.delete(url, params=params)
    return response.json()
```

## Migration Notes

If you're migrating from local storage to S3:

1. **Database Updates**: Update any database records that store `file_path` to store `s3_key` instead
2. **API Responses**: Update frontend code to use `s3_key` and `url` fields instead of `file_path`
3. **URL Generation**: Use the new URL generation endpoints instead of local file serving
4. **File Operations**: Use S3-specific endpoints for file operations

## Security Considerations

1. **Access Control**: Ensure your S3 bucket has appropriate access controls
2. **CORS**: Configure CORS policy for web applications
3. **Presigned URLs**: Use presigned URLs for sensitive images
4. **File Validation**: The API validates file types, sizes, and dimensions before upload

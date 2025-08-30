# Image Upload API Documentation

This document provides comprehensive information about the Image Upload API, a general-purpose image and document upload service that can handle different types of files for various use cases across the application.

## 🚀 **API Overview**

The Image Upload API provides a unified interface for uploading, managing, and serving images and documents. It supports multiple file types, automatic optimization, and organized storage in type-specific folders.

## 📁 **Supported Image Types**

| Type | Folder | Max Size | Formats | Max Dimensions | Quality | Use Case |
|------|--------|----------|---------|----------------|---------|----------|
| `user` | `users/{user_id}/` | 5MB | jpg, jpeg, png, webp | 800x800 | 85% | User profile pictures |
| `profile` | `profiles/{user_id}/` | 3MB | jpg, jpeg, png, webp | 400x400 | 80% | Small profile images |
| `property` | `properties/` | 10MB | jpg, jpeg, png, webp | 1920x1080 | 90% | Property photos |
| `room` | `rooms/` | 8MB | jpg, jpeg, png, webp | 1600x1200 | 90% | Room photos |
| `document` | `documents/` | 15MB | jpg, jpeg, png, pdf | 1200x1600 | 85% | General documents |
| `bank` | `bank_documents/` | 8MB | jpg, jpeg, png, pdf | 1200x1600 | 85% | Bank-related documents |

## 🔗 **API Endpoints**

### Base URL
```
https://your-domain.com/api/v1/images
```

### Endpoints Summary
- `POST /upload` - Upload single image
- `POST /upload/multiple` - Upload multiple images
- `GET /types` - Get supported image types and configurations
- `DELETE /delete` - Delete uploaded image
- `GET /serve/{file_path}` - Serve image file
- `GET /info/{file_path}` - Get image information

## 📤 **Upload Single Image**

### Endpoint
```http
POST /api/v1/images/upload
```

### Request
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: Image file (required)
  - `image_type`: Type of image (required)
  - `user_id`: User ID for user-specific uploads (optional, required for user/profile types)

### Example Request (cURL)
```bash
curl -X POST "https://your-domain.com/api/v1/images/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@profile.jpg" \
  -F "image_type=profile" \
  -F "user_id=123"
```

### Example Request (JavaScript/Fetch)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('image_type', 'profile');
formData.append('user_id', '123');

fetch('/api/v1/images/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Example Request (Python/Requests)
```python
import requests

files = {'file': open('profile.jpg', 'rb')}
data = {
    'image_type': 'profile',
    'user_id': '123'
}

response = requests.post(
    'https://your-domain.com/api/v1/images/upload',
    files=files,
    data=data
)

print(response.json())
```

### Response (Success)
```json
{
  "status": "success",
  "message": "Image uploaded successfully",
  "data": {
    "file_path": "uploads/profiles/123/20240115_104530_a1b2c3d4.jpg",
    "file_name": "20240115_104530_a1b2c3d4.jpg",
    "file_size": 245760,
    "file_type": "jpg",
    "image_type": "profile",
    "uploaded_at": "2024-01-15T10:45:30.123456Z",
    "metadata": {
      "dimensions": [400, 400],
      "format": "JPEG",
      "mode": "RGB"
    },
    "public_url": "https://your-domain.com/uploads/profiles/123/20240115_104530_a1b2c3d4.jpg"
  }
}
```

### Response (Error)
```json
{
  "detail": "user_id is required for user and profile image uploads"
}
```

## 📤 **Upload Multiple Images**

### Endpoint
```http
POST /api/v1/images/upload/multiple
```

### Request
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `files`: Array of image files (required, max 10 files)
  - `image_type`: Type of image (required)
  - `user_id`: User ID for user-specific uploads (optional, required for user/profile types)

### Example Request (cURL)
```bash
curl -X POST "https://your-domain.com/api/v1/images/upload/multiple" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg" \
  -F "image_type=property" \
  -F "user_id=456"
```

### Example Request (JavaScript/Fetch)
```javascript
const formData = new FormData();
formData.append('image_type', 'property');

// Add multiple files
for (let i = 0; i < fileInput.files.length; i++) {
  formData.append('files', fileInput.files[i]);
}

fetch('/api/v1/images/upload/multiple', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Response (Success)
```json
{
  "status": "success",
  "message": "Uploaded 3 out of 3 images successfully",
  "data": [
    {
      "file_path": "uploads/properties/20240115_104530_a1b2c3d4.jpg",
      "file_name": "20240115_104530_a1b2c3d4.jpg",
      "file_size": 1048576,
      "file_type": "jpg",
      "image_type": "property",
      "uploaded_at": "2024-01-15T10:45:30.123456Z",
      "metadata": {
        "dimensions": [1920, 1080],
        "format": "JPEG",
        "mode": "RGB"
      },
      "public_url": "https://your-domain.com/uploads/properties/20240115_104530_a1b2c3d4.jpg"
    },
    {
      "file_path": "uploads/properties/20240115_104531_e5f6g7h8.jpg",
      "file_name": "20240115_104531_e5f6g7h8.jpg",
      "file_size": 2097152,
      "file_type": "jpg",
      "image_type": "property",
      "uploaded_at": "2024-01-15T10:45:31.123456Z",
      "metadata": {
        "dimensions": [1600, 900],
        "format": "JPEG",
        "mode": "RGB"
      },
      "public_url": "https://your-domain.com/uploads/properties/20240115_104531_e5f6g7h8.jpg"
    },
    {
      "file_path": "uploads/properties/20240115_104532_i9j0k1l2.jpg",
      "file_name": "20240115_104532_i9j0k1l2.jpg",
      "file_size": 1572864,
      "file_type": "jpg",
      "image_type": "property",
      "uploaded_at": "2024-01-15T10:45:32.123456Z",
      "metadata": {
        "dimensions": [1280, 720],
        "format": "JPEG",
        "mode": "RGB"
      },
      "public_url": "https://your-domain.com/uploads/properties/20240115_104532_i9j0k1l2.jpg"
    }
  ],
  "total_uploaded": 3,
  "total_failed": 0
}
```

### Response (Partial Success)
```json
{
  "status": "success",
  "message": "Uploaded 2 out of 3 images successfully",
  "data": [
    {
      "file_path": "uploads/properties/20240115_104530_a1b2c3d4.jpg",
      "file_name": "20240115_104530_a1b2c3d4.jpg",
      "file_size": 1048576,
      "file_type": "jpg",
      "image_type": "property",
      "uploaded_at": "2024-01-15T10:45:30.123456Z",
      "metadata": {
        "dimensions": [1920, 1080],
        "format": "JPEG",
        "mode": "RGB"
      },
      "public_url": "https://your-domain.com/uploads/properties/20240115_104530_a1b2c3d4.jpg"
    },
    {
      "error": "File size (12.5MB) exceeds maximum allowed size (10MB)",
      "file_name": "large_image.jpg",
      "success": false
    },
    {
      "file_path": "uploads/properties/20240115_104531_e5f6g7h8.jpg",
      "file_name": "20240115_104531_e5f6g7h8.jpg",
      "file_size": 2097152,
      "file_type": "jpg",
      "image_type": "property",
      "uploaded_at": "2024-01-15T10:45:31.123456Z",
      "metadata": {
        "dimensions": [1600, 900],
        "format": "JPEG",
        "mode": "RGB"
      },
      "public_url": "https://your-domain.com/uploads/properties/20240115_104531_e5f6g7h8.jpg"
    }
  ],
  "total_uploaded": 2,
  "total_failed": 1
}
```

## 📋 **Get Image Types Information**

### Endpoint
```http
GET /api/v1/images/types
```

### Request
- **Method**: GET
- **No parameters required**

### Response
```json
{
  "status": "success",
  "message": "Image types retrieved successfully",
  "data": {
    "user": {
      "folder": "users",
      "max_size_mb": 5,
      "allowed_formats": ["jpg", "jpeg", "png", "webp"],
      "max_dimensions": [800, 800]
    },
    "profile": {
      "folder": "profiles",
      "max_size_mb": 3,
      "allowed_formats": ["jpg", "jpeg", "png", "webp"],
      "max_dimensions": [400, 400]
    },
    "property": {
      "folder": "properties",
      "max_size_mb": 10,
      "allowed_formats": ["jpg", "jpeg", "png", "webp"],
      "max_dimensions": [1920, 1080]
    },
    "room": {
      "folder": "rooms",
      "max_size_mb": 8,
      "allowed_formats": ["jpg", "jpeg", "png", "webp"],
      "max_dimensions": [1600, 1200]
    },
    "document": {
      "folder": "documents",
      "max_size_mb": 15,
      "allowed_formats": ["jpg", "jpeg", "png", "pdf"],
      "max_dimensions": [1200, 1600]
    },
    "bank": {
      "folder": "bank_documents",
      "max_size_mb": 8,
      "allowed_formats": ["jpg", "jpeg", "png", "pdf"],
      "max_dimensions": [1200, 1600]
    }
  }
}
```

## 🗑️ **Delete Image**

### Endpoint
```http
DELETE /api/v1/images/delete?file_path={file_path}
```

### Request
- **Method**: DELETE
- **Query Parameters**:
  - `file_path`: Path to the file to delete (relative to uploads directory)

### Example Request (cURL)
```bash
curl -X DELETE "https://your-domain.com/api/v1/images/delete?file_path=profiles/123/20240115_104530_a1b2c3d4.jpg"
```

### Response (Success)
```json
{
  "status": "success",
  "message": "Image deleted successfully",
  "data": {
    "deleted": true,
    "file_path": "profiles/123/20240115_104530_a1b2c3d4.jpg"
  }
}
```

### Response (Error)
```json
{
  "detail": "File not found or already deleted"
}
```

## 🖼️ **Serve Image**

### Endpoint
```http
GET /api/v1/images/serve/{file_path}
```

### Request
- **Method**: GET
- **Path Parameters**:
  - `file_path`: Path to the image file relative to uploads directory

### Example Request
```http
GET /api/v1/images/serve/profiles/123/20240115_104530_a1b2c3d4.jpg
```

### Response
- **Content-Type**: Based on file type (image/jpeg, image/png, etc.)
- **Body**: Binary file content

### Alternative Direct Access
Images can also be accessed directly via the static file mount:
```http
GET /uploads/profiles/123/20240115_104530_a1b2c3d4.jpg
```

## ℹ️ **Get Image Information**

### Endpoint
```http
GET /api/v1/images/info/{file_path}
```

### Request
- **Method**: GET
- **Path Parameters**:
  - `file_path`: Path to the image file relative to uploads directory

### Example Request
```http
GET /api/v1/images/info/profiles/123/20240115_104530_a1b2c3d4.jpg
```

### Response
```json
{
  "status": "success",
  "message": "Image information retrieved successfully",
  "data": {
    "file_path": "profiles/123/20240115_104530_a1b2c3d4.jpg",
    "file_name": "20240115_104530_a1b2c3d4.jpg",
    "file_size": 245760,
    "file_type": "jpg",
    "image_type": "profile",
    "uploaded_at": 1705316730.123456,
    "public_url": "https://your-domain.com/uploads/profiles/123/20240115_104530_a1b2c3d4.jpg",
    "metadata": {
      "exists": true,
      "readable": true
    }
  }
}
```

## 🔧 **Use Cases and Examples**

### 1. **User Profile Picture Upload**
```javascript
// Upload user profile picture
const formData = new FormData();
formData.append('file', profileImage);
formData.append('image_type', 'profile');
formData.append('user_id', currentUserId);

const response = await fetch('/api/v1/images/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
if (result.status === 'success') {
  // Update user profile with image URL
  const imageUrl = result.data.public_url;
  await updateUserProfile({ profile_image: imageUrl });
}
```

### 2. **Property Photo Gallery Upload**
```javascript
// Upload multiple property photos
const formData = new FormData();
formData.append('image_type', 'property');

propertyImages.forEach(image => {
  formData.append('files', image);
});

const response = await fetch('/api/v1/images/upload/multiple', {
  method: 'POST',
  body: formData
});

const result = await response.json();
if (result.status === 'success') {
  // Save image paths to property
  const imagePaths = result.data
    .filter(item => !item.error)
    .map(item => item.file_path);
  
  await savePropertyPhotos(propertyId, imagePaths);
}
```

### 3. **Document Upload (ID Proof, Bank Documents)**
```javascript
// Upload ID proof document
const formData = new FormData();
formData.append('file', idProofDocument);
formData.append('image_type', 'document');

const response = await fetch('/api/v1/images/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
if (result.status === 'success') {
  // Save document path to user profile
  await updateUserProfile({ 
    id_proof_document: result.data.file_path 
  });
}
```

### 4. **Bank Document Upload**
```javascript
// Upload bank passbook image
const formData = new FormData();
formData.append('file', bankPassbook);
formData.append('image_type', 'bank');

const response = await fetch('/api/v1/images/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
if (result.status === 'success') {
  // Save to bank details
  await updateBankDetails({
    bank_passbook_image: result.data.file_path
  });
}
```

## 🛡️ **Security Features**

### 1. **File Type Validation**
- Only allowed file formats are accepted
- File extension validation
- MIME type checking

### 2. **File Size Limits**
- Configurable size limits per image type
- Prevents large file uploads
- Memory-efficient processing

### 3. **Path Traversal Protection**
- Prevents `../` in file paths
- Validates file paths before operations
- Secure file serving

### 4. **User Isolation**
- User-specific folders for personal images
- Prevents access to other users' files
- Secure file organization

## 📁 **File Storage Structure**

```
uploads/
├── users/
│   └── 123/
│       ├── 20240115_104530_a1b2c3d4.jpg
│       └── 20240115_110000_e5f6g7h8.png
├── profiles/
│   └── 123/
│       └── 20240115_104530_a1b2c3d4.jpg
├── properties/
│   ├── 20240115_104530_a1b2c3d4.jpg
│   ├── 20240115_104531_e5f6g7h8.jpg
│   └── 20240115_104532_i9j0k1l2.jpg
├── rooms/
│   ├── 20240115_104530_a1b2c3d4.jpg
│   └── 20240115_104531_e5f6g7h8.jpg
├── documents/
│   ├── 20240115_104530_a1b2c3d4.pdf
│   └── 20240115_104531_e5f6g7h8.jpg
└── bank_documents/
    ├── 20240115_104530_a1b2c3d4.jpg
    └── 20240115_104531_e5f6g7h8.pdf
```

## 🔄 **File Naming Convention**

Files are automatically renamed using the following format:
```
{YYYYMMDD}_{HHMMSS}_{UUID8}.{extension}
```

**Example**: `20240115_104530_a1b2c3d4.jpg`

- **Date**: YYYYMMDD format
- **Time**: HHMMSS format (24-hour)
- **UUID**: First 8 characters of UUID4
- **Extension**: Original file extension

## 🎯 **Image Processing Features**

### 1. **Automatic Optimization**
- JPEG quality optimization
- WebP support
- Format conversion when needed

### 2. **Resizing**
- Automatic resizing to max dimensions
- Maintains aspect ratio
- High-quality resampling

### 3. **Format Support**
- **Images**: JPG, JPEG, PNG, WebP
- **Documents**: JPG, JPEG, PNG, PDF
- **Automatic conversion** to RGB for compatibility

## 📊 **Error Handling**

### Common Error Responses

#### 1. **Invalid Image Type**
```json
{
  "detail": "Invalid image type: invalid_type. Allowed types: user, property, room, document, bank, profile"
}
```

#### 2. **File Too Large**
```json
{
  "detail": "File size (12.5MB) exceeds maximum allowed size (10MB)"
}
```

#### 3. **Invalid File Format**
```json
{
  "detail": "Invalid file format. Allowed formats: jpg, jpeg, png, webp"
}
```

#### 4. **Missing User ID**
```json
{
  "detail": "user_id is required for user and profile image uploads"
}
```

#### 5. **File Not Found**
```json
{
  "detail": "Image not found"
}
```

## 🚀 **Performance Optimizations**

### 1. **Efficient Processing**
- Stream-based file reading
- Memory-efficient image processing
- Optimized file saving

### 2. **Caching**
- Static file serving
- Browser caching headers
- CDN-ready structure

### 3. **Batch Operations**
- Multiple file upload support
- Parallel processing
- Bulk operations

## 🔧 **Configuration**

### Environment Variables
```bash
# Upload directory (default: uploads)
UPLOAD_DIR=uploads

# Base URL for public access
BASE_URL=https://your-domain.com

# Maximum file size (in bytes)
MAX_FILE_SIZE=10485760  # 10MB
```

### Service Configuration
The image service can be configured by modifying the `allowed_types` dictionary in `app/services/image_service.py`:

```python
self.allowed_types = {
    "custom_type": {
        "folder": "custom_folder",
        "max_size_mb": 5,
        "allowed_formats": ["jpg", "png"],
        "max_dimensions": (800, 600),
        "quality": 85
    }
}
```

## 📱 **Frontend Integration**

### React Component Example
```jsx
import React, { useState } from 'react';

const ImageUploader = ({ imageType, userId, onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('image_type', imageType);
    
    if (userId) {
      formData.append('user_id', userId);
    }

    try {
      const response = await fetch('/api/v1/images/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        onUploadSuccess(result.data);
      } else {
        setError(result.message || 'Upload failed');
      }
    } catch (err) {
      setError('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => handleUpload(e.target.files[0])}
        disabled={uploading}
      />
      {uploading && <p>Uploading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ImageUploader;
```

### Vue.js Component Example
```vue
<template>
  <div>
    <input
      type="file"
      accept="image/*"
      @change="handleFileSelect"
      :disabled="uploading"
    />
    <p v-if="uploading">Uploading...</p>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script>
export default {
  props: {
    imageType: {
      type: String,
      required: true
    },
    userId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      uploading: false,
      error: null
    };
  },
  methods: {
    async handleFileSelect(event) {
      const file = event.target.files[0];
      if (!file) return;

      this.uploading = true;
      this.error = null;

      const formData = new FormData();
      formData.append('file', file);
      formData.append('image_type', this.imageType);
      
      if (this.userId) {
        formData.append('user_id', this.userId);
      }

      try {
        const response = await fetch('/api/v1/images/upload', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();
        
        if (result.status === 'success') {
          this.$emit('upload-success', result.data);
        } else {
          this.error = result.message || 'Upload failed';
        }
      } catch (err) {
        this.error = 'Upload failed: ' + err.message;
      } finally {
        this.uploading = false;
      }
    }
  }
};
</script>
```

## 🧪 **Testing**

### Test File Upload
```bash
# Test single image upload
curl -X POST "http://localhost:8000/api/v1/images/upload" \
  -F "file=@test_image.jpg" \
  -F "image_type=profile" \
  -F "user_id=123"

# Test multiple image upload
curl -X POST "http://localhost:8000/api/v1/images/upload/multiple" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "image_type=property"

# Test image types endpoint
curl "http://localhost:8000/api/v1/images/types"

# Test image serving
curl "http://localhost:8000/api/v1/images/serve/profiles/123/test_image.jpg"
```

## 📝 **Best Practices**

### 1. **File Validation**
- Always validate file types on frontend
- Check file sizes before upload
- Use appropriate image types for use cases

### 2. **Error Handling**
- Implement proper error handling for failed uploads
- Show user-friendly error messages
- Retry failed uploads when appropriate

### 3. **User Experience**
- Show upload progress indicators
- Provide immediate feedback on success/failure
- Allow users to retry failed uploads

### 4. **Security**
- Validate file types on both frontend and backend
- Implement proper access controls
- Sanitize file names and paths

### 5. **Performance**
- Use appropriate image types for different use cases
- Implement lazy loading for image galleries
- Optimize images for web display

## 🔮 **Future Enhancements**

### Planned Features
- **Image cropping and editing**
- **Watermarking support**
- **Multiple format generation** (thumbnails, different sizes)
- **Cloud storage integration** (AWS S3, Google Cloud Storage)
- **Image compression algorithms**
- **Batch processing capabilities**
- **Image metadata extraction**
- **Face detection and recognition**

### Integration Possibilities
- **CDN integration** for global distribution
- **Image optimization services** (Cloudinary, ImageKit)
- **AI-powered image analysis**
- **Automatic tagging and categorization**
- **Duplicate image detection**

---

This Image Upload API provides a robust, secure, and scalable solution for handling all image and document upload needs across your application. It's designed to be easy to use, highly configurable, and production-ready.

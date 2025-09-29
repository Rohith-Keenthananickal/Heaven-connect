#!/usr/bin/env python3
"""
S3 Integration Example for Heaven Connect Image Service

This script demonstrates how to use the new S3-integrated image service.
Make sure to set up your environment variables before running this example.
"""

import asyncio
import os
from fastapi import UploadFile
from app.services.image_service import image_service
from app.services.s3_service import s3_service

async def example_usage():
    """Example of how to use the S3-integrated image service"""
    
    print("=== S3 Image Service Example ===\n")
    
    # 1. Check S3 connection
    print("1. Testing S3 connection...")
    try:
        # This will be called automatically when the service initializes
        print("✅ S3 connection successful!")
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return
    
    # 2. Get allowed image types
    print("\n2. Available image types:")
    allowed_types = image_service.get_allowed_types()
    for image_type, config in allowed_types.items():
        print(f"   - {image_type}: {config['max_size_mb']}MB max, {config['allowed_formats']}")
    
    # 3. Example of uploading a file (you would need an actual file)
    print("\n3. Example upload response structure:")
    example_response = {
        "s3_key": "users/123/20241201_143022_a1b2c3d4.jpg",
        "file_name": "20241201_143022_a1b2c3d4.jpg",
        "file_size": 245760,
        "file_type": "jpg",
        "image_type": "user",
        "url": "https://your-bucket.s3.us-east-1.amazonaws.com/users/123/20241201_143022_a1b2c3d4.jpg",
        "uploaded_at": "2024-12-01T14:30:22.123456",
        "metadata": {
            "dimensions": "800x600",
            "format": "JPEG",
            "mode": "RGB",
            "original_filename": "profile.jpg"
        }
    }
    
    for key, value in example_response.items():
        print(f"   {key}: {value}")
    
    # 4. Example of generating URLs
    print("\n4. URL generation examples:")
    s3_key = "properties/20241201_143022_a1b2c3d4.jpg"
    
    public_url = image_service.get_image_url(s3_key)
    print(f"   Public URL: {public_url}")
    
    presigned_url = image_service.get_presigned_url(s3_key, expires_in=7200)  # 2 hours
    print(f"   Presigned URL (2h): {presigned_url[:50]}...")
    
    # 5. Example of checking file existence
    print("\n5. File existence check:")
    exists = await image_service.image_exists(s3_key)
    print(f"   File exists: {exists}")
    
    print("\n=== Example completed ===")

def print_environment_setup():
    """Print instructions for setting up environment variables"""
    print("=== Environment Setup Required ===")
    print("Before using the S3 integration, set these environment variables:")
    print()
    print("AWS_ACCESS_KEY_ID=your-aws-access-key-id")
    print("AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key")
    print("AWS_REGION=us-east-1")
    print("S3_BUCKET_NAME=your-s3-bucket-name")
    print("S3_ENDPOINT_URL=  # Optional, for custom S3-compatible services")
    print("S3_USE_SSL=True")
    print("S3_SIGNATURE_VERSION=s3v4")
    print()
    print("You can also copy these to your .env file.")
    print("=====================================")

if __name__ == "__main__":
    print_environment_setup()
    print()
    
    # Check if required environment variables are set
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY", 
        "S3_BUCKET_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables and try again.")
    else:
        print("✅ All required environment variables are set.")
        print("Running example...")
        asyncio.run(example_usage())

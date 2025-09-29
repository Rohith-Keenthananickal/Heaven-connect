#!/usr/bin/env python3
"""
Simple test script to verify the updated image upload API without user_id
"""

import requests
import os
from io import BytesIO
from PIL import Image

def create_test_image():
    """Create a simple test image"""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_upload():
    """Test the simplified upload API"""
    print("=== Testing Simplified Image Upload API ===\n")
    
    # Create test image
    test_image = create_test_image()
    
    # Test data
    files = {"file": ("test_image.jpg", test_image, "image/jpeg")}
    data = {"image_type": "user"}
    
    try:
        # Test upload
        print("1. Testing single image upload...")
        response = requests.post("http://localhost:8000/api/v1/images/upload", 
                               files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Upload successful!")
            print(f"   📁 S3 Key: {result['data']['s3_key']}")
            print(f"   🔗 URL: {result['data']['url']}")
            print(f"   📏 Size: {result['data']['file_size']} bytes")
            print(f"   🏷️  Type: {result['data']['image_type']}")
            
            # Test URL generation
            s3_key = result['data']['s3_key']
            print(f"\n2. Testing URL generation for: {s3_key}")
            
            url_response = requests.get(f"http://localhost:8000/api/v1/images/url/{s3_key}")
            if url_response.status_code == 200:
                url_data = url_response.json()
                print("   ✅ URL generation successful!")
                print(f"   🔗 Public URL: {url_data['data']['public_url']}")
            else:
                print(f"   ❌ URL generation failed: {url_response.text}")
            
            # Test file existence check
            print(f"\n3. Testing file existence check...")
            exists_response = requests.get(f"http://localhost:8000/api/v1/images/exists/{s3_key}")
            if exists_response.status_code == 200:
                exists_data = exists_response.json()
                print(f"   ✅ File exists: {exists_data['data']['exists']}")
            else:
                print(f"   ❌ Existence check failed: {exists_response.text}")
            
            # Test metadata retrieval
            print(f"\n4. Testing metadata retrieval...")
            metadata_response = requests.get(f"http://localhost:8000/api/v1/images/metadata/{s3_key}")
            if metadata_response.status_code == 200:
                metadata_data = metadata_response.json()
                print("   ✅ Metadata retrieval successful!")
                print(f"   📊 Content Type: {metadata_data['data']['metadata']['content_type']}")
                print(f"   📏 Content Length: {metadata_data['data']['metadata']['content_length']}")
            else:
                print(f"   ❌ Metadata retrieval failed: {metadata_response.text}")
            
            # Test deletion
            print(f"\n5. Testing file deletion...")
            delete_response = requests.delete(f"http://localhost:8000/api/v1/images/delete?s3_key={s3_key}")
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                print("   ✅ File deleted successfully!")
                print(f"   🗑️  Deleted: {delete_data['data']['deleted']}")
            else:
                print(f"   ❌ Deletion failed: {delete_response.text}")
                
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

def test_different_image_types():
    """Test upload with different image types"""
    print("\n=== Testing Different Image Types ===\n")
    
    image_types = ["user", "property", "room", "document", "bank", "profile"]
    
    for image_type in image_types:
        print(f"Testing {image_type} upload...")
        
        # Create a fresh image for each upload
        test_image = create_test_image()
        files = {"file": ("test_image.jpg", test_image, "image/jpeg")}
        data = {"image_type": image_type}
        
        try:
            response = requests.post("http://localhost:8000/api/v1/images/upload", 
                                   files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                s3_key = result['data']['s3_key']
                print(f"   ✅ {image_type}: {s3_key}")
                
                # Clean up
                requests.delete(f"http://localhost:8000/api/v1/images/delete?s3_key={s3_key}")
            else:
                print(f"   ❌ {image_type}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ {image_type}: Exception - {e}")

if __name__ == "__main__":
    print("🚀 Starting simplified image upload API tests...")
    print("Make sure your server is running on http://localhost:8000")
    print("=" * 50)
    
    test_upload()
    test_different_image_types()
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")

#!/usr/bin/env python3
"""
S3 Connection Test Script

This script helps debug S3 connection issues.
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

def test_s3_connection():
    """Test S3 connection with detailed error reporting"""
    
    # Load environment variables
    load_dotenv()
    
    print("=== S3 Connection Test ===\n")
    
    # Check environment variables
    print("1. Checking environment variables...")
    required_vars = {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION'),
        'S3_BUCKET_NAME': os.getenv('S3_BUCKET_NAME')
    }
    
    missing_vars = []
    for var, value in required_vars.items():
        if not value:
            missing_vars.append(var)
            print(f"   ❌ {var}: Not set")
        else:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
        return False
    
    print("\n2. Testing S3 client initialization...")
    
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=required_vars['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=required_vars['AWS_SECRET_ACCESS_KEY'],
            region_name=required_vars['AWS_REGION'],
            use_ssl=True,
            config=boto3.session.Config(signature_version='s3v4')
        )
        print("   ✅ S3 client initialized successfully")
        
    except NoCredentialsError:
        print("   ❌ AWS credentials not found")
        return False
    except Exception as e:
        print(f"   ❌ Failed to initialize S3 client: {e}")
        return False
    
    print("\n3. Testing S3 bucket access...")
    
    try:
        # Test bucket access
        bucket_name = required_vars['S3_BUCKET_NAME']
        response = s3_client.head_bucket(Bucket=bucket_name)
        print(f"   ✅ Successfully connected to bucket: {bucket_name}")
        
        # Get bucket location
        location_response = s3_client.get_bucket_location(Bucket=bucket_name)
        bucket_region = location_response.get('LocationConstraint', 'us-east-1')
        if bucket_region is None:
            bucket_region = 'us-east-1'
        
        print(f"   📍 Bucket region: {bucket_region}")
        
        # Check if region matches
        if bucket_region != required_vars['AWS_REGION']:
            print(f"   ⚠️  Warning: Bucket region ({bucket_region}) doesn't match AWS_REGION ({required_vars['AWS_REGION']})")
            print(f"   💡 Consider updating AWS_REGION to: {bucket_region}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"   ❌ Bucket '{bucket_name}' not found")
            print("   💡 Check if the bucket name is correct and exists in your AWS account")
        elif error_code == '403':
            print(f"   ❌ Access denied to bucket '{bucket_name}'")
            print("   💡 Check your AWS credentials and IAM permissions")
        else:
            print(f"   ❌ Error accessing bucket: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    print("\n4. Testing basic S3 operations...")
    
    try:
        # Test list objects (this is a lightweight operation)
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        print("   ✅ Successfully listed objects in bucket")
        
        # Test upload permissions (upload a small test object)
        test_key = "test-connection.txt"
        test_content = "S3 connection test"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print("   ✅ Successfully uploaded test object")
        
        # Clean up test object
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("   ✅ Successfully deleted test object")
        
    except ClientError as e:
        print(f"   ❌ Error during S3 operations: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error during operations: {e}")
        return False
    
    print("\n✅ S3 connection test completed successfully!")
    print("Your S3 configuration is working correctly.")
    return True

def print_troubleshooting_tips():
    """Print troubleshooting tips"""
    print("\n=== Troubleshooting Tips ===")
    print("1. Verify your AWS credentials are correct")
    print("2. Check that the S3 bucket exists in your AWS account")
    print("3. Ensure your AWS user has the following permissions:")
    print("   - s3:GetObject")
    print("   - s3:PutObject")
    print("   - s3:DeleteObject")
    print("   - s3:ListBucket")
    print("   - s3:HeadBucket")
    print("4. Verify the bucket region matches your AWS_REGION setting")
    print("5. Check if your AWS account has any restrictions")
    print("6. Try using AWS CLI to test: aws s3 ls s3://your-bucket-name")

if __name__ == "__main__":
    success = test_s3_connection()
    
    if not success:
        print_troubleshooting_tips()
    else:
        print("\n🎉 Your S3 setup is ready to use!")

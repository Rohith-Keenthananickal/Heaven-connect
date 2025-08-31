#!/usr/bin/env python3
"""
Simple test script to test the login endpoint
"""
import requests
import json

# Test the login endpoint
def test_login():
    url = "http://localhost:8000/api/v1/auth/login/email"
    
    # Test data
    login_data = {
        "email": "rajesh@example.com",
        "password": "password123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Testing login endpoint: {url}")
    print(f"📤 Request data: {json.dumps(login_data, indent=2)}")
    print(f"📋 Headers: {headers}")
    
    try:
        response = requests.post(url, json=login_data, headers=headers)
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            print(f"📋 Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Raw Response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_login()

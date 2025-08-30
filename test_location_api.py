#!/usr/bin/env python3
"""
Test script for the Location API endpoints (Districts and Grama Panchayats)

This script tests the basic functionality of the new location APIs.
Run this after starting your FastAPI server.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

def print_response(response: requests.Response, title: str):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.content else 'No content'}")
    print(f"{'='*50}")

def test_districts_api():
    """Test Districts API endpoints"""
    print("\n🧪 Testing Districts API...")
    
    # Test 1: Create a district
    district_data = {
        "name": "Test District",
        "state": "Test State",
        "code": "TEST",
        "description": "A test district for API testing",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/districts/", json=district_data, headers=HEADERS)
    print_response(response, "Create District")
    
    if response.status_code == 201:
        district_id = response.json()["id"]
        
        # Test 2: Get district by ID
        response = requests.get(f"{BASE_URL}/districts/{district_id}")
        print_response(response, f"Get District by ID ({district_id})")
        
        # Test 3: Update district
        update_data = {
            "description": "Updated description for testing"
        }
        response = requests.put(f"{BASE_URL}/districts/{district_id}", json=update_data, headers=HEADERS)
        print_response(response, f"Update District ({district_id})")
        
        # Test 4: Get all districts
        response = requests.get(f"{BASE_URL}/districts/")
        print_response(response, "Get All Districts")
        
        # Test 5: Get districts by state
        response = requests.get(f"{BASE_URL}/districts/?state=Test State")
        print_response(response, "Get Districts by State")
        
        # Test 6: Search districts
        response = requests.get(f"{BASE_URL}/districts/?search=Test")
        print_response(response, "Search Districts")
        
        return district_id
    else:
        print("❌ Failed to create district, skipping other tests")
        return None

def test_grama_panchayats_api(district_id: int):
    """Test Grama Panchayats API endpoints"""
    print("\n🏛️ Testing Grama Panchayats API...")
    
    # Test 1: Create a grama panchayat
    panchayat_data = {
        "name": "Test Panchayat",
        "district_id": district_id,
        "code": "TPAN",
        "description": "A test grama panchayat for API testing",
        "population": 10000,
        "area_sq_km": 15.5,
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/grama-panchayats/", json=panchayat_data, headers=HEADERS)
    print_response(response, "Create Grama Panchayat")
    
    if response.status_code == 201:
        panchayat_id = response.json()["id"]
        
        # Test 2: Get panchayat by ID
        response = requests.get(f"{BASE_URL}/grama-panchayats/{panchayat_id}")
        print_response(response, f"Get Grama Panchayat by ID ({panchayat_id})")
        
        # Test 3: Update panchayat
        update_data = {
            "population": 12000,
            "description": "Updated description for testing"
        }
        response = requests.put(f"{BASE_URL}/grama-panchayats/{panchayat_id}", json=update_data, headers=HEADERS)
        print_response(response, f"Update Grama Panchayat ({panchayat_id})")
        
        # Test 4: Get all panchayats
        response = requests.get(f"{BASE_URL}/grama-panchayats/")
        print_response(response, "Get All Grama Panchayats")
        
        # Test 5: Get panchayats by district
        response = requests.get(f"{BASE_URL}/grama-panchayats/district/{district_id}")
        print_response(response, f"Get Panchayats by District ({district_id})")
        
        # Test 6: Get panchayat with district info
        response = requests.get(f"{BASE_URL}/grama-panchayats/{panchayat_id}/with-district")
        print_response(response, f"Get Panchayat with District Info ({panchayat_id})")
        
        # Test 7: Search panchayats
        response = requests.get(f"{BASE_URL}/grama-panchayats/?search=Test")
        print_response(response, "Search Grama Panchayats")
        
        # Test 8: Filter by population range
        response = requests.get(f"{BASE_URL}/grama-panchayats/?min_population=5000&max_population=15000")
        print_response(response, "Filter Panchayats by Population Range")
        
        return panchayat_id
    else:
        print("❌ Failed to create grama panchayat, skipping other tests")
        return None

def test_district_with_panchayats(district_id: int):
    """Test getting district with all its panchayats"""
    print("\n🏘️ Testing District with Panchayats...")
    
    response = requests.get(f"{BASE_URL}/districts/{district_id}/with-panchayats")
    print_response(response, f"Get District with Panchayats ({district_id})")

def cleanup_test_data(district_id: int, panchayat_id: int):
    """Clean up test data (soft delete)"""
    print("\n🧹 Cleaning up test data...")
    
    if panchayat_id:
        response = requests.delete(f"{BASE_URL}/grama-panchayats/{panchayat_id}")
        print(f"Deleted panchayat {panchayat_id}: {response.status_code}")
    
    if district_id:
        response = requests.delete(f"{BASE_URL}/districts/{district_id}")
        print(f"Deleted district {district_id}: {response.status_code}")

def main():
    """Main test function"""
    print("🚀 Starting Location API Tests...")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Test Districts API
        district_id = test_districts_api()
        
        if district_id:
            # Test Grama Panchayats API
            panchayat_id = test_grama_panchayats_api(district_id)
            
            if panchayat_id:
                # Test District with Panchayats
                test_district_with_panchayats(district_id)
                
                # Clean up test data
                cleanup_test_data(district_id, panchayat_id)
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Make sure your FastAPI server is running on http://localhost:8000")
        print("Start the server with: python main.py")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()

"""
Test script for the Enquiry API endpoints
"""
import requests
import json
import time
from datetime import date

# Base URL for API
BASE_URL = "http://localhost:8000/api/v1"

def test_create_enquiry():
    """Test creating a new enquiry"""
    print("\n=== Testing Create Enquiry ===")
    
    # Test data
    data = {
        "company_name": "Test Company Ltd",
        "host_name": "John Doe",
        "email": "johndoe@example.com",
        "phone_number": "9876543210",
        "alternate_phone_number": "8765432109",
        "dob": "1990-01-15",
        "gender": "MALE",
        "id_card_type": "AADHAR",
        "id_card_number": "123456789012"
    }
    
    # Send POST request
    response = requests.post(f"{BASE_URL}/enquiries/", json=data)
    
    # Print response
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("Enquiry created successfully!")
        result = response.json()
        print(f"Enquiry ID: {result['data']['id']}")
        return result['data']['id']
    else:
        print(f"Failed to create enquiry: {response.text}")
        return None

def test_get_enquiry(enquiry_id):
    """Test retrieving a specific enquiry"""
    print("\n=== Testing Get Enquiry ===")
    
    # Send GET request
    response = requests.get(f"{BASE_URL}/enquiries/{enquiry_id}")
    
    # Print response
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Enquiry retrieved successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to retrieve enquiry: {response.text}")

def test_update_enquiry(enquiry_id):
    """Test updating an enquiry"""
    print("\n=== Testing Update Enquiry ===")
    
    # Test data with unique ATP ID based on enquiry ID
    data = {
        "company_name": "Updated Company Name",
        "atp_id": f"ATP-{enquiry_id}-{int(time.time())}"
    }
    
    # Send PUT request
    response = requests.put(f"{BASE_URL}/enquiries/{enquiry_id}", json=data)
    
    # Print response
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Enquiry updated successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to update enquiry: {response.text}")

def test_update_enquiry_status(enquiry_id):
    """Test updating enquiry status"""
    print("\n=== Testing Update Enquiry Status ===")
    
    # Test data
    data = {
        "status": "PROCESSED",
        "remarks": "Enquiry has been processed and will be contacted soon."
    }
    
    # Send PATCH request
    response = requests.patch(f"{BASE_URL}/enquiries/{enquiry_id}/status", json=data)
    
    # Print response
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Enquiry status updated successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to update enquiry status: {response.text}")

def test_list_enquiries():
    """Test listing all enquiries"""
    print("\n=== Testing List Enquiries ===")
    
    # Send GET request
    response = requests.get(f"{BASE_URL}/enquiries/")
    
    # Print response
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Retrieved {len(result['data'])} enquiries")
        print(json.dumps(result, indent=2))
    else:
        print(f"Failed to list enquiries: {response.text}")

def test_search_enquiries():
    """Test searching enquiries"""
    print("\n=== Testing Search Enquiries ===")
    
    # Test data
    data = {
        "page": 1,
        "limit": 10,
        "status": "PROCESSED",
        "host_name": "John"
    }
    
    # Send POST request
    response = requests.post(f"{BASE_URL}/enquiries/search", json=data)
    
    # Print response
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result['data'])} matching enquiries")
        print(json.dumps(result, indent=2))
    else:
        print(f"Failed to search enquiries: {response.text}")

def test_delete_enquiry(enquiry_id):
    """Test deleting an enquiry"""
    print("\n=== Testing Delete Enquiry ===")
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete enquiry {enquiry_id}? (y/n): ")
    if confirm.lower() != 'y':
        print("Delete operation cancelled")
        return
    
    # Send DELETE request
    response = requests.delete(f"{BASE_URL}/enquiries/{enquiry_id}")
    
    # Print response
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Enquiry deleted successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to delete enquiry: {response.text}")

if __name__ == "__main__":
    print("Testing Enquiry API Endpoints")
    print("============================")
    
    # Run tests in sequence
    enquiry_id = test_create_enquiry()
    
    if enquiry_id:
        test_get_enquiry(enquiry_id)
        test_update_enquiry(enquiry_id)
        test_update_enquiry_status(enquiry_id)
        test_list_enquiries()
        test_search_enquiries()
        
        # Optional deletion test
        delete = input("Do you want to test deletion of the created enquiry? (y/n): ")
        if delete.lower() == 'y':
            test_delete_enquiry(enquiry_id)
    
    print("\nTest completed!")

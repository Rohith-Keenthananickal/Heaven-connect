#!/usr/bin/env python3
"""
Test script for the User Search API
This demonstrates how to use the new paginated user search endpoint
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL (adjust as needed)
BASE_URL = "http://localhost:8000/api/v1"

def test_user_search():
    """Test the user search API with various filters"""
    
    # Test 1: Basic search with pagination
    print("=== Test 1: Basic search with pagination ===")
    basic_search = {
        "page": 1,
        "limit": 10,
        "search_query": None,
        "user_type": None,
        "date_filter": None,
        "status": None
    }
    
    response = requests.post(f"{BASE_URL}/users/search", json=basic_search)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total users: {data['pagination']['total']}")
        print(f"Page: {data['pagination']['page']}/{data['pagination']['total_pages']}")
        print(f"Users found: {len(data['data'])}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Search by user type (single)
    print("=== Test 2: Search by user type (HOST) ===")
    host_search = {
        "page": 1,
        "limit": 5,
        "search_query": None,
        "user_type": ["HOST"],
        "date_filter": None,
        "status": ["ACTIVE"]
    }
    
    response = requests.post(f"{BASE_URL}/users/search", json=host_search)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Host users found: {len(data['data'])}")
        for user in data['data']:
            print(f"- {user['full_name']} ({user['user_type']}) - Email: {user['email']} - Status: {user['status']}")
            print(f"  Phone: {user['phone_number']}, DOB: {user['dob']}, Profile: {user['profile_image']}")
            print(f"  Created: {user['created_at']}, Updated: {user['updated_at']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Search with text query
    print("=== Test 3: Search with text query ===")
    text_search = {
        "page": 1,
        "limit": 10,
        "search_query": "john",  # Search for users with "john" in name, email, or phone
        "user_type": None,
        "date_filter": None,
        "status": None
    }
    
    response = requests.post(f"{BASE_URL}/users/search", json=text_search)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Users matching 'john': {len(data['data'])}")
        for user in data['data']:
            print(f"- {user['full_name']} ({user['email']}) - Phone: {user['phone_number']} - Status: {user['status']}")
            print(f"  DOB: {user['dob']}, Profile: {user['profile_image']}")
            print(f"  Created: {user['created_at']}, Updated: {user['updated_at']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Search with date filter
    print("=== Test 4: Search with date filter ===")
    
    # Calculate dates (last 30 days)
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    date_search = {
        "page": 1,
        "limit": 10,
        "search_query": None,
        "user_type": None,
        "date_filter": {
            "from_date": int(thirty_days_ago.timestamp() * 1000),  # Convert to milliseconds
            "to_date": int(now.timestamp() * 1000)  # Convert to milliseconds
        },
        "status": None
    }
    
    response = requests.post(f"{BASE_URL}/users/search", json=date_search)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Users created in last 30 days: {len(data['data'])}")
        for user in data['data']:
            created_date = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
            print(f"- {user['full_name']} (created: {created_date.strftime('%Y-%m-%d')}) - Status: {user['status']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 5: Combined search (type + status + text)
    print("=== Test 5: Combined search (type + status + text) ===")
    combined_search = {
        "page": 1,
        "limit": 5,
        "search_query": "a",  # Search for users with "a" in name, email, or phone
        "user_type": ["GUEST"],
        "date_filter": None,
        "status": ["ACTIVE"]
    }
    
    response = requests.post(f"{BASE_URL}/users/search", json=combined_search)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Active guest users with 'a' in details: {len(data['data'])}")
        for user in data['data']:
            print(f"- {user['full_name']} ({user['user_type']}) - {user['email']} - Status: {user['status']}")
            print(f"  Phone: {user['phone_number']}, DOB: {user['dob']}, Profile: {user['profile_image']}")
            print(f"  Created: {user['created_at']}, Updated: {user['updated_at']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 6: Search for blocked users
    print("=== Test 6: Search for blocked users ===")
    blocked_search = {
        "page": 1,
        "limit": 10,
        "search_query": None,
        "user_type": None,
        "date_filter": None,
        "status": ["BLOCKED"]
    }
    
    response = requests.post(f"{BASE_URL}/users/search", json=blocked_search)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Blocked users found: {len(data['data'])}")
        for user in data['data']:
            print(f"- {user['full_name']} ({user['user_type']}) - Status: {user['status']}")
            print(f"  Email: {user['email']}, Phone: {user['phone_number']}, DOB: {user['dob']}")
            print(f"  Profile: {user['profile_image']}, Created: {user['created_at']}, Updated: {user['updated_at']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 7: Search with multiple user types (array)
    print("=== Test 7: Search with multiple user types (HOST + GUEST) ===")
    multi_type_search = {
        "page": 1,
        "limit": 10,
        "search_query": None,
        "user_type": ["HOST", "GUEST"],  # Search for both HOST and GUEST users
        "date_filter": None,
        "status": ["ACTIVE"]
    }
    
    response = requests.post(f"{BASE_URL}/users/search", json=multi_type_search)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"HOST + GUEST users found: {len(data['data'])}")
        for user in data['data']:
            print(f"- {user['full_name']} ({user['user_type']}) - Status: {user['status']}")
            print(f"  Email: {user['email']}, Phone: {user['phone_number']}, DOB: {user['dob']}")
            print(f"  Profile: {user['profile_image']}, Created: {user['created_at']}, Updated: {user['updated_at']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 8: Search with multiple statuses (array)
    print("=== Test 8: Search with multiple statuses (ACTIVE + BLOCKED) ===")
    multi_status_search = {
        "page": 1,
        "limit": 10,
        "search_query": None,
        "user_type": None,
        "date_filter": None,
        "status": ["ACTIVE", "BLOCKED"]  # Search for both ACTIVE and BLOCKED users
    }
    
    response = requests.post(f"{BASE_URL}/users/search", json=multi_status_search)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"ACTIVE + BLOCKED users found: {len(data['data'])}")
        for user in data['data']:
            print(f"- {user['full_name']} ({user['user_type']}) - Status: {user['status']}")
            print(f"  Email: {user['email']}, Phone: {user['phone_number']}, DOB: {user['dob']}")
            print(f"  Profile: {user['profile_image']}, Created: {user['created_at']}, Updated: {user['updated_at']}")
    else:
        print(f"Error: {response.text}")


def test_user_status_operations():
    """Test user status operations using the single status update endpoint"""
    print("\n" + "="*50)
    print("=== Testing User Status Operations ===")
    print("="*50)
    
    # Note: These tests require existing user IDs
    # You may need to create users first or use existing IDs
    
    # Test 1: Block a user
    print("\n--- Test 1: Block User ---")
    user_id = 1  # Change this to an existing user ID
    status_update = {"status": "BLOCKED"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}/status", json=status_update)
    print(f"Block user {user_id} - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['data']['message']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Activate a user
    print("\n--- Test 2: Activate User ---")
    status_update = {"status": "ACTIVE"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}/status", json=status_update)
    print(f"Activate user {user_id} - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['data']['message']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: Soft delete a user
    print("\n--- Test 3: Soft Delete User ---")
    status_update = {"status": "DELETED"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}/status", json=status_update)
    print(f"Soft delete user {user_id} - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['data']['message']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 4: Reactivate the user
    print("\n--- Test 4: Reactivate User ---")
    status_update = {"status": "ACTIVE"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}/status", json=status_update)
    print(f"Reactivate user {user_id} - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['data']['message']}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("Testing User Search API...")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print()
    
    try:
        test_user_search()
        test_user_status_operations()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Please make sure your FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")

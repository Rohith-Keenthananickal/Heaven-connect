"""
Test script for the Issue API endpoints
"""
import requests
import json
import time
from datetime import datetime

# Base URL for API
BASE_URL = "http://localhost:8000/api/v1"

# Test user IDs (you may need to adjust these based on your database)
TEST_CREATED_BY_ID = 1
TEST_ASSIGNED_TO_ID = 1
TEST_PROPERTY_ID = 1  # Optional, can be None

def test_create_complaint_issue():
    """Test creating a new COMPLAINT issue"""
    print("\n=== Testing Create COMPLAINT Issue ===")
    
    data = {
        "issue": "Property maintenance complaint",
        "type": "COMPLAINT",
        "description": "The property needs urgent maintenance work",
        "property_id": TEST_PROPERTY_ID,
        "assigned_to_id": TEST_ASSIGNED_TO_ID,
        "priority": "HIGH",
        "created_by_id": TEST_CREATED_BY_ID,
        "issue_status": "OPEN",
        "attachments": []
    }
    
    response = requests.post(f"{BASE_URL}/issues/", json=data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("COMPLAINT Issue created successfully!")
        result = response.json()
        print(f"Issue ID: {result['data']['id']}")
        print(f"Issue Code: {result['data']['issue_code']}")
        print(json.dumps(result, indent=2))
        return result['data']['id']
    else:
        print(f"Failed to create issue: {response.text}")
        return None

def test_create_support_issue():
    """Test creating a new SUPPORT issue"""
    print("\n=== Testing Create SUPPORT Issue ===")
    
    data = {
        "issue": "Technical support request",
        "type": "SUPPORT",
        "description": "Need help with account setup",
        "property_id": None,
        "assigned_to_id": TEST_ASSIGNED_TO_ID,
        "priority": "MEDIUM",
        "created_by_id": TEST_CREATED_BY_ID,
        "issue_status": "OPEN",
        "attachments": []
    }
    
    response = requests.post(f"{BASE_URL}/issues/", json=data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("SUPPORT Issue created successfully!")
        result = response.json()
        print(f"Issue ID: {result['data']['id']}")
        print(f"Issue Code: {result['data']['issue_code']}")
        print(json.dumps(result, indent=2))
        return result['data']['id']
    else:
        print(f"Failed to create issue: {response.text}")
        return None

def test_get_issue(issue_id):
    """Test retrieving a specific issue"""
    print(f"\n=== Testing Get Issue {issue_id} ===")
    
    response = requests.get(f"{BASE_URL}/issues/{issue_id}")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Issue retrieved successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to retrieve issue: {response.text}")

def test_list_issues():
    """Test listing all issues"""
    print("\n=== Testing List Issues ===")
    
    response = requests.get(f"{BASE_URL}/issues/")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Retrieved {len(result['data'])} issues")
        if result['data']:
            print(f"First issue code: {result['data'][0].get('issue_code', 'N/A')}")
        print(json.dumps(result, indent=2))
    else:
        print(f"Failed to list issues: {response.text}")

def test_search_issues():
    """Test searching issues"""
    print("\n=== Testing Search Issues ===")
    
    data = {
        "page": 1,
        "limit": 10,
        "type": "COMPLAINT",
        "issue_status": "OPEN"
    }
    
    response = requests.post(f"{BASE_URL}/issues/search", json=data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result['data'])} matching issues")
        print(json.dumps(result, indent=2))
    else:
        print(f"Failed to search issues: {response.text}")

def test_update_issue(issue_id):
    """Test updating an issue"""
    print(f"\n=== Testing Update Issue {issue_id} ===")
    
    data = {
        "description": "Updated description for the issue",
        "priority": "URGENT"
    }
    
    response = requests.put(
        f"{BASE_URL}/issues/{issue_id}",
        json=data,
        params={"updated_by_id": TEST_CREATED_BY_ID}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Issue updated successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to update issue: {response.text}")

def test_update_issue_status(issue_id):
    """Test updating issue status"""
    print(f"\n=== Testing Update Issue Status {issue_id} ===")
    
    data = {
        "issue_status": "IN_PROGRESS",
        "description": "Issue is now being worked on"
    }
    
    response = requests.patch(
        f"{BASE_URL}/issues/{issue_id}/status",
        json=data,
        params={"updated_by_id": TEST_CREATED_BY_ID}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Issue status updated successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to update issue status: {response.text}")

def test_assign_issue(issue_id):
    """Test assigning an issue"""
    print(f"\n=== Testing Assign Issue {issue_id} ===")
    
    data = {
        "assigned_to_id": TEST_ASSIGNED_TO_ID
    }
    
    response = requests.patch(
        f"{BASE_URL}/issues/{issue_id}/assign",
        json=data,
        params={"assigned_by_id": TEST_CREATED_BY_ID}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Issue assigned successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to assign issue: {response.text}")

def test_update_priority(issue_id):
    """Test updating issue priority"""
    print(f"\n=== Testing Update Priority {issue_id} ===")
    
    data = {
        "priority": "HIGH"
    }
    
    response = requests.patch(
        f"{BASE_URL}/issues/{issue_id}/priority",
        json=data,
        params={"updated_by_id": TEST_CREATED_BY_ID}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Priority updated successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to update priority: {response.text}")

def test_create_activity(issue_id):
    """Test creating an activity log"""
    print(f"\n=== Testing Create Activity for Issue {issue_id} ===")
    
    data = {
        "activity_type": "COMMENT_ADDED",
        "description": "Added a comment to track progress",
        "performed_by_id": TEST_CREATED_BY_ID
    }
    
    response = requests.post(f"{BASE_URL}/issues/{issue_id}/activities", json=data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("Activity created successfully!")
        print(json.dumps(response.json(), indent=2))
        return response.json()['data']['id']
    else:
        print(f"Failed to create activity: {response.text}")
        return None

def test_get_activities(issue_id):
    """Test getting issue activities"""
    print(f"\n=== Testing Get Activities for Issue {issue_id} ===")
    
    response = requests.get(f"{BASE_URL}/issues/{issue_id}/activities")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Retrieved {len(result['data'])} activities")
        print(json.dumps(result, indent=2))
    else:
        print(f"Failed to get activities: {response.text}")

def test_create_escalation(issue_id):
    """Test creating an escalation (only for COMPLAINT issues)"""
    print(f"\n=== Testing Create Escalation for Issue {issue_id} ===")
    
    data = {
        "escalation_level": "LEVEL_1",
        "escalated_by_id": TEST_CREATED_BY_ID,
        "escalated_to_id": TEST_ASSIGNED_TO_ID,
        "reason": "Issue requires immediate attention",
        "notes": "Escalating to senior support"
    }
    
    response = requests.post(f"{BASE_URL}/issues/{issue_id}/escalations", json=data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("Escalation created successfully!")
        result = response.json()
        print(json.dumps(result, indent=2))
        return result['data']['id']
    else:
        print(f"Failed to create escalation: {response.text}")
        return None

def test_get_escalations(issue_id):
    """Test getting issue escalations"""
    print(f"\n=== Testing Get Escalations for Issue {issue_id} ===")
    
    response = requests.get(f"{BASE_URL}/issues/{issue_id}/escalations")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Retrieved {len(result['data'])} escalations")
        print(json.dumps(result, indent=2))
        if result['data']:
            return result['data'][0]['id']
    else:
        print(f"Failed to get escalations: {response.text}")
    return None

def test_update_escalation(escalation_id):
    """Test updating an escalation"""
    print(f"\n=== Testing Update Escalation {escalation_id} ===")
    
    data = {
        "resolved": True,
        "notes": "Escalation has been resolved",
        "resolved_by_id": TEST_ASSIGNED_TO_ID
    }
    
    response = requests.patch(f"{BASE_URL}/issues/escalations/{escalation_id}", json=data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Escalation updated successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to update escalation: {response.text}")

def test_delete_issue(issue_id):
    """Test deleting an issue (soft delete)"""
    print(f"\n=== Testing Delete Issue {issue_id} ===")
    
    confirm = input(f"Are you sure you want to delete issue {issue_id}? (y/n): ")
    if confirm.lower() != 'y':
        print("Delete operation cancelled")
        return
    
    response = requests.delete(
        f"{BASE_URL}/issues/{issue_id}",
        params={"deleted_by_id": TEST_CREATED_BY_ID}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Issue deleted successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to delete issue: {response.text}")

def test_filter_issues():
    """Test filtering issues by various parameters"""
    print("\n=== Testing Filter Issues ===")
    
    # Test by type
    print("\n--- Filter by COMPLAINT type ---")
    response = requests.get(f"{BASE_URL}/issues/?type=COMPLAINT")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result['data'])} COMPLAINT issues")
    
    # Test by status
    print("\n--- Filter by OPEN status ---")
    response = requests.get(f"{BASE_URL}/issues/?issue_status=OPEN")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result['data'])} OPEN issues")
    
    # Test by priority
    print("\n--- Filter by HIGH priority ---")
    response = requests.get(f"{BASE_URL}/issues/?priority=HIGH")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result['data'])} HIGH priority issues")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Issue API Endpoints")
    print("=" * 60)
    print(f"\nUsing Test User IDs:")
    print(f"  Created By ID: {TEST_CREATED_BY_ID}")
    print(f"  Assigned To ID: {TEST_ASSIGNED_TO_ID}")
    print(f"  Property ID: {TEST_PROPERTY_ID}")
    print("\nNote: Make sure these IDs exist in your database!")
    print("=" * 60)
    
    # Run tests in sequence
    complaint_id = test_create_complaint_issue()
    support_id = test_create_support_issue()
    
    if complaint_id:
        test_get_issue(complaint_id)
        test_update_issue(complaint_id)
        test_update_issue_status(complaint_id)
        test_assign_issue(complaint_id)
        test_update_priority(complaint_id)
        test_create_activity(complaint_id)
        test_get_activities(complaint_id)
        
        # Test escalation (only for COMPLAINT)
        escalation_id = test_create_escalation(complaint_id)
        if escalation_id:
            test_get_escalations(complaint_id)
            test_update_escalation(escalation_id)
    
    if support_id:
        test_get_issue(support_id)
        test_create_activity(support_id)
        test_get_activities(support_id)
        # Escalation should fail for SUPPORT type
        print("\n=== Testing Escalation on SUPPORT (should fail) ===")
        test_create_escalation(support_id)
    
    test_list_issues()
    test_search_issues()
    test_filter_issues()
    
    # Optional deletion test
    if complaint_id or support_id:
        delete = input("\nDo you want to test deletion of created issues? (y/n): ")
        if delete.lower() == 'y':
            if complaint_id:
                test_delete_issue(complaint_id)
            if support_id:
                test_delete_issue(support_id)
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


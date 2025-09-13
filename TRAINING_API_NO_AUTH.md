# Training Module API Documentation (No Authentication)

## Overview

The Training Module API provides comprehensive functionality for managing training modules, content, and progress tracking for Area Coordinators. This version works **without JWT authentication** - instead, you pass the `user_id` as a query parameter.

## Key Changes from Authenticated Version

- **No JWT tokens required** - all endpoints accept `user_id` as a query parameter
- **Role verification** - the API verifies that the user exists and has the correct role
- **Simplified integration** - easier to integrate with existing systems that don't use JWT

## API Endpoints

### Base URL
```
/api/v1/training
```

## Training Module Endpoints

### 1. Create Training Module
```http
POST /api/v1/training/modules?created_by={admin_user_id}
```

**Parameters:**
- `created_by` (query): Admin user ID who is creating the module

**Request Body:**
```json
{
  "title": "Area Coordinator Basics",
  "description": "Introduction to the role and responsibilities",
  "module_order": 1,
  "is_active": true,
  "estimated_duration_minutes": 30,
  "contents": [
    {
      "content_type": "TEXT",
      "title": "Welcome Message",
      "content": "Welcome to your new role...",
      "content_order": 1,
      "is_required": true
    }
  ]
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/training/modules?created_by=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Safety Training",
    "description": "Important safety guidelines",
    "module_order": 1,
    "estimated_duration_minutes": 45
  }'
```

### 2. Get All Training Modules
```http
GET /api/v1/training/modules?skip=0&limit=100&active_only=true
```

**Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)
- `active_only` (optional): Only return active modules (default: true)

### 3. Get Specific Module
```http
GET /api/v1/training/modules/{module_id}
```

### 4. Update Training Module
```http
PUT /api/v1/training/modules/{module_id}?admin_user_id={admin_user_id}
```

### 5. Delete Training Module
```http
DELETE /api/v1/training/modules/{module_id}?admin_user_id={admin_user_id}
```

## Training Content Endpoints

### 1. Create Training Content
```http
POST /api/v1/training/modules/{module_id}/contents?admin_user_id={admin_user_id}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/training/modules/1/contents?admin_user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "QUIZ",
    "title": "Safety Quiz",
    "content": "Test your safety knowledge",
    "content_order": 3,
    "is_required": true,
    "quiz_questions": {
      "q1": {
        "question": "What should you do in case of fire?",
        "options": ["Run", "Call 911", "Use extinguisher", "All of the above"],
        "correct": "All of the above"
      }
    },
    "passing_score": 80
  }'
```

### 2. Get Module Contents
```http
GET /api/v1/training/modules/{module_id}/contents
```

### 3. Get Content with User Progress
```http
GET /api/v1/training/contents/{content_id}?user_id={user_id}
```

**Parameters:**
- `user_id` (query): Area Coordinator user ID

### 4. Update Training Content
```http
PUT /api/v1/training/contents/{content_id}?admin_user_id={admin_user_id}
```

### 5. Delete Training Content
```http
DELETE /api/v1/training/contents/{content_id}?admin_user_id={admin_user_id}
```

## Area Coordinator Endpoints

### 1. Get My Training Modules
```http
GET /api/v1/training/my-modules?user_id={user_id}&skip=0&limit=100
```

**Parameters:**
- `user_id` (query): Area Coordinator user ID
- `skip` (optional): Number of records to skip
- `limit` (optional): Maximum number of records to return

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/training/my-modules?user_id=123&skip=0&limit=10"
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Area Coordinator Basics",
    "description": "Introduction to the role and responsibilities",
    "module_order": 1,
    "is_active": true,
    "estimated_duration_minutes": 30,
    "contents": [
      {
        "id": 1,
        "content_type": "TEXT",
        "title": "Welcome Message",
        "content": "Welcome to your new role...",
        "content_order": 1,
        "is_required": true,
        "user_progress": {
          "id": 1,
          "status": "COMPLETED",
          "progress_percentage": 100,
          "time_spent_seconds": 300,
          "completed_at": "2024-01-15T11:00:00Z"
        }
      }
    ],
    "user_progress": {
      "id": 1,
      "status": "IN_PROGRESS",
      "progress_percentage": 66,
      "time_spent_seconds": 900
    },
    "total_contents": 3,
    "completed_contents": 2
  }
]
```

### 2. Update Training Progress
```http
POST /api/v1/training/progress?user_id={user_id}
```

**Parameters:**
- `user_id` (query): Area Coordinator user ID

**Request Body:**
```json
{
  "content_id": 1,
  "progress_percentage": 100,
  "time_spent_seconds": 300,
  "status": "COMPLETED"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/training/progress?user_id=123" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 1,
    "progress_percentage": 100,
    "time_spent_seconds": 300,
    "status": "COMPLETED"
  }'
```

### 3. Submit Quiz
```http
POST /api/v1/training/quiz/submit?user_id={user_id}
```

**Parameters:**
- `user_id` (query): Area Coordinator user ID

**Request Body:**
```json
{
  "content_id": 3,
  "answers": {
    "q1": "All of the above",
    "q2": "Monthly",
    "q3": "Call emergency services immediately"
  },
  "time_spent_seconds": 120
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/training/quiz/submit?user_id=123" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 3,
    "answers": {
      "q1": "All of the above",
      "q2": "Monthly"
    },
    "time_spent_seconds": 120
  }'
```

**Response:**
```json
{
  "content_id": 3,
  "score": 85,
  "passed": true,
  "total_questions": 2,
  "correct_answers": 1,
  "attempts": 1
}
```

### 4. Get Training Statistics
```http
GET /api/v1/training/stats?user_id={user_id}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/training/stats?user_id=123"
```

**Response:**
```json
{
  "total_modules": 4,
  "completed_modules": 2,
  "total_contents": 14,
  "completed_contents": 8,
  "total_time_spent_seconds": 3600,
  "overall_progress_percentage": 57.14,
  "current_module_id": 3,
  "next_module_id": 4
}
```

### 5. Get Module Progress Summary
```http
GET /api/v1/training/modules/{module_id}/progress?user_id={user_id}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/training/modules/1/progress?user_id=123"
```

**Response:**
```json
{
  "module_id": 1,
  "module_title": "Area Coordinator Basics",
  "total_contents": 3,
  "completed_contents": 2,
  "progress_percentage": 66.67,
  "status": "IN_PROGRESS",
  "time_spent_seconds": 900,
  "estimated_duration_minutes": 30,
  "is_completed": false,
  "completed_at": null
}
```

## Admin Analytics Endpoints

### 1. Get Training Analytics
```http
GET /api/v1/training/admin/analytics?admin_user_id={admin_user_id}
```

### 2. Get User Training Progress
```http
GET /api/v1/training/admin/user/{user_id}/progress?admin_user_id={admin_user_id}
```

## Python Code Examples

### 1. Get User's Training Modules
```python
import httpx
import asyncio

async def get_user_training_modules(user_id: int, base_url: str = "http://localhost:8000"):
    """Get all training modules for a user with their progress"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/api/v1/training/my-modules",
            params={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

# Usage
modules = await get_user_training_modules(123)
for module in modules:
    print(f"Module: {module['title']}")
    print(f"Progress: {module['user_progress']['progress_percentage']}%")
    print(f"Completed Contents: {module['completed_contents']}/{module['total_contents']}")
```

### 2. Mark Content as Completed
```python
async def mark_content_completed(user_id: int, content_id: int, time_spent: int):
    """Mark a content item as completed"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/training/progress",
            params={"user_id": user_id},
            json={
                "content_id": content_id,
                "progress_percentage": 100,
                "time_spent_seconds": time_spent,
                "status": "COMPLETED"
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
result = await mark_content_completed(123, 1, 300)
print(f"Content {result['content_id']} marked as completed")
```

### 3. Submit Quiz Answers
```python
async def submit_quiz(user_id: int, content_id: int, answers: dict, time_spent: int):
    """Submit quiz answers and get score"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/training/quiz/submit",
            params={"user_id": user_id},
            json={
                "content_id": content_id,
                "answers": answers,
                "time_spent_seconds": time_spent
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
quiz_result = await submit_quiz(
    123, 
    3, 
    {
        "q1": "All of the above",
        "q2": "Monthly"
    },
    120
)
print(f"Quiz Score: {quiz_result['score']}% - {'Passed' if quiz_result['passed'] else 'Failed'}")
```

### 4. Get Training Statistics
```python
async def get_training_stats(user_id: int):
    """Get comprehensive training statistics"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/training/stats",
            params={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

# Usage
stats = await get_training_stats(123)
print(f"Overall Progress: {stats['overall_progress_percentage']}%")
print(f"Completed Modules: {stats['completed_modules']}/{stats['total_modules']}")
print(f"Time Spent: {stats['total_time_spent_seconds']} seconds")
```

## Frontend Integration Example

```javascript
// Get user's training modules
async function getUserTrainingModules(userId) {
  const response = await fetch(`/api/v1/training/my-modules?user_id=${userId}`);
  return await response.json();
}

// Mark content as completed
async function markContentCompleted(userId, contentId, timeSpent) {
  const response = await fetch('/api/v1/training/progress', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      content_id: contentId,
      progress_percentage: 100,
      time_spent_seconds: timeSpent,
      status: 'COMPLETED'
    })
  });
  return await response.json();
}

// Submit quiz
async function submitQuiz(userId, contentId, answers, timeSpent) {
  const response = await fetch('/api/v1/training/quiz/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      content_id: contentId,
      answers: answers,
      time_spent_seconds: timeSpent
    })
  });
  return await response.json();
}
```

## Key Points

1. **No Authentication Required**: All endpoints work without JWT tokens
2. **User ID Parameter**: Pass `user_id` as a query parameter for area coordinator endpoints
3. **Admin ID Parameter**: Pass `admin_user_id` as a query parameter for admin endpoints
4. **Role Verification**: The API automatically verifies that users have the correct roles
5. **Progress Tracking**: The system automatically calculates module progress based on completed contents
6. **Time Tracking**: All interactions are tracked for analytics
7. **Quiz Scoring**: Quizzes have configurable passing scores and allow multiple attempts

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content (for deletions)
- `400`: Bad Request
- `404`: Not Found (user not found or wrong role)
- `422`: Validation Error

## Database Migration

To set up the training module tables, run:

```bash
python app/migrations/create_training_tables.py
```

This will create the necessary tables and insert sample data for testing.

The training system is now ready to use without authentication! Simply pass the appropriate user IDs as query parameters.

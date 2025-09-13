# Training Module API Documentation (With Common Response Models)

## Overview

The Training Module API now uses the common response models established in the codebase, providing consistent response formatting across all endpoints. All responses follow the `BaseResponse` pattern with `status`, `data`, and `message` fields.

## Response Format

All API responses now follow this consistent structure:

```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

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

**Response Model**: `TrainingModuleCreateAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "Area Coordinator Basics",
    "description": "Introduction to the role and responsibilities",
    "module_order": 1,
    "is_active": true,
    "estimated_duration_minutes": 30,
    "created_by": 1,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "contents": [
      {
        "id": 1,
        "content_type": "TEXT",
        "title": "Welcome Message",
        "content": "Welcome to your new role...",
        "content_order": 1,
        "is_required": true
      }
    ]
  },
  "message": "Training module created successfully"
}
```

### 2. Get All Training Modules
```http
GET /api/v1/training/modules?skip=0&limit=100&active_only=true
```

**Response Model**: `TrainingModuleListAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Area Coordinator Basics",
      "description": "Introduction to the role and responsibilities",
      "module_order": 1,
      "is_active": true,
      "estimated_duration_minutes": 30,
      "created_by": 1,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "message": "Training modules retrieved successfully"
}
```

### 3. Get Specific Module
```http
GET /api/v1/training/modules/{module_id}
```

**Response Model**: `TrainingModuleGetAPIResponse`

### 4. Update Training Module
```http
PUT /api/v1/training/modules/{module_id}?admin_user_id={admin_user_id}
```

**Response Model**: `TrainingModuleUpdateAPIResponse`

### 5. Delete Training Module
```http
DELETE /api/v1/training/modules/{module_id}?admin_user_id={admin_user_id}
```

**Response Model**: `TrainingModuleDeleteAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": {},
  "message": "Training module deleted successfully"
}
```

## Training Content Endpoints

### 1. Create Training Content
```http
POST /api/v1/training/modules/{module_id}/contents?admin_user_id={admin_user_id}
```

**Response Model**: `TrainingContentCreateAPIResponse`

### 2. Get Module Contents
```http
GET /api/v1/training/modules/{module_id}/contents
```

**Response Model**: `TrainingContentListAPIResponse`

### 3. Get Content with User Progress
```http
GET /api/v1/training/contents/{content_id}?user_id={user_id}
```

**Response Model**: `TrainingContentGetAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "module_id": 1,
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
  },
  "message": "Training content retrieved successfully"
}
```

### 4. Update Training Content
```http
PUT /api/v1/training/contents/{content_id}?admin_user_id={admin_user_id}
```

**Response Model**: `TrainingContentUpdateAPIResponse`

### 5. Delete Training Content
```http
DELETE /api/v1/training/contents/{content_id}?admin_user_id={admin_user_id}
```

**Response Model**: `TrainingContentDeleteAPIResponse`

## Area Coordinator Endpoints

### 1. Get My Training Modules
```http
GET /api/v1/training/my-modules?user_id={user_id}&skip=0&limit=100
```

**Response Model**: `UserTrainingModulesAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": [
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
            "time_spent_seconds": 300
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
  ],
  "message": "User training modules retrieved successfully"
}
```

### 2. Update Training Progress
```http
POST /api/v1/training/progress?user_id={user_id}
```

**Response Model**: `TrainingProgressUpdateAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 123,
    "module_id": 1,
    "content_id": 1,
    "status": "COMPLETED",
    "progress_percentage": 100,
    "time_spent_seconds": 300,
    "quiz_score": null,
    "quiz_attempts": 0,
    "started_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T11:00:00Z",
    "last_accessed_at": "2024-01-15T11:00:00Z",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  },
  "message": "Training progress updated successfully"
}
```

### 3. Submit Quiz
```http
POST /api/v1/training/quiz/submit?user_id={user_id}
```

**Response Model**: `QuizSubmitAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": {
    "content_id": 3,
    "score": 85,
    "passed": true,
    "total_questions": 3,
    "correct_answers": 2,
    "attempts": 1
  },
  "message": "Quiz submitted successfully"
}
```

### 4. Get Training Statistics
```http
GET /api/v1/training/stats?user_id={user_id}
```

**Response Model**: `TrainingStatsAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": {
    "total_modules": 4,
    "completed_modules": 2,
    "total_contents": 14,
    "completed_contents": 8,
    "total_time_spent_seconds": 3600,
    "overall_progress_percentage": 57.14,
    "current_module_id": 3,
    "next_module_id": 4
  },
  "message": "Training statistics retrieved successfully"
}
```

### 5. Get Module Progress Summary
```http
GET /api/v1/training/modules/{module_id}/progress?user_id={user_id}
```

**Response Model**: `ModuleProgressAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": {
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
  },
  "message": "Module progress retrieved successfully"
}
```

## Admin Analytics Endpoints

### 1. Get Training Analytics
```http
GET /api/v1/training/admin/analytics?admin_user_id={admin_user_id}
```

**Response Model**: `TrainingAnalyticsAPIResponse`

**Example Response**:
```json
{
  "status": "success",
  "data": [
    {
      "message": "Analytics endpoint - to be implemented based on requirements"
    }
  ],
  "message": "Training analytics retrieved successfully"
}
```

### 2. Get User Training Progress
```http
GET /api/v1/training/admin/user/{user_id}/progress?admin_user_id={admin_user_id}
```

**Response Model**: `TrainingStatsAPIResponse`

## Error Responses

All error responses follow the same pattern:

```json
{
  "status": "error",
  "detail": "Error message describing what went wrong"
}
```

**Common Error Status Codes**:
- `400`: Bad Request
- `404`: Not Found (user not found or wrong role)
- `422`: Validation Error

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
        data = response.json()
        
        # Access the data field from the common response
        modules = data["data"]
        message = data["message"]
        
        print(f"Message: {message}")
        for module in modules:
            print(f"Module: {module['title']}")
            print(f"Progress: {module['user_progress']['progress_percentage']}%")
            print(f"Completed Contents: {module['completed_contents']}/{module['total_contents']}")
        
        return modules

# Usage
modules = await get_user_training_modules(123)
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
        data = response.json()
        
        # Access the data field from the common response
        progress = data["data"]
        message = data["message"]
        
        print(f"Message: {message}")
        print(f"Content {progress['content_id']} marked as completed")
        
        return progress

# Usage
result = await mark_content_completed(123, 1, 300)
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
        data = response.json()
        
        # Access the data field from the common response
        quiz_result = data["data"]
        message = data["message"]
        
        print(f"Message: {message}")
        print(f"Quiz Score: {quiz_result['score']}% - {'Passed' if quiz_result['passed'] else 'Failed'}")
        
        return quiz_result

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
```

## Frontend Integration Example

```javascript
// Get user's training modules
async function getUserTrainingModules(userId) {
  const response = await fetch(`/api/v1/training/my-modules?user_id=${userId}`);
  const data = await response.json();
  
  // Access the data field from the common response
  const modules = data.data;
  const message = data.message;
  
  console.log(message);
  return modules;
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
  
  const data = await response.json();
  
  // Access the data field from the common response
  const progress = data.data;
  const message = data.message;
  
  console.log(message);
  return progress;
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
  
  const data = await response.json();
  
  // Access the data field from the common response
  const quizResult = data.data;
  const message = data.message;
  
  console.log(message);
  return quizResult;
}
```

## Key Benefits of Common Response Models

1. **Consistent API Responses**: All endpoints follow the same response structure
2. **Better Error Handling**: Standardized error response format
3. **Improved Documentation**: Clear response schemas for Swagger/OpenAPI
4. **Easier Frontend Integration**: Predictable response structure
5. **Better Debugging**: Consistent message and status fields
6. **Future-Proof**: Easy to extend with additional metadata

## Response Model Hierarchy

```
BaseResponse
├── TrainingModuleCreateAPIResponse
├── TrainingModuleGetAPIResponse
├── TrainingModuleListAPIResponse
├── TrainingModuleUpdateAPIResponse
├── TrainingModuleDeleteAPIResponse
├── TrainingContentCreateAPIResponse
├── TrainingContentGetAPIResponse
├── TrainingContentListAPIResponse
├── TrainingContentUpdateAPIResponse
├── TrainingContentDeleteAPIResponse
├── TrainingProgressUpdateAPIResponse
├── QuizSubmitAPIResponse
├── TrainingStatsAPIResponse
├── ModuleProgressAPIResponse
├── UserTrainingModulesAPIResponse
└── TrainingAnalyticsAPIResponse
```

The training system now provides a consistent and professional API experience that matches the established patterns in your codebase!

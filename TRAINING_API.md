# Training Module API Documentation

## Overview

The Training Module API provides comprehensive functionality for managing training modules, content, and progress tracking for Area Coordinators. This system allows administrators to create and manage training modules with various content types (text, video, documents, quizzes) and enables Area Coordinators to access training materials and track their progress.

## Features

- **Training Module Management**: Create, read, update, and delete training modules
- **Content Management**: Support for text, video, document, and quiz content types
- **Progress Tracking**: Track user progress through modules and individual content
- **Quiz System**: Interactive quizzes with scoring and passing requirements
- **Analytics**: Comprehensive statistics and progress reporting
- **Role-based Access**: Different permissions for admins and area coordinators

## Database Schema

### Tables

1. **training_modules**: Stores training module information
2. **training_contents**: Stores individual content items within modules
3. **training_progress**: Tracks user progress through modules and content

### Key Relationships

- Each training module can have multiple contents
- Each content can have multiple progress records (one per user)
- Users can have progress records for both modules and individual contents

## API Endpoints

### Authentication

All endpoints require authentication. Use the existing auth system with JWT tokens.

### Base URL

```
/api/v1/training
```

## Training Module Endpoints

### Create Training Module
```http
POST /api/v1/training/modules
```

**Authorization**: Admin only

**Request Body**:
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
    },
    {
      "content_type": "VIDEO",
      "title": "Overview Video",
      "content": "https://example.com/video.mp4",
      "content_order": 2,
      "is_required": true,
      "video_duration_seconds": 300,
      "thumbnail_url": "https://example.com/thumb.jpg"
    }
  ]
}
```

### Get Training Modules
```http
GET /api/v1/training/modules?skip=0&limit=100&active_only=true
```

**Response**: List of training modules

### Get Specific Module
```http
GET /api/v1/training/modules/{module_id}
```

**Response**: Training module with all contents

### Update Training Module
```http
PUT /api/v1/training/modules/{module_id}
```

**Authorization**: Admin only

### Delete Training Module
```http
DELETE /api/v1/training/modules/{module_id}
```

**Authorization**: Admin only

## Training Content Endpoints

### Create Training Content
```http
POST /api/v1/training/modules/{module_id}/contents
```

**Authorization**: Admin only

**Request Body**:
```json
{
  "content_type": "QUIZ",
  "title": "Module Assessment",
  "content": "Test your knowledge",
  "content_order": 3,
  "is_required": true,
  "quiz_questions": {
    "q1": {
      "question": "What is the primary responsibility?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct": "Option A"
    }
  },
  "passing_score": 70
}
```

### Get Module Contents
```http
GET /api/v1/training/modules/{module_id}/contents
```

### Get Content with Progress
```http
GET /api/v1/training/contents/{content_id}
```

**Authorization**: Area Coordinator only

**Response**: Content with user's progress information

### Update Training Content
```http
PUT /api/v1/training/contents/{content_id}
```

**Authorization**: Admin only

### Delete Training Content
```http
DELETE /api/v1/training/contents/{content_id}
```

**Authorization**: Admin only

## Area Coordinator Endpoints

### Get My Training Modules
```http
GET /api/v1/training/my-modules?skip=0&limit=100
```

**Authorization**: Area Coordinator only

**Response**: List of modules with user's progress

### Update Training Progress
```http
POST /api/v1/training/progress
```

**Authorization**: Area Coordinator only

**Request Body**:
```json
{
  "content_id": 1,
  "progress_percentage": 50,
  "time_spent_seconds": 300,
  "status": "IN_PROGRESS"
}
```

### Submit Quiz
```http
POST /api/v1/training/quiz/submit
```

**Authorization**: Area Coordinator only

**Request Body**:
```json
{
  "content_id": 3,
  "answers": {
    "q1": "Option A",
    "q2": "Option C",
    "q3": "Option B"
  },
  "time_spent_seconds": 120
}
```

**Response**:
```json
{
  "content_id": 3,
  "score": 85,
  "passed": true,
  "total_questions": 3,
  "correct_answers": 2,
  "attempts": 1
}
```

### Get Training Statistics
```http
GET /api/v1/training/stats
```

**Authorization**: Area Coordinator only

**Response**:
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

### Get Module Progress Summary
```http
GET /api/v1/training/modules/{module_id}/progress
```

**Authorization**: Area Coordinator only

**Response**:
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

### Get Training Analytics
```http
GET /api/v1/training/admin/analytics
```

**Authorization**: Admin only

### Get User Training Progress
```http
GET /api/v1/training/admin/user/{user_id}/progress
```

**Authorization**: Admin only

## Content Types

### TEXT
- Simple text content
- Used for instructions, descriptions, and reading materials

### VIDEO
- Video content with URL
- Optional thumbnail and duration tracking
- Progress tracked by time spent

### DOCUMENT
- Document content with URL
- PDFs, images, or other downloadable materials

### QUIZ
- Interactive quiz with questions and answers
- Scoring system with passing requirements
- Multiple attempts allowed

## Progress Tracking

### Status Values
- `NOT_STARTED`: User hasn't started this content/module
- `IN_PROGRESS`: User is currently working on this content/module
- `COMPLETED`: User has successfully completed this content/module
- `FAILED`: User failed to complete (typically for quizzes)

### Progress Calculation
- Module progress is calculated based on completed required contents
- Content progress is tracked individually
- Time spent is accumulated across all interactions

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content (for deletions)
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error

## Usage Examples

### Creating a Complete Training Module

1. **Create Module**:
```bash
curl -X POST "http://localhost:8000/api/v1/training/modules" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Safety Training",
    "description": "Important safety guidelines",
    "module_order": 1,
    "estimated_duration_minutes": 45,
    "contents": [
      {
        "content_type": "TEXT",
        "title": "Introduction",
        "content": "Safety is our top priority...",
        "content_order": 1,
        "is_required": true
      },
      {
        "content_type": "VIDEO",
        "title": "Safety Video",
        "content": "https://example.com/safety-video.mp4",
        "content_order": 2,
        "is_required": true,
        "video_duration_seconds": 600
      },
      {
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
      }
    ]
  }'
```

2. **Area Coordinator Accessing Training**:
```bash
# Get my modules
curl -X GET "http://localhost:8000/api/v1/training/my-modules" \
  -H "Authorization: Bearer AREA_COORDINATOR_JWT_TOKEN"

# Update progress
curl -X POST "http://localhost:8000/api/v1/training/progress" \
  -H "Authorization: Bearer AREA_COORDINATOR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 1,
    "progress_percentage": 100,
    "time_spent_seconds": 300,
    "status": "COMPLETED"
  }'

# Submit quiz
curl -X POST "http://localhost:8000/api/v1/training/quiz/submit" \
  -H "Authorization: Bearer AREA_COORDINATOR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 3,
    "answers": {
      "q1": "All of the above"
    },
    "time_spent_seconds": 60
  }'
```

## Database Migration

To set up the training module tables, run:

```bash
python app/migrations/create_training_tables.py
```

This will create the necessary tables and insert sample data for testing.

## Notes

- All timestamps are in UTC
- Progress is automatically calculated based on content completion
- Quiz scores are calculated as percentages
- Time tracking is in seconds
- Content order determines the sequence within a module
- Module order determines the sequence of modules
- Only active modules are shown to area coordinators by default

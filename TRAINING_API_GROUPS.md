# Training API - Swagger Group Organization

## Overview

The Training API has been organized into two distinct groups in Swagger for better organization and clarity:

1. **Training Modules Master** - Admin CRUD operations for training modules and content
2. **ATP Training Controller** - Area Coordinator training operations and analytics

## Group 1: Training Modules Master

This group contains all the administrative endpoints for managing training modules and content. These are typically used by administrators to create, update, and manage the training curriculum.

### Endpoints in this group:

#### Training Modules CRUD
- `POST /api/v1/training/modules` - Create training module
- `GET /api/v1/training/modules` - Get all training modules
- `GET /api/v1/training/modules/{module_id}` - Get specific training module
- `PUT /api/v1/training/modules/{module_id}` - Update training module
- `DELETE /api/v1/training/modules/{module_id}` - Delete training module

#### Training Content CRUD
- `POST /api/v1/training/modules/{module_id}/contents` - Create training content
- `GET /api/v1/training/modules/{module_id}/contents` - Get module contents
- `GET /api/v1/training/contents/{content_id}` - Get content with user progress
- `PUT /api/v1/training/contents/{content_id}` - Update training content
- `DELETE /api/v1/training/contents/{content_id}` - Delete training content

### Who uses this group:
- **System Administrators**
- **Training Managers**
- **Content Creators**

### Purpose:
- Manage the training curriculum
- Create and update training modules
- Add/remove training content
- Configure quiz questions and passing scores
- Set module order and requirements

---

## Group 2: ATP Training Controller

This group contains all the operational endpoints for Area Coordinators to access training, track progress, and submit assessments. It also includes analytics endpoints for monitoring training effectiveness.

### Endpoints in this group:

#### Area Coordinator Training Operations
- `GET /api/v1/training/my-modules` - Get user's training modules with progress
- `POST /api/v1/training/progress` - Update training progress
- `POST /api/v1/training/quiz/submit` - Submit quiz answers
- `GET /api/v1/training/stats` - Get comprehensive training statistics
- `GET /api/v1/training/modules/{module_id}/progress` - Get detailed module progress

#### Admin Analytics & Monitoring
- `GET /api/v1/training/admin/analytics` - Get training analytics for all users
- `GET /api/v1/training/admin/user/{user_id}/progress` - Get specific user's training progress

### Who uses this group:
- **Area Coordinators** (primary users)
- **Training Supervisors**
- **HR Managers**
- **System Administrators** (for analytics)

### Purpose:
- Access assigned training modules
- Track learning progress
- Complete quizzes and assessments
- View training statistics and achievements
- Monitor training effectiveness (admin)

---

## Swagger Documentation Structure

In the Swagger UI, you will now see:

```
📁 Training Modules Master
├── POST /api/v1/training/modules
├── GET /api/v1/training/modules
├── GET /api/v1/training/modules/{module_id}
├── PUT /api/v1/training/modules/{module_id}
├── DELETE /api/v1/training/modules/{module_id}
├── POST /api/v1/training/modules/{module_id}/contents
├── GET /api/v1/training/modules/{module_id}/contents
├── GET /api/v1/training/contents/{content_id}
├── PUT /api/v1/training/contents/{content_id}
└── DELETE /api/v1/training/contents/{content_id}

📁 ATP Training Controller
├── GET /api/v1/training/my-modules
├── POST /api/v1/training/progress
├── POST /api/v1/training/quiz/submit
├── GET /api/v1/training/stats
├── GET /api/v1/training/modules/{module_id}/progress
├── GET /api/v1/training/admin/analytics
└── GET /api/v1/training/admin/user/{user_id}/progress
```

## Benefits of This Organization

### 1. **Clear Separation of Concerns**
- Administrative functions are separate from operational functions
- Easy to understand which endpoints are for which user type

### 2. **Better User Experience**
- Users can quickly find the endpoints they need
- Reduces confusion about endpoint purposes

### 3. **Improved Documentation**
- Swagger UI is more organized and navigable
- Each group has a clear purpose and target audience

### 4. **Easier Maintenance**
- Related endpoints are grouped together
- Easier to add new endpoints to the appropriate group

### 5. **Role-Based Access**
- Clear distinction between admin and user endpoints
- Easier to implement role-based access controls

## Usage Examples

### For Administrators (Training Modules Master)
```bash
# Create a new training module
curl -X POST "http://localhost:8000/api/v1/training/modules?created_by=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Safety Training",
    "description": "Important safety guidelines",
    "module_order": 1
  }'

# Add content to the module
curl -X POST "http://localhost:8000/api/v1/training/modules/1/contents?admin_user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "TEXT",
    "title": "Safety Introduction",
    "content": "Safety is our top priority...",
    "content_order": 1
  }'
```

### For Area Coordinators (ATP Training Controller)
```bash
# Get my training modules
curl -X GET "http://localhost:8000/api/v1/training/my-modules?user_id=123"

# Update progress
curl -X POST "http://localhost:8000/api/v1/training/progress?user_id=123" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 1,
    "progress_percentage": 100,
    "time_spent_seconds": 300,
    "status": "COMPLETED"
  }'

# Submit quiz
curl -X POST "http://localhost:8000/api/v1/training/quiz/submit?user_id=123" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 3,
    "answers": {"q1": "All of the above"},
    "time_spent_seconds": 120
  }'
```

## API Response Format

Both groups maintain the same consistent response format:

```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

## Future Extensions

This grouping structure makes it easy to add new endpoints:

- **Training Modules Master**: Add endpoints for bulk operations, content templates, etc.
- **ATP Training Controller**: Add endpoints for notifications, certificates, leaderboards, etc.

The clear separation ensures that new features can be added to the appropriate group without cluttering the API documentation.

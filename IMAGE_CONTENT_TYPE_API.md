# IMAGE Content Type API Documentation

This document describes how to use the new IMAGE content type in the training module APIs.

## Overview

The IMAGE content type has been added to the ContentType enum, allowing training modules to include image-based content alongside existing TEXT, VIDEO, DOCUMENT, and QUIZ content types.

## ContentType Enum

```python
class ContentType(str, enum.Enum):
    TEXT = "TEXT"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    QUIZ = "QUIZ"
    IMAGE = "IMAGE"  # New content type
```

## API Usage Examples

### 1. Creating a Training Module with IMAGE Content

```json
POST /training/modules
{
  "title": "Visual Learning Module",
  "description": "Module with image-based learning content",
  "module_order": 1,
  "is_active": true,
  "estimated_duration_minutes": 15,
  "contents": [
    {
      "content_type": "IMAGE",
      "title": "Property Layout Diagram",
      "content": "https://example.com/images/property-layout.jpg",
      "content_order": 1,
      "is_required": true,
      "thumbnail_url": "https://example.com/images/property-layout-thumb.jpg"
    },
    {
      "content_type": "IMAGE",
      "title": "Safety Equipment Guide",
      "content": "https://example.com/images/safety-equipment.jpg",
      "content_order": 2,
      "is_required": true,
      "thumbnail_url": "https://example.com/images/safety-equipment-thumb.jpg"
    }
  ]
}
```

### 2. Creating Individual IMAGE Content

```json
POST /training/modules/{module_id}/contents
{
  "content_type": "IMAGE",
  "title": "Emergency Exit Map",
  "content": "https://example.com/images/emergency-exit-map.jpg",
  "content_order": 3,
  "is_required": true,
  "thumbnail_url": "https://example.com/images/emergency-exit-thumb.jpg"
}
```

### 3. Updating IMAGE Content

```json
PUT /training/contents/{content_id}
{
  "title": "Updated Property Layout Diagram",
  "content": "https://example.com/images/updated-property-layout.jpg",
  "thumbnail_url": "https://example.com/images/updated-property-layout-thumb.jpg"
}
```

### 4. Getting IMAGE Content

```json
GET /training/contents/{content_id}
```

Response:
```json
{
  "success": true,
  "data": {
    "id": 15,
    "module_id": 1,
    "content_type": "IMAGE",
    "title": "Property Layout Diagram",
    "content": "https://example.com/images/property-layout.jpg",
    "content_order": 1,
    "is_required": true,
    "video_duration_seconds": null,
    "thumbnail_url": "https://example.com/images/property-layout-thumb.jpg",
    "quiz_questions": null,
    "passing_score": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

## Field Usage for IMAGE Content

- **`content`**: URL or path to the main image file
- **`thumbnail_url`**: URL or path to a smaller thumbnail version of the image
- **`video_duration_seconds`**: Not applicable for IMAGE content (will be null)
- **`quiz_questions`**: Not applicable for IMAGE content (will be null)
- **`passing_score`**: Not applicable for IMAGE content (will be null)

## Database Schema

The `training_contents` table has been updated to support the IMAGE content type:

```sql
content_type ENUM('TEXT', 'VIDEO', 'DOCUMENT', 'QUIZ', 'IMAGE') NOT NULL
```

## Migration

To add IMAGE content type to an existing database, run:

```bash
python app/migrations/add_image_content_type.py
```

## Use Cases for IMAGE Content

1. **Property Layouts**: Show property floor plans and layouts
2. **Safety Equipment**: Display safety equipment and their locations
3. **Process Diagrams**: Visual guides for procedures
4. **Emergency Maps**: Emergency exit routes and safety information
5. **Equipment Photos**: Images of tools and equipment
6. **Before/After Comparisons**: Visual examples of good practices
7. **Infographics**: Visual learning materials and charts

## Best Practices

1. **Image URLs**: Use reliable, accessible URLs for image content
2. **Thumbnails**: Provide thumbnail URLs for better performance
3. **Alt Text**: Consider adding descriptive titles for accessibility
4. **File Formats**: Use common web formats (JPEG, PNG, WebP)
5. **File Sizes**: Optimize images for web delivery
6. **Responsive Design**: Ensure images work on different screen sizes

## API Endpoints Supporting IMAGE Content

All existing training content endpoints now support IMAGE content type:

- `POST /training/modules` - Create modules with IMAGE content
- `GET /training/modules` - List modules (includes IMAGE content)
- `GET /training/modules/{module_id}` - Get module with IMAGE content
- `PUT /training/modules/{module_id}` - Update modules
- `DELETE /training/modules/{module_id}` - Delete modules
- `POST /training/modules/{module_id}/contents` - Create IMAGE content
- `GET /training/modules/{module_id}/contents` - List contents (includes IMAGE)
- `GET /training/contents/{content_id}` - Get specific IMAGE content
- `PUT /training/contents/{content_id}` - Update IMAGE content
- `DELETE /training/contents/{content_id}` - Delete IMAGE content
- `GET /training/my-modules` - Get user modules with IMAGE content
- `GET /training/stats` - Get stats (includes IMAGE content in calculations)
- `GET /training/modules/{module_id}/progress` - Get progress (includes IMAGE content)

The IMAGE content type integrates seamlessly with the existing training system and follows the same patterns as other content types.

# Property Types API Documentation

This document describes the new Property Types API endpoints for managing property classifications in the Heaven Connect platform.

## Overview

The Property Types API allows administrators to manage different categories of properties such as "Backwater & Scenic", "Hill Stations & Wildlife", "Beaches & Coastal", etc. Properties can be mapped to these types for better categorization and search functionality.

## Base URL

```
/api/v1/property-types
```

## Endpoints

### 1. Create Property Type

**POST** `/api/v1/property-types/`

Creates a new property type.

**Request Body:**
```json
{
  "name": "Backwater & Scenic",
  "description": "Properties located near backwaters, lakes, rivers, and scenic natural landscapes",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Backwater & Scenic",
  "description": "Properties located near backwaters, lakes, rivers, and scenic natural landscapes",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 2. Get All Property Types

**GET** `/api/v1/property-types/`

Retrieves all property types with optional filtering.

**Query Parameters:**
- `active_only` (boolean, default: true): Return only active property types

**Response:**
```json
{
  "property_types": [
    {
      "id": 1,
      "name": "Backwater & Scenic",
      "description": "Properties located near backwaters, lakes, rivers, and scenic natural landscapes",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### 3. Get Property Type by ID

**GET** `/api/v1/property-types/{type_id}`

Retrieves a specific property type by ID.

**Response:**
```json
{
  "id": 1,
  "name": "Backwater & Scenic",
  "description": "Properties located near backwaters, lakes, rivers, and scenic natural landscapes",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. Update Property Type

**PUT** `/api/v1/property-types/{type_id}`

Updates an existing property type.

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "is_active": false
}
```

**Response:** Updated property type object

### 5. Delete Property Type

**DELETE** `/api/v1/property-types/{type_id}`

Soft deletes a property type by setting `is_active` to false.

**Response:** 204 No Content

## Property Search API

### Search Properties

**POST** `/api/v1/properties/search`

Searches properties with advanced filtering and pagination.

**Request Body:**
```json
{
  "user_id": 123,
  "property_type_id": [1, 2],
  "property_type_name": ["Backwater & Scenic", "Hill Stations & Wildlife"],
  "status": ["ACTIVE", "INACTIVE"],
  "page": 1,
  "search_query": "lake view",
  "date_filter": {
    "from_date": 1640995200000,
    "to_date": 1640995200000
  },
  "limit": 20
}
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 123,
      "property_name": "Lake View Villa",
      "property_type_id": 1,
      "property_type_name": "Backwater & Scenic",
      "status": "ACTIVE",
      "classification": "GOLD",
      "progress_step": 9,
      "is_verified": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

## Property Status Values

Properties now have a status field with the following values:
- `ACTIVE`: Property is active and available
- `INACTIVE`: Property is temporarily inactive
- `BLOCKED`: Property is blocked by admin
- `DELETED`: Property is soft deleted

## Database Changes

The following new tables and fields have been added:

### New Table: `property_types`
- `id` (Primary Key)
- `name` (Unique, indexed)
- `description`
- `is_active`
- `created_at`
- `updated_at`

### Updated Table: `properties`
- Added `property_type_id` (Foreign Key to property_types.id)
- Added `status` (Enum: ACTIVE, INACTIVE, BLOCKED, DELETED)

## Seeding Initial Data

Run the seeding script to populate initial property types:

```bash
python seed_property_types.py
```

This will create 10 predefined property types including:
- Backwater & Scenic
- Hill Stations & Wildlife
- Beaches & Coastal
- Heritage & Cultural
- Adventure & Sports
- Wellness & Spa
- Business & Corporate
- Family & Kids
- Luxury & Premium
- Budget & Backpacker

## Usage Examples

### Creating a Property with Type
```json
{
  "user_id": 123,
  "property_name": "Mountain Retreat",
  "property_type_id": 2,
  "status": "ACTIVE"
}
```

### Searching Properties by Type
```json
{
  "property_type_id": [2, 5],
  "status": ["ACTIVE"],
  "page": 1,
  "limit": 10
}
```

### Filtering by Property Type Name
```json
{
  "property_type_name": ["Hill Stations & Wildlife", "Adventure & Sports"],
  "page": 1,
  "limit": 20
}
```

## Error Handling

The API includes comprehensive error handling:
- 400 Bad Request: Invalid input data
- 404 Not Found: Property type not found
- 500 Internal Server Error: Server-side errors

## Authentication & Authorization

All endpoints require proper authentication. Property type management endpoints are typically restricted to admin users.

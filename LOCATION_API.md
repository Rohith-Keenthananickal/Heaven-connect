# Location API Documentation

This document describes the API endpoints for managing districts and grama panchayats in the Heaven Connect platform.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require authentication unless specified otherwise.

## Districts API

### 1. Create District
**POST** `/districts/`

Creates a new district.

**Request Body:**
```json
{
  "name": "Thiruvananthapuram",
  "state": "Kerala",
  "code": "TVM",
  "description": "Capital district of Kerala",
  "is_active": true
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Thiruvananthapuram",
  "state": "Kerala",
  "code": "TVM",
  "description": "Capital district of Kerala",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 2. Get All Districts
**GET** `/districts/`

Retrieves all districts with optional filtering and pagination.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Number of records to return (default: 100, max: 1000)
- `state` (string, optional): Filter by state
- `search` (string, optional): Search by name or state
- `active_only` (boolean, optional): Return only active districts (default: true)

**Example Requests:**
```
GET /districts/?state=Kerala
GET /districts/?search=Thiruvananthapuram
GET /districts/?skip=0&limit=20
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Thiruvananthapuram",
    "state": "Kerala",
    "code": "TVM",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### 3. Get District by ID
**GET** `/districts/{district_id}`

Retrieves a specific district by ID.

**Response:**
```json
{
  "id": 1,
  "name": "Thiruvananthapuram",
  "state": "Kerala",
  "code": "TVM",
  "description": "Capital district of Kerala",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. Get District with Panchayats
**GET** `/districts/{district_id}/with-panchayats`

Retrieves a district with all its grama panchayats.

**Response:**
```json
{
  "id": 1,
  "name": "Thiruvananthapuram",
  "state": "Kerala",
  "code": "TVM",
  "description": "Capital district of Kerala",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "grama_panchayats": [
    {
      "id": 1,
      "name": "Kovalam",
      "district_id": 1,
      "code": "KVL",
      "description": "Famous beach destination",
      "population": 15000,
      "area_sq_km": 25.5,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 5. Update District
**PUT** `/districts/{district_id}`

Updates an existing district.

**Request Body:**
```json
{
  "name": "Thiruvananthapuram Updated",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Thiruvananthapuram Updated",
  "state": "Kerala",
  "code": "TVM",
  "description": "Updated description",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### 6. Delete District
**DELETE** `/districts/{district_id}`

Soft deletes a district by setting `is_active` to false.

**Response:** 204 No Content

## Grama Panchayats API

### 1. Create Grama Panchayat
**POST** `/grama-panchayats/`

Creates a new grama panchayat.

**Request Body:**
```json
{
  "name": "Kovalam",
  "district_id": 1,
  "code": "KVL",
  "description": "Famous beach destination",
  "population": 15000,
  "area_sq_km": 25.5,
  "is_active": true
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Kovalam",
  "district_id": 1,
  "code": "KVL",
  "description": "Famous beach destination",
  "population": 15000,
  "area_sq_km": 25.5,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 2. Get All Grama Panchayats
**GET** `/grama-panchayats/`

Retrieves all grama panchayats with optional filtering and pagination.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Number of records to return (default: 100, max: 1000)
- `district_id` (int, optional): Filter by district ID
- `search` (string, optional): Search by name
- `active_only` (boolean, optional): Return only active panchayats (default: true)
- `min_population` (int, optional): Minimum population filter
- `max_population` (int, optional): Maximum population filter

**Example Requests:**
```
GET /grama-panchayats/?district_id=1
GET /grama-panchayats/?search=Kovalam
GET /grama-panchayats/?min_population=10000&max_population=20000
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Kovalam",
    "district_id": 1,
    "code": "KVL",
    "population": 15000,
    "area_sq_km": 25.5,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### 3. Get Grama Panchayat by ID
**GET** `/grama-panchayats/{panchayat_id}`

Retrieves a specific grama panchayat by ID.

**Response:**
```json
{
  "id": 1,
  "name": "Kovalam",
  "district_id": 1,
  "code": "KVL",
  "description": "Famous beach destination",
  "population": 15000,
  "area_sq_km": 25.5,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. Get Grama Panchayat with District
**GET** `/grama-panchayats/{panchayat_id}/with-district`

Retrieves a grama panchayat with its district information.

**Response:**
```json
{
  "id": 1,
  "name": "Kovalam",
  "district_id": 1,
  "code": "KVL",
  "description": "Famous beach destination",
  "population": 15000,
  "area_sq_km": 25.5,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "district": {
    "id": 1,
    "name": "Thiruvananthapuram",
    "state": "Kerala",
    "code": "TVM",
    "description": "Capital district of Kerala",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 5. Update Grama Panchayat
**PUT** `/grama-panchayats/{panchayat_id}`

Updates an existing grama panchayat.

**Request Body:**
```json
{
  "name": "Kovalam Updated",
  "population": 16000
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Kovalam Updated",
  "district_id": 1,
  "code": "KVL",
  "description": "Famous beach destination",
  "population": 16000,
  "area_sq_km": 25.5,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### 6. Delete Grama Panchayat
**DELETE** `/grama-panchayats/{panchayat_id}`

Soft deletes a grama panchayat by setting `is_active` to false.

**Response:** 204 No Content

### 7. Get Panchayats by District
**GET** `/grama-panchayats/district/{district_id}`

Retrieves all grama panchayats for a specific district.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Number of records to return (default: 100, max: 1000)
- `active_only` (boolean, optional): Return only active panchayats (default: true)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Kovalam",
    "district_id": 1,
    "code": "KVL",
    "population": 15000,
    "area_sq_km": 25.5,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "name": "Varkala",
    "district_id": 1,
    "code": "VRK",
    "population": 12000,
    "area_sq_km": 20.0,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "District with this code already exists"
}
```

### 404 Not Found
```json
{
  "detail": "District not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to create district: Database connection error"
}
```

## Data Models

### District
- `id` (int): Primary key
- `name` (string): District name (unique)
- `state` (string): State where district is located
- `code` (string, optional): Official district code (unique)
- `description` (text, optional): Description of the district
- `is_active` (boolean): Whether the district is active
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

### Grama Panchayat
- `id` (int): Primary key
- `name` (string): Panchayat name
- `district_id` (int): Foreign key to districts table
- `code` (string, optional): Official panchayat code (unique)
- `description` (text, optional): Description of the panchayat
- `population` (int, optional): Population count
- `area_sq_km` (float, optional): Area in square kilometers
- `is_active` (boolean): Whether the panchayat is active
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

## Database Schema

```sql
-- Districts table
CREATE TABLE districts (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    state VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_districts_name (name),
    INDEX idx_districts_state (state),
    INDEX idx_districts_code (code),
    INDEX idx_districts_active (is_active)
);

-- Grama Panchayats table
CREATE TABLE grama_panchayats (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    district_id INTEGER NOT NULL,
    code VARCHAR(20) UNIQUE,
    description TEXT,
    population INTEGER,
    area_sq_km FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
    INDEX idx_grama_panchayats_name (name),
    INDEX idx_grama_panchayats_district_id (district_id),
    INDEX idx_grama_panchayats_code (code),
    INDEX idx_grama_panchayats_active (is_active)
);
```

## Usage Examples

### Python Requests Example
```python
import requests

# Create a district
district_data = {
    "name": "New District",
    "state": "Karnataka",
    "code": "NEW",
    "description": "A new district"
}

response = requests.post(
    "http://localhost:8000/api/v1/districts/",
    json=district_data
)
print(response.json())

# Get all districts in Karnataka
response = requests.get(
    "http://localhost:8000/api/v1/districts/?state=Karnataka"
)
print(response.json())
```

### cURL Examples
```bash
# Create a district
curl -X POST "http://localhost:8000/api/v1/districts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New District",
    "state": "Karnataka",
    "code": "NEW",
    "description": "A new district"
  }'

# Get all districts
curl "http://localhost:8000/api/v1/districts/"

# Get districts in a specific state
curl "http://localhost:8000/api/v1/districts/?state=Kerala"
```

## Notes

1. **Soft Delete**: Both districts and grama panchayats use soft delete (setting `is_active` to false) instead of hard delete.
2. **Cascade Delete**: When a district is deleted, all its grama panchayats are automatically deleted.
3. **Unique Constraints**: District names and codes must be unique across the system.
4. **Indexing**: Proper database indexes are created for optimal query performance.
5. **Validation**: Input validation is performed on all endpoints to ensure data integrity.

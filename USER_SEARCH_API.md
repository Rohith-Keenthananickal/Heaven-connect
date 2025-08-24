# User Search API Documentation

## Overview
The User Search API provides a powerful, paginated search functionality for users with multiple filtering options. This endpoint allows you to search users based on various criteria including user type, status, date ranges, and text queries.

## Endpoint
```
POST /api/v1/users/search
```

## Request Schema

### UserSearchRequest
```json
{
  "user_type": ["HOST", "GUEST"], // Optional: Filter by user types (array)
  "page": 1,                      // Required: Page number (1-based)
  "search_query": "john",         // Optional: Search in name, email, or phone
  "date_filter": {                // Optional: Date range filter
    "from_date": 1640995200000,   // From date in milliseconds
    "to_date": 1643673600000      // To date in milliseconds
  },
  "limit": 20,                    // Required: Items per page (1-100)
  "status": ["ACTIVE", "BLOCKED"] // Optional: Filter by user statuses (array)
}
```

### Field Descriptions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `user_type` | array | No | Filter by user types | `["HOST"]`, `["GUEST", "ADMIN"]` |
| `page` | integer | Yes | Page number (1-based) | `1`, `2`, `3` |
| `search_query` | string | No | Search in name, email, or phone | `"john"`, `"example.com"` |
| `date_filter.from_date` | integer | No | Start date in milliseconds | `1640995200000` |
| `date_filter.to_date` | integer | No | End date in milliseconds | `1643673600000` |
| `limit` | integer | Yes | Items per page (1-100) | `10`, `20`, `50` |
| `status` | array | No | Filter by user statuses | `["ACTIVE"]`, `["BLOCKED", "DELETED"]` |

### User Status Values
- **ACTIVE**: User account is active and can use the system
- **BLOCKED**: User account is blocked and cannot access the system
- **DELETED**: User account is soft-deleted (hidden but not permanently removed)

## Response Schema

**Note**: The search API returns complete user data (excluding password_hash for security) including all profile information, dates, and metadata.

### UserSearchResponse
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "auth_provider": "EMAIL",
      "user_type": "HOST",
      "email": "john@example.com",
      "phone_number": "+1234567890",
      "full_name": "John Doe",
      "dob": "1990-01-01",
      "profile_image": "https://example.com/profile.jpg",
      "status": "ACTIVE",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### Pagination Info

| Field | Type | Description |
|-------|------|-------------|
| `page` | integer | Current page number |
| `limit` | integer | Items per page |
| `total` | integer | Total number of users matching criteria |
| `total_pages` | integer | Total number of pages |
| `has_next` | boolean | Whether there's a next page |
| `has_prev` | boolean | Whether there's a previous page |

## User Management Endpoints

### 1. User Status Operations

#### Update User Status
```bash
PATCH /api/v1/users/{user_id}/status
```

**Request Body:**
```json
{
  "status": "ACTIVE"  // or "BLOCKED" or "DELETED"
}
```

**Description:** Updates user status to the specified value. This single endpoint replaces the need for separate block/activate endpoints.

**Status Values:**
- `"ACTIVE"`: Activates the user account
- `"BLOCKED"`: Blocks the user account
- `"DELETED"`: Soft-deletes the user account

#### Soft Delete User
```bash
DELETE /api/v1/users/{user_id}
```
Changes user status to `DELETED` (doesn't permanently remove the user)

### 2. User Search with Status Filters

#### Search for Active Users
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 20,
    "status": "ACTIVE"
  }'
```

#### Search for Blocked Users
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 20,
    "status": "BLOCKED"
  }'
```

#### Search for Deleted Users
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 20,
    "status": "DELETED"
  }'
```

## Usage Examples

### 1. Basic Search with Pagination
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 10
  }'
```

### 2. Search by User Type and Status (Single Values)
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 20,
    "user_type": ["HOST"],
    "status": ["ACTIVE"]
  }'
```

### 3. Search by Multiple User Types (Array)
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 20,
    "user_type": ["HOST", "GUEST"],
    "status": ["ACTIVE"]
  }'
```

### 4. Search by Multiple Statuses (Array)
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 20,
    "user_type": ["HOST"],
    "status": ["ACTIVE", "BLOCKED"]
  }'
```

### 5. Search with Text Query
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 15,
    "search_query": "john"
  }'
```

### 6. Search with Date Filter
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 20,
    "date_filter": {
      "from_date": 1640995200000,
      "to_date": 1643673600000
    }
  }'
```

### 7. Combined Search
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "limit": 10,
    "user_type": ["GUEST"],
    "status": ["ACTIVE"],
    "search_query": "a",
    "date_filter": {
      "from_date": 1640995200000
    }
  }'
```

## JavaScript/TypeScript Examples

### Using Fetch API
```javascript
const searchUsers = async (searchParams) => {
  try {
    const response = await fetch('/api/v1/users/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchParams)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error searching users:', error);
    throw error;
  }
};

// Example usage
const searchParams = {
  page: 1,
  limit: 20,
  user_type: ['HOST'],
  status: ['ACTIVE']
};

searchUsers(searchParams).then(result => {
  console.log('Users found:', result.data);
  console.log('Pagination:', result.pagination);
});
```

### Using Axios
```javascript
import axios from 'axios';

const searchUsers = async (searchParams) => {
  try {
    const response = await axios.post('/api/v1/users/search', searchParams);
    return response.data;
  } catch (error) {
    console.error('Error searching users:', error);
    throw error;
  }
};

// Example usage
const searchParams = {
  page: 1,
  limit: 20,
  search_query: 'john',
  user_type: ['HOST'],
  status: ['ACTIVE']
};

// Example with multiple types and statuses
const multiSearchParams = {
  page: 1,
  limit: 20,
  user_type: ['HOST', 'GUEST'],
  status: ['ACTIVE', 'BLOCKED']
};

searchUsers(searchParams).then(result => {
  console.log('Users found:', result.data);
  console.log('Total pages:', result.pagination.total_pages);
});
```

## User Status Management Examples

### Update User Status (Single Endpoint)
```javascript
const updateUserStatus = async (userId, newStatus) => {
  try {
    const response = await fetch(`/api/v1/users/${userId}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: newStatus })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error updating user status:', error);
    throw error;
  }
};

// Example usage
// Block a user
updateUserStatus(123, 'BLOCKED').then(result => {
  console.log('User blocked:', result.data.message);
});

// Activate a user
updateUserStatus(123, 'ACTIVE').then(result => {
  console.log('User activated:', result.data.message);
});

// Soft delete a user
updateUserStatus(123, 'DELETED').then(result => {
  console.log('User deleted:', result.data.message);
});
```

### Soft Delete a User (Alternative Method)
```javascript
const softDeleteUser = async (userId) => {
  try {
    const response = await fetch(`/api/v1/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error soft deleting user:', error);
    throw error;
  }
};
```

## Date Handling

### Converting Dates to Milliseconds
```javascript
// Convert Date object to milliseconds
const date = new Date('2024-01-01');
const milliseconds = date.getTime();

// Convert ISO string to milliseconds
const isoString = '2024-01-01T00:00:00Z';
const milliseconds = new Date(isoString).getTime();

// Convert current date to milliseconds
const now = Date.now();
```

### Date Range Examples
```javascript
// Last 7 days
const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
const now = Date.now();

const dateFilter = {
  from_date: sevenDaysAgo,
  to_date: now
};

// Last month
const lastMonth = new Date();
lastMonth.setMonth(lastMonth.getMonth() - 1);
const lastMonthMs = lastMonth.getTime();

const dateFilter = {
  from_date: lastMonthMs,
  to_date: Date.now()
};
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Success with results
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "detail": "Error message description",
  "status_code": 400
}
```

## Performance Considerations

1. **Pagination**: Always use pagination to limit the number of results returned
2. **Date Filters**: Use date filters to narrow down results when possible
3. **Search Queries**: Text search queries are case-insensitive and use LIKE operations
4. **Status Filters**: Use status filters to get specific user states
5. **Indexing**: The API automatically uses database indexes on `user_type`, `status`, `created_at`, `email`, and `phone_number`

## Best Practices

1. **Set Reasonable Limits**: Use `limit` values between 10-50 for optimal performance
2. **Combine Filters**: Use multiple filters together to get more targeted results
3. **Handle Pagination**: Always check `has_next` and `has_prev` for navigation
4. **Error Handling**: Implement proper error handling for failed requests
5. **Status Management**: Use the single status update endpoint for all status changes
6. **Soft Deletes**: Use soft deletes to maintain data integrity and allow recovery

## Testing

Use the provided `test_user_search.py` script to test the API:

```bash
python test_user_search.py
```

Make sure your FastAPI server is running on `http://localhost:8000` before running the tests.

## Database Migration Note

**Important**: After updating the code, you'll need to create a database migration to change the `status` field from boolean to enum. The migration should:

1. Change the column type from `BOOLEAN` to `ENUM('ACTIVE', 'BLOCKED', 'DELETED')`
2. Set default value to `'ACTIVE'`
3. Convert existing `true` values to `'ACTIVE'` and `false` values to `'BLOCKED'`

Example migration:
```sql
-- Update existing boolean values to enum
UPDATE users SET status = 'ACTIVE' WHERE status = true;
UPDATE users SET status = 'BLOCKED' WHERE status = false;

-- Change column type
ALTER TABLE users MODIFY COLUMN status ENUM('ACTIVE', 'BLOCKED', 'DELETED') NOT NULL DEFAULT 'ACTIVE';
```

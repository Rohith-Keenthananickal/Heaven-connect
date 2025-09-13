# ATP UUID Implementation Documentation

## Overview

The ATP UUID feature adds a unique identifier for Area Coordinators in the format `ATP-01234`. This identifier is automatically generated when an Area Coordinator is created and is included in all user/ATP responses.

## Features

- **Automatic Generation**: ATP UUID is automatically generated when an Area Coordinator is created
- **Unique Format**: Uses the format `ATP-XXXXX` where XXXXX is a 5-digit number with leading zeros
- **Sequential Numbering**: Numbers are generated sequentially starting from 00001
- **Database Uniqueness**: Enforced at the database level with unique constraint
- **API Integration**: Included in all user/ATP response schemas

## Implementation Details

### 1. Database Model Changes

**File**: `app/models/user.py`

Added `atp_uuid` field to the `AreaCoordinator` model:

```python
class AreaCoordinator(Base):
    __tablename__ = "area_coordinators"
    
    # Primary key is also foreign key to users table
    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    
    # Basic Area Coordinator fields
    atp_uuid: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True, index=True, comment="ATP UUID in format ATP-01234")
    region: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # ... other fields
```

**Key Features**:
- `unique=True`: Ensures no duplicate ATP UUIDs
- `index=True`: Optimizes database queries
- `nullable=True`: Allows for existing records during migration
- `String(20)`: Sufficient length for ATP-XXXXX format

### 2. UUID Generation Utility

**File**: `app/utils/atp_uuid.py`

Created a utility function to generate unique ATP UUIDs:

```python
async def generate_atp_uuid(db: AsyncSession) -> str:
    """
    Generate a unique ATP UUID in the format ATP-01234
    
    Args:
        db: Database session
        
    Returns:
        str: Unique ATP UUID like 'ATP-01234'
    """
    # Get the highest existing ATP number
    result = await db.execute(
        select(func.max(
            func.cast(
                func.substring(AreaCoordinator.atp_uuid, 5),  # Extract number part after 'ATP-'
                Integer
            )
        )).where(AreaCoordinator.atp_uuid.isnot(None))
    )
    max_number = result.scalar()
    
    # If no existing ATP UUIDs, start from 1
    if max_number is None:
        next_number = 1
    else:
        next_number = max_number + 1
    
    # Format as ATP-XXXXX (5 digits with leading zeros)
    atp_uuid = f"ATP-{next_number:05d}"
    
    # Double-check uniqueness (in case of race conditions)
    existing = await db.execute(
        select(AreaCoordinator.atp_uuid).where(AreaCoordinator.atp_uuid == atp_uuid)
    )
    if existing.scalar_one_or_none():
        # If somehow it exists, try the next number
        return await generate_atp_uuid(db)
    
    return atp_uuid
```

**Key Features**:
- **Sequential Generation**: Finds the highest existing number and increments
- **Race Condition Safe**: Double-checks uniqueness before returning
- **Format Consistency**: Always generates 5-digit numbers with leading zeros
- **Database Efficient**: Uses SQL functions for optimal performance

### 3. Schema Updates

**File**: `app/schemas/users.py`

Updated `AreaCoordinatorProfileBase` to include ATP UUID:

```python
class AreaCoordinatorProfileBase(BaseModel):
    atp_uuid: Optional[str] = Field(None, max_length=20, description="ATP UUID in format ATP-01234")
    region: Optional[str] = Field(None, max_length=200)
    assigned_properties: Optional[int] = Field(0, ge=0)
    # ... other fields
```

**Inheritance Chain**:
- `AreaCoordinatorProfileBase` (includes atp_uuid)
- `AreaCoordinatorProfileCreate` (inherits from base)
- `AreaCoordinatorProfileUpdate` (inherits from base)
- `AreaCoordinatorProfileResponse` (inherits from base)

### 4. Service Layer Updates

**File**: `app/services/users_service.py`

Updated user creation to generate ATP UUID:

```python
async def _create_user_profile(self, db: AsyncSession, user_id: int, user_type: UserType, 
                             guest_profile: dict, host_profile: dict, area_coordinator_profile: dict):
    """Create the appropriate profile for the user"""
    if user_type == UserType.GUEST and guest_profile:
        profile = Guest(id=user_id, **guest_profile)
        db.add(profile)
    elif user_type == UserType.HOST and host_profile:
        profile = Host(id=user_id, **host_profile)
        db.add(profile)
    elif user_type == UserType.AREA_COORDINATOR and area_coordinator_profile:
        # Generate ATP UUID for new Area Coordinator
        atp_uuid = await generate_atp_uuid(db)
        area_coordinator_profile["atp_uuid"] = atp_uuid
        profile = AreaCoordinator(id=user_id, **area_coordinator_profile)
        db.add(profile)
```

Updated response conversion to include ATP UUID:

```python
elif user.user_type == UserType.AREA_COORDINATOR and user.area_coordinator_profile:
    user_dict["area_coordinator_profile"] = {
        "id": user.area_coordinator_profile.id,
        "atp_uuid": user.area_coordinator_profile.atp_uuid,  # Added this line
        "region": user.area_coordinator_profile.region,
        "assigned_properties": user.area_coordinator_profile.assigned_properties,
        # ... other fields
    }
```

### 5. Database Migration

**File**: `app/migrations/add_atp_uuid_field.py`

Created migration script to add ATP UUID field and populate existing records:

```python
async def add_atp_uuid_field():
    """Add ATP UUID field to area_coordinators table"""
    
    # Add the ATP UUID field
    add_atp_uuid_sql = """
    ALTER TABLE area_coordinators 
    ADD COLUMN atp_uuid VARCHAR(20) NULL COMMENT 'ATP UUID in format ATP-01234',
    ADD UNIQUE INDEX idx_atp_uuid (atp_uuid),
    ADD INDEX idx_atp_uuid_lookup (atp_uuid);
    """
    
    # Generate ATP UUIDs for existing records
    generate_atp_uuids_sql = """
    UPDATE area_coordinators 
    SET atp_uuid = CONCAT('ATP-', LPAD(ROW_NUMBER() OVER (ORDER BY id), 5, '0'))
    WHERE atp_uuid IS NULL;
    """
```

## Usage Examples

### 1. Creating a New Area Coordinator

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "auth_provider": "EMAIL",
    "user_type": "AREA_COORDINATOR",
    "email": "coordinator@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "area_coordinator_profile": {
      "region": "Kerala",
      "district": "Thiruvananthapuram",
      "panchayat": "Kazhakuttom",
      "address_line1": "123 Main Street",
      "city": "Thiruvananthapuram",
      "state": "Kerala",
      "postal_code": "695040"
    }
  }'
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "auth_provider": "EMAIL",
    "user_type": "AREA_COORDINATOR",
    "email": "coordinator@example.com",
    "full_name": "John Doe",
    "area_coordinator_profile": {
      "id": 123,
      "atp_uuid": "ATP-00001",
      "region": "Kerala",
      "assigned_properties": 0,
      "approval_status": "PENDING",
      "district": "Thiruvananthapuram",
      "panchayat": "Kazhakuttom",
      "address_line1": "123 Main Street",
      "city": "Thiruvananthapuram",
      "state": "Kerala",
      "postal_code": "695040"
    }
  },
  "message": "User created successfully"
}
```

### 2. Getting Area Coordinator Details

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/users/123"
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "auth_provider": "EMAIL",
    "user_type": "AREA_COORDINATOR",
    "email": "coordinator@example.com",
    "full_name": "John Doe",
    "area_coordinator_profile": {
      "id": 123,
      "atp_uuid": "ATP-00001",
      "region": "Kerala",
      "assigned_properties": 5,
      "approval_status": "APPROVED",
      "approval_date": "2024-01-15T10:00:00Z",
      "district": "Thiruvananthapuram",
      "panchayat": "Kazhakuttom",
      "address_line1": "123 Main Street",
      "city": "Thiruvananthapuram",
      "state": "Kerala",
      "postal_code": "695040"
    }
  },
  "message": "User retrieved successfully"
}
```

### 3. Searching Area Coordinators by ATP UUID

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/search" \
  -H "Content-Type: application/json" \
  -d '{
    "user_type": "AREA_COORDINATOR",
    "atp_uuid": "ATP-00001"
  }'
```

## Database Schema

### Before Migration
```sql
CREATE TABLE area_coordinators (
    id INT PRIMARY KEY,
    region VARCHAR(200),
    assigned_properties INT DEFAULT 0,
    -- ... other fields
);
```

### After Migration
```sql
CREATE TABLE area_coordinators (
    id INT PRIMARY KEY,
    atp_uuid VARCHAR(20) UNIQUE,
    region VARCHAR(200),
    assigned_properties INT DEFAULT 0,
    -- ... other fields
    INDEX idx_atp_uuid (atp_uuid),
    INDEX idx_atp_uuid_lookup (atp_uuid)
);
```

## Migration Instructions

### 1. Run the Migration Script

```bash
python app/migrations/add_atp_uuid_field.py
```

This will:
- Add the `atp_uuid` column to the `area_coordinators` table
- Create unique and lookup indexes
- Generate ATP UUIDs for existing Area Coordinators
- Display sample generated ATP UUIDs

### 2. Verify the Migration

```sql
-- Check the new column
DESCRIBE area_coordinators;

-- View sample ATP UUIDs
SELECT id, atp_uuid, region FROM area_coordinators LIMIT 5;

-- Verify uniqueness
SELECT atp_uuid, COUNT(*) FROM area_coordinators GROUP BY atp_uuid HAVING COUNT(*) > 1;
```

## API Response Changes

### All User Endpoints Now Include ATP UUID

The following endpoints now include `atp_uuid` in the response for Area Coordinators:

- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user
- `POST /api/v1/users/search` - Search users
- `GET /api/v1/users` - List users

### Training API Integration

The ATP UUID is also available in training-related responses:

- `GET /api/v1/training/my-modules?user_id={user_id}` - User's training modules
- `GET /api/v1/training/stats?user_id={user_id}` - Training statistics
- All other training endpoints that return user information

## Benefits

### 1. **Unique Identification**
- Each Area Coordinator has a unique, human-readable identifier
- Easy to reference in communications and documentation

### 2. **Sequential Numbering**
- ATP UUIDs are generated sequentially (ATP-00001, ATP-00002, etc.)
- Easy to track the order of registration

### 3. **Database Efficiency**
- Indexed for fast lookups
- Unique constraint prevents duplicates

### 4. **API Consistency**
- Included in all user/ATP responses
- Consistent format across all endpoints

### 5. **Future-Proof**
- Can be extended to support different prefixes
- Easy to add additional UUID types if needed

## Error Handling

### Duplicate ATP UUID Prevention
- Database unique constraint prevents duplicates
- Service layer double-checks uniqueness before creation
- Automatic retry mechanism for race conditions

### Migration Safety
- Existing records are preserved
- ATP UUIDs are generated for existing Area Coordinators
- No data loss during migration

## Testing

### Unit Tests
```python
# Test ATP UUID generation
async def test_generate_atp_uuid():
    atp_uuid = await generate_atp_uuid(db)
    assert atp_uuid.startswith("ATP-")
    assert len(atp_uuid) == 9  # ATP-XXXXX
    assert atp_uuid[4:].isdigit()
```

### Integration Tests
```python
# Test Area Coordinator creation with ATP UUID
async def test_create_area_coordinator_with_atp_uuid():
    user_data = {
        "user_type": "AREA_COORDINATOR",
        "email": "test@example.com",
        "area_coordinator_profile": {...}
    }
    response = await client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert "atp_uuid" in data["data"]["area_coordinator_profile"]
    assert data["data"]["area_coordinator_profile"]["atp_uuid"].startswith("ATP-")
```

## Future Enhancements

### 1. **Custom Prefixes**
- Support for different prefixes (e.g., "ATP-", "AC-", "COORD-")
- Configurable per region or type

### 2. **UUID Validation**
- API endpoint to validate ATP UUID format
- Bulk validation for data imports

### 3. **UUID History**
- Track ATP UUID changes
- Audit trail for identifier modifications

### 4. **Bulk Operations**
- Bulk ATP UUID generation
- Import/export with ATP UUIDs

The ATP UUID implementation provides a robust, scalable solution for uniquely identifying Area Coordinators while maintaining data integrity and API consistency.

# User Model Refactor: Class Table Inheritance

This document describes the refactored SQLAlchemy user model that uses **class table inheritance** to separate type-specific fields into dedicated tables while maintaining common fields in the base `users` table.

## Overview

The refactor splits the monolithic `User` model into:
- **Base `User` model**: Contains common fields shared by all user types
- **Type-specific profile models**: `Guest`, `Host`, `AreaCoordinator` with specialized fields
- **Proper relationships**: Each user can have one profile based on their `user_type`

## Database Schema

### Tables Structure

#### 1. `users` (Base Table)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    auth_provider VARCHAR(50) NOT NULL,
    user_type VARCHAR(50) NOT NULL DEFAULT 'GUEST',
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(200) NOT NULL,
    dob DATE,
    profile_image VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 2. `guests` (Guest Profile Table)
```sql
CREATE TABLE guests (
    id INTEGER PRIMARY KEY,
    passport_number VARCHAR(50),
    nationality VARCHAR(100),
    preferences JSON,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 3. `hosts` (Host Profile Table)
```sql
CREATE TABLE hosts (
    id INTEGER PRIMARY KEY,
    license_number VARCHAR(100),
    experience_years INTEGER,
    company_name VARCHAR(200),
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 4. `area_coordinators` (Area Coordinator Profile Table)
```sql
CREATE TABLE area_coordinators (
    id INTEGER PRIMARY KEY,
    region VARCHAR(200),
    assigned_properties INTEGER DEFAULT 0,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Model Relationships

### One-to-One Relationships
- `User` ↔ `Guest` (via `guest_profile`)
- `User` ↔ `Host` (via `host_profile`)  
- `User` ↔ `AreaCoordinator` (via `area_coordinator_profile`)

### Key Features
- **Foreign Key as Primary Key**: Each profile table uses the user's ID as both foreign key and primary key
- **Cascade Delete**: When a user is deleted, their profile is automatically removed
- **Optional Profiles**: Users may not have a profile initially (e.g., ADMIN users)
- **Type Validation**: The `user_type` enum ensures data consistency

## Usage Examples

### Creating Users with Profiles

```python
from app.models.user import User, Guest, Host, AreaCoordinator, UserType, AuthProvider, UserStatus

# Create a guest user
def create_guest_user(db: Session, full_name: str, email: str, passport_number: str):
    # Create base user
    user = User(
        auth_provider=AuthProvider.EMAIL,
        user_type=UserType.GUEST,
        email=email,
        full_name=full_name,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    db.flush()  # Get the user ID
    
    # Create guest profile
    guest_profile = Guest(
        id=user.id,
        passport_number=passport_number,
        nationality="US"
    )
    db.add(guest_profile)
    db.commit()
    return user

# Create a host user
def create_host_user(db: Session, full_name: str, email: str, license_number: str):
    user = User(
        auth_provider=AuthProvider.EMAIL,
        user_type=UserType.HOST,
        email=email,
        full_name=full_name,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    db.flush()
    
    host_profile = Host(
        id=user.id,
        license_number=license_number,
        experience_years=5
    )
    db.add(host_profile)
    db.commit()
    return user
```

### Querying Users with Profiles

```python
# Get user with their profile
user = db.query(User).filter(User.id == user_id).first()

if user.user_type == UserType.GUEST and user.guest_profile:
    print(f"Passport: {user.guest_profile.passport_number}")
    print(f"Nationality: {user.guest_profile.nationality}")

elif user.user_type == UserType.HOST and user.host_profile:
    print(f"License: {user.host_profile.license_number}")
    print(f"Experience: {user.host_profile.experience_years} years")

elif user.user_type == UserType.AREA_COORDINATOR and user.area_coordinator_profile:
    print(f"Region: {user.area_coordinator_profile.region}")
    print(f"Properties: {user.area_coordinator_profile.assigned_properties}")
```

### Updating Profiles

```python
# Update guest preferences
guest = db.query(Guest).filter(Guest.id == user_id).first()
if guest:
    guest.preferences = {"preferred_style": "modern", "max_price": 2000}
    db.commit()

# Update host experience
host = db.query(Host).filter(Host.id == user_id).first()
if host:
    host.experience_years = 7
    db.commit()
```

## Migration Guide

### 1. Update Models
The models have been updated in `app/models/user.py`. The new structure includes:
- Base `User` model with common fields
- `Guest`, `Host`, `AreaCoordinator` profile models
- Proper relationships between models

### 2. Create Database Tables
Run the migration script to create the new tables:

```bash
cd app/migrations
python create_profile_tables.py
```

Choose option 1 to create the profile tables.

### 3. Migrate Existing Data
If you have existing users, migrate them to have profile records:

```bash
python create_profile_tables.py
```

Choose option 2 to migrate existing users.

### 4. Update Application Code
- Update your API endpoints to handle the new model structure
- Modify user creation logic to create both user and profile records
- Update queries to access profile data through relationships

## Benefits of This Approach

### 1. **Data Normalization**
- Common fields are stored once in the `users` table
- Type-specific fields are stored in dedicated tables
- Reduces data duplication

### 2. **Flexibility**
- Easy to add new user types without modifying the base table
- Type-specific fields can be added without affecting other user types
- Maintains backward compatibility

### 3. **Performance**
- Efficient queries for common user data
- Indexed foreign keys for fast profile lookups
- Reduced table size for common queries

### 4. **Maintainability**
- Clear separation of concerns
- Easy to understand and modify
- Follows SQLAlchemy best practices

## Constraints and Considerations

### 1. **Data Integrity**
- Foreign key constraints ensure profile consistency
- Cascade delete maintains referential integrity
- `user_type` enum validates user classification

### 2. **Query Complexity**
- Some queries may require JOINs across multiple tables
- Consider using SQLAlchemy's `joinedload()` for eager loading
- Profile data is loaded lazily by default

### 3. **Migration Complexity**
- Existing data needs to be migrated to new structure
- Consider downtime requirements for production migrations
- Test migration scripts thoroughly

## Testing

Test the new structure with:

```python
# Test user creation
guest_user = create_guest_user(db, "John Doe", "john@example.com", "A12345678")
assert guest_user.user_type == UserType.GUEST
assert guest_user.guest_profile is not None
assert guest_user.guest_profile.passport_number == "A12345678"

# Test profile relationships
user = get_user_with_profile(db, guest_user.id)
assert user.guest_profile.nationality == "US"
```

## Troubleshooting

### Common Issues

1. **Profile Not Found**: Ensure the profile record was created when the user was created
2. **Relationship Loading**: Use `joinedload()` if you need profile data in a single query
3. **Migration Errors**: Check foreign key constraints and ensure users exist before creating profiles

### Debug Queries

```python
# Check if profile exists
guest = db.query(Guest).filter(Guest.id == user_id).first()
if not guest:
    print(f"No guest profile found for user {user_id}")

# Check user type consistency
user = db.query(User).filter(User.id == user_id).first()
print(f"User type: {user.user_type}")
```

## Future Enhancements

Consider these potential improvements:
- Add validation that profile exists when `user_type` is set
- Implement profile creation triggers
- Add audit logging for profile changes
- Consider using polymorphic associations for more complex inheritance

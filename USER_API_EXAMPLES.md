# User API Examples: Profile-Based User Management

This document provides comprehensive examples of how to use the updated User API endpoints with the new profile-based structure.

## API Endpoints Overview

### Base Endpoints
- `POST /users/` - Create a new user with profile
- `GET /users/` - Get all users (with optional filtering)
- `GET /users/{user_id}` - Get specific user with profile
- `PUT /users/{user_id}` - Update user and profile
- `DELETE /users/{user_id}` - Soft delete user
- `PATCH /users/{user_id}/status` - Update user status

### Profile-Specific Endpoints
- `GET /users/{user_id}/profile` - Get user profile data
- `PATCH /users/{user_id}/profile` - Update user profile
- `GET /users/types/{user_type}` - Get users by type

### Area Coordinator Approval Endpoints
- `PATCH /users/{user_id}/approval` - Approve/reject area coordinator

### Bank Details Endpoints (Area Coordinators Only)
- `POST /users/{user_id}/bank-details` - Create bank details
- `GET /users/{user_id}/bank-details` - Get bank details
- `PUT /users/{user_id}/bank-details` - Update bank details
- `PATCH /users/{user_id}/bank-details/verify` - Verify bank details

## Creating Users

### 1. Create a Guest User

```json
POST /users/
{
  "auth_provider": "EMAIL",
  "user_type": "GUEST",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "full_name": "John Doe",
  "dob": "1990-05-15",
  "profile_image": "https://example.com/profile.jpg",
  "status": "ACTIVE",
  "password": "securepassword123",
  "guest_profile": {
    "passport_number": "A12345678",
    "nationality": "US",
    "preferences": {
      "preferred_style": "modern",
      "max_price": 2000,
      "amenities": ["wifi", "parking", "kitchen"],
      "location_preference": "downtown"
    }
  }
}
```

**Response:**
```json
{
  "id": 1,
  "auth_provider": "EMAIL",
  "user_type": "GUEST",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "full_name": "John Doe",
  "dob": "1990-05-15",
  "profile_image": "https://example.com/profile.jpg",
  "status": "ACTIVE",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "guest_profile": {
    "id": 1,
    "passport_number": "A12345678",
    "nationality": "US",
    "preferences": {
      "preferred_style": "modern",
      "max_price": 2000,
      "amenities": ["wifi", "parking", "kitchen"],
      "location_preference": "downtown"
    }
  },
  "host_profile": null,
  "area_coordinator_profile": null
}
```

### 2. Create a Host User

```json
POST /users/
{
  "auth_provider": "EMAIL",
  "user_type": "HOST",
  "email": "jane.smith@example.com",
  "phone_number": "+0987654321",
  "full_name": "Jane Smith",
  "dob": "1985-08-22",
  "profile_image": "https://example.com/jane.jpg",
  "status": "ACTIVE",
  "password": "hostpassword456",
  "host_profile": {
    "license_number": "HOST123456",
    "experience_years": 5,
    "company_name": "Smith Properties LLC"
  }
}
```

**Response:**
```json
{
  "id": 2,
  "auth_provider": "EMAIL",
  "user_type": "HOST",
  "email": "jane.smith@example.com",
  "phone_number": "+0987654321",
  "full_name": "Jane Smith",
  "dob": "1985-08-22",
  "profile_image": "https://example.com/jane.jpg",
  "status": "ACTIVE",
  "created_at": "2024-01-15T10:35:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "guest_profile": null,
  "host_profile": {
    "id": 2,
    "license_number": "HOST123456",
    "experience_years": 5,
    "company_name": "Smith Properties LLC"
  },
  "area_coordinator_profile": null
}
```

### 3. Create an Enhanced Area Coordinator User (Pending Approval)

```json
POST /users/
{
  "auth_provider": "EMAIL",
  "user_type": "AREA_COORDINATOR",
  "email": "bob.wilson@example.com",
  "phone_number": "+1122334455",
  "full_name": "Bob Wilson",
  "dob": "1978-12-10",
  "profile_image": "https://example.com/bob.jpg",
  "status": "ACTIVE",
  "password": "coordinator789",
  "area_coordinator_profile": {
    "region": "Downtown District",
    "assigned_properties": 0,
    "id_proof_type": "Aadhar",
    "id_proof_number": "123456789012",
    "pancard_number": "ABCDE1234F",
    "passport_size_photo": "https://example.com/bob-photo.jpg",
    "id_proof_document": "https://example.com/bob-aadhar.pdf",
    "address_proof_document": "https://example.com/bob-address.pdf",
    "district": "Mumbai Central",
    "panchayat": "Mumbai Central Ward",
    "address_line1": "123 Main Street",
    "address_line2": "Apartment 4B",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "emergency_contact": "+1199887766",
    "emergency_contact_name": "Alice Wilson",
    "emergency_contact_relationship": "Spouse"
  }
}
```

**Response:**
```json
{
  "id": 3,
  "auth_provider": "EMAIL",
  "user_type": "AREA_COORDINATOR",
  "email": "bob.wilson@example.com",
  "phone_number": "+1122334455",
  "full_name": "Bob Wilson",
  "dob": "1978-12-10",
  "profile_image": "https://example.com/bob.jpg",
  "status": "ACTIVE",
  "created_at": "2024-01-15T10:40:00Z",
  "updated_at": "2024-01-15T10:40:00Z",
  "guest_profile": null,
  "host_profile": null,
  "area_coordinator_profile": {
    "id": 3,
    "region": "Downtown District",
    "assigned_properties": 0,
    "approval_status": "PENDING",
    "approval_date": null,
    "approved_by": null,
    "rejection_reason": null,
    "id_proof_type": "Aadhar",
    "id_proof_number": "123456789012",
    "pancard_number": "ABCDE1234F",
    "passport_size_photo": "https://example.com/bob-photo.jpg",
    "id_proof_document": "https://example.com/bob-aadhar.pdf",
    "address_proof_document": "https://example.com/bob-address.pdf",
    "district": "Mumbai Central",
    "panchayat": "Mumbai Central Ward",
    "address_line1": "123 Main Street",
    "address_line2": "Apartment 4B",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "emergency_contact": "+1199887766",
    "emergency_contact_name": "Alice Wilson",
    "emergency_contact_relationship": "Spouse",
    "bank_details": null
  }
}
```

### 4. Create an Admin User (No Profile Required)

```json
POST /users/
{
  "auth_provider": "EMAIL",
  "user_type": "ADMIN",
  "email": "admin@example.com",
  "phone_number": "+1555666777",
  "full_name": "Admin User",
  "status": "ACTIVE",
  "password": "adminpassword123"
}
```

## Area Coordinator Approval Management

### 1. Approve Area Coordinator (Admin Only)

```json
PATCH /users/3/approval
{
  "approval_status": "APPROVED"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 3,
    "region": "Downtown District",
    "assigned_properties": 0,
    "approval_status": "APPROVED",
    "approval_date": "2024-01-15T11:00:00Z",
    "approved_by": 1,
    "rejection_reason": null,
    "id_proof_type": "Aadhar",
    "id_proof_number": "123456789012",
    "pancard_number": "ABCDE1234F",
    "passport_size_photo": "https://example.com/bob-photo.jpg",
    "id_proof_document": "https://example.com/bob-aadhar.pdf",
    "address_proof_document": "https://example.com/bob-address.pdf",
    "district": "Mumbai Central",
    "panchayat": "Mumbai Central Ward",
    "address_line1": "123 Main Street",
    "address_line2": "Apartment 4B",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "emergency_contact": "+1199887766",
    "emergency_contact_name": "Alice Wilson",
    "emergency_contact_relationship": "Spouse",
    "bank_details": null
  },
  "message": "Area coordinator approved successfully"
}
```

### 2. Reject Area Coordinator (Admin Only)

```json
PATCH /users/4/approval
{
  "approval_status": "REJECTED",
  "rejection_reason": "Incomplete documentation. Please provide valid address proof and ID verification documents."
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 4,
    "region": "Uptown District",
    "assigned_properties": 0,
    "approval_status": "REJECTED",
    "approval_date": "2024-01-15T11:15:00Z",
    "approved_by": 1,
    "rejection_reason": "Incomplete documentation. Please provide valid address proof and ID verification documents.",
    "id_proof_type": "PAN",
    "id_proof_number": "ABCDE1234F",
    "pancard_number": "ABCDE1234F",
    "passport_size_photo": "https://example.com/jane-photo.jpg",
    "id_proof_document": "https://example.com/jane-pan.pdf",
    "address_proof_document": null,
    "district": "Mumbai North",
    "panchayat": "Mumbai North Ward",
    "address_line1": "456 Oak Avenue",
    "address_line2": null,
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400002",
    "latitude": 19.0761,
    "longitude": 72.8778,
    "emergency_contact": "+1199887765",
    "emergency_contact_name": "John Smith",
    "emergency_contact_relationship": "Brother",
    "bank_details": null
  },
  "message": "Area coordinator rejected successfully"
}
```

## Bank Details Management

### 1. Create Bank Details for Area Coordinator

```json
POST /users/3/bank-details
{
  "bank_details": {
    "bank_name": "State Bank of India",
    "account_holder_name": "Bob Wilson",
    "account_number": "12345678901",
    "ifsc_code": "SBIN0001234",
    "branch_name": "Mumbai Central Branch",
    "branch_code": "MC001",
    "account_type": "Savings",
    "bank_passbook_image": "https://example.com/bob-passbook.jpg",
    "cancelled_cheque_image": "https://example.com/bob-cheque.jpg"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "area_coordinator_id": 3,
    "bank_name": "State Bank of India",
    "account_holder_name": "Bob Wilson",
    "account_number": "12345678901",
    "ifsc_code": "SBIN0001234",
    "branch_name": "Mumbai Central Branch",
    "branch_code": "MC001",
    "account_type": "Savings",
    "is_verified": false,
    "bank_passbook_image": "https://example.com/bob-passbook.jpg",
    "cancelled_cheque_image": "https://example.com/bob-cheque.jpg",
    "created_at": "2024-01-15T10:45:00Z",
    "updated_at": "2024-01-15T10:45:00Z"
  },
  "message": "Bank details created successfully"
}
```

### 2. Update Bank Details

```json
PUT /users/3/bank-details
{
  "bank_details": {
    "branch_name": "Mumbai Central Main Branch",
    "account_type": "Current"
  }
}
```

### 3. Verify Bank Details (Admin Only)

```json
PATCH /users/3/bank-details/verify
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "area_coordinator_id": 3,
    "bank_name": "State Bank of India",
    "account_holder_name": "Bob Wilson",
    "account_number": "12345678901",
    "ifsc_code": "SBIN0001234",
    "branch_name": "Mumbai Central Main Branch",
    "branch_code": "MC001",
    "account_type": "Current",
    "is_verified": true,
    "bank_passbook_image": "https://example.com/bob-passbook.jpg",
    "cancelled_cheque_image": "https://example.com/bob-cheque.jpg",
    "created_at": "2024-01-15T10:45:00Z",
    "updated_at": "2024-01-15T10:50:00Z"
  },
  "message": "Bank details verified successfully"
}
```

## Updating Users

### 1. Update User Basic Information

```json
PUT /users/1
{
  "full_name": "John Michael Doe",
  "email": "john.michael@example.com",
  "profile_image": "https://example.com/new-profile.jpg"
}
```

### 2. Update User Profile

```json
PATCH /users/1/profile
{
  "profile_data": {
    "passport_number": "A87654321",
    "nationality": "Canada",
    "preferences": {
      "preferred_style": "luxury",
      "max_price": 3500,
      "amenities": ["wifi", "parking", "kitchen", "pool", "gym"],
      "location_preference": "beachfront"
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "passport_number": "A87654321",
    "nationality": "Canada",
    "preferences": {
      "preferred_style": "luxury",
      "max_price": 3500,
      "amenities": ["wifi", "parking", "kitchen", "pool", "gym"],
      "location_preference": "beachfront"
    }
  },
  "message": "Guest profile updated successfully"
}
```

### 3. Update Host Experience

```json
PATCH /users/2/profile
{
  "profile_data": {
    "experience_years": 7,
    "company_name": "Smith & Associates Properties"
  }
}
```

### 4. Update Area Coordinator Location

```json
PATCH /users/3/profile
{
  "profile_data": {
    "region": "Uptown District",
    "assigned_properties": 5,
    "latitude": 19.0761,
    "longitude": 72.8778
  }
}
```

## Querying Users

### 1. Get All Users

```http
GET /users?skip=0&limit=10&active_only=true
```

### 2. Get Users by Type

```http
GET /users/types/GUEST?skip=0&limit=20
GET /users/types/HOST?skip=0&limit=20
GET /users/types/AREA_COORDINATOR?skip=0&limit=20
```

### 3. Get Specific User with Profile

```http
GET /users/3
```

**Response:**
```json
{
  "id": 3,
  "auth_provider": "EMAIL",
  "user_type": "AREA_COORDINATOR",
  "email": "bob.wilson@example.com",
  "phone_number": "+1122334455",
  "full_name": "Bob Wilson",
  "dob": "1978-12-10",
  "profile_image": "https://example.com/bob.jpg",
  "status": "ACTIVE",
  "created_at": "2024-01-15T10:40:00Z",
  "updated_at": "2024-01-15T10:50:00Z",
  "guest_profile": null,
  "host_profile": null,
  "area_coordinator_profile": {
    "id": 3,
    "region": "Uptown District",
    "assigned_properties": 5,
    "approval_status": "APPROVED",
    "approval_date": "2024-01-15T11:00:00Z",
    "approved_by": 1,
    "rejection_reason": null,
    "id_proof_type": "Aadhar",
    "id_proof_number": "123456789012",
    "pancard_number": "ABCDE1234F",
    "passport_size_photo": "https://example.com/bob-photo.jpg",
    "id_proof_document": "https://example.com/bob-aadhar.pdf",
    "address_proof_document": "https://example.com/bob-address.pdf",
    "district": "Mumbai Central",
    "panchayat": "Mumbai Central Ward",
    "address_line1": "123 Main Street",
    "address_line2": "Apartment 4B",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "latitude": 19.0761,
    "longitude": 72.8778,
    "emergency_contact": "+1199887766",
    "emergency_contact_name": "Alice Wilson",
    "emergency_contact_relationship": "Spouse",
    "bank_details": {
      "id": 1,
      "area_coordinator_id": 3,
      "bank_name": "State Bank of India",
      "account_holder_name": "Bob Wilson",
      "account_number": "12345678901",
      "ifsc_code": "SBIN0001234",
      "branch_name": "Mumbai Central Main Branch",
      "branch_code": "MC001",
      "account_type": "Current",
      "is_verified": true,
      "bank_passbook_image": "https://example.com/bob-passbook.jpg",
      "cancelled_cheque_image": "https://example.com/bob-cheque.jpg",
      "created_at": "2024-01-15T10:45:00Z",
      "updated_at": "2024-01-15T10:50:00Z"
    }
  }
}
```

### 4. Get User Profile Only

```http
GET /users/3/profile
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 3,
    "region": "Uptown District",
    "assigned_properties": 5,
    "approval_status": "APPROVED",
    "approval_date": "2024-01-15T11:00:00Z",
    "approved_by": 1,
    "rejection_reason": null,
    "id_proof_type": "Aadhar",
    "id_proof_number": "123456789012",
    "pancard_number": "ABCDE1234F",
    "passport_size_photo": "https://example.com/bob-photo.jpg",
    "id_proof_document": "https://example.com/bob-aadhar.pdf",
    "address_proof_document": "https://example.com/bob-address.pdf",
    "district": "Mumbai Central",
    "panchayat": "Mumbai Central Ward",
    "address_line1": "123 Main Street",
    "address_line2": "Apartment 4B",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "latitude": 19.0761,
    "longitude": 72.8778,
    "emergency_contact": "+1199887766",
    "emergency_contact_name": "Alice Wilson",
    "emergency_contact_relationship": "Spouse",
    "bank_details": {
      "id": 1,
      "area_coordinator_id": 3,
      "bank_name": "State Bank of India",
      "account_holder_name": "Bob Wilson",
      "account_number": "12345678901",
      "ifsc_code": "SBIN0001234",
      "branch_name": "Mumbai Central Main Branch",
      "branch_code": "MC001",
      "account_type": "Current",
      "is_verified": true,
      "bank_passbook_image": "https://example.com/bob-passbook.jpg",
      "cancelled_cheque_image": "https://example.com/bob-cheque.jpg",
      "created_at": "2024-01-15T10:45:00Z",
      "updated_at": "2024-01-15T10:50:00Z"
    }
  },
  "type": "area_coordinator"
}
```

## Search Users with Approval Status Filtering

### 1. Search by User Type and Approval Status

```json
POST /users/search
{
  "user_type": ["AREA_COORDINATOR"],
  "approval_status": ["PENDING"],
  "page": 1,
  "limit": 20,
  "status": ["ACTIVE"]
}
```

**Use Cases:**
- **Get Pending Area Coordinators**: `"approval_status": ["PENDING"]`
- **Get Approved Area Coordinators**: `"approval_status": ["APPROVED"]`
- **Get Rejected Area Coordinators**: `"approval_status": ["REJECTED"]`
- **Get Multiple Statuses**: `"approval_status": ["PENDING", "APPROVED"]`

### 2. Search with Date Filter

```json
POST /users/search
{
  "page": 1,
  "limit": 20,
  "date_filter": {
    "from_date": 1705257600000,
    "to_date": 1705344000000
  }
}
```

### 3. Search by User Type

```json
POST /users/search
{
  "user_type": ["GUEST", "HOST"],
  "page": 1,
  "limit": 20,
  "status": ["ACTIVE"],
  "search_query": "John"
}
```

## Status Management

### 1. Activate User

```json
PATCH /users/1/status
{
  "status": "ACTIVE"
}
```

### 2. Block User

```json
PATCH /users/1/status
{
  "status": "BLOCKED"
}
```

### 3. Soft Delete User

```json
PATCH /users/1/status
{
  "status": "DELETED"
}
```

## Error Responses

### 1. Missing Required Profile

```json
{
  "detail": "Guest profile is required for GUEST user type"
}
```

### 2. Invalid User Type

```json
{
  "detail": "Invalid user type: INVALID_TYPE"
}
```

### 3. Profile Not Found

```json
{
  "detail": "Guest profile not found"
}
```

### 4. Bank Details Already Exist

```json
{
  "detail": "Bank details already exist for this area coordinator"
}
```

### 5. Already Approved/Rejected

```json
{
  "detail": "Area coordinator is already approved"
}
```

### 6. Missing Rejection Reason

```json
{
  "detail": "Rejection reason is required when rejecting an area coordinator"
}
```

## Validation Rules

### User Creation
- **Required fields**: `auth_provider`, `user_type`, `full_name`
- **Profile requirement**: Must provide profile data matching `user_type`
- **Email/Phone**: Must be unique if provided
- **Password**: Required for EMAIL auth provider, min 8 characters

### Profile Updates
- **Guest**: `passport_number` and `nationality` are required for creation
- **Host**: `license_number` and `experience_years` are required for creation
- **Area Coordinator**: `region`, `district`, `panchayat`, `address_line1`, `city`, `state`, `postal_code` are required for creation
- **Preferences**: JSON object for guest preferences
- **Experience**: Integer between 0-50 for host experience
- **Coordinates**: Latitude (-90 to 90), Longitude (-180 to 180)

### Approval System
- **Default status**: All new area coordinators start with `PENDING` status
- **Admin approval**: Only admins can approve/reject area coordinators
- **Rejection reason**: Required when rejecting an area coordinator
- **Status tracking**: Records approval date and admin who approved/rejected

### Bank Details
- **Required fields**: `bank_name`, `account_holder_name`, `account_number`, `ifsc_code`
- **Unique constraint**: One bank details record per area coordinator
- **Verification**: Admin can mark bank details as verified

### User Updates
- All fields are optional
- Profile updates can be included in user updates
- Status changes use dedicated endpoint

## Best Practices

### 1. **Profile Creation**
- Always provide profile data when creating users
- Ensure profile data matches the user type
- Use appropriate validation for profile fields
- Include required address fields for area coordinators

### 2. **Approval Workflow**
- Create area coordinators with `PENDING` status
- Admin reviews documentation and profile information
- Approve only after thorough verification
- Provide clear rejection reasons for rejected applications
- Track approval history and admin actions

### 3. **Bank Details Management**
- Create bank details after area coordinator profile is created
- Include document images for verification
- Use proper IFSC codes and account numbers
- Verify bank details before processing payments

### 4. **Profile Updates**
- Use dedicated profile endpoint for profile-only updates
- Include profile updates in user updates when modifying both
- Validate profile data before updates
- Update location coordinates when address changes

### 5. **Querying and Search**
- Use the consolidated search API for all filtering needs
- Filter area coordinators by approval status using `approval_status` array
- Combine multiple filters for precise results
- Use pagination for large result sets
- Access bank details through area coordinator profile

### 6. **Error Handling**
- Check for profile existence before updates
- Validate user type consistency
- Handle missing profiles gracefully
- Verify area coordinator status before bank operations
- Check approval status before allowing operations

## Migration Notes

### From Old Structure
- Existing users without profiles will need migration
- Profile creation is now mandatory for new users
- API responses now include profile data
- Separate profile endpoints available
- New approval system for area coordinators
- New bank details table for area coordinators

### Backward Compatibility
- Basic user operations remain the same
- Profile data is optional in responses for existing users
- Status management unchanged
- Search functionality enhanced
- Bank details are optional and can be added later
- Approval status defaults to PENDING for new area coordinators

## Enhanced Area Coordinator Features

### New Fields Added
- **ID Proof**: `id_proof_type`, `id_proof_number`, `pancard_number`
- **Documents**: `passport_size_photo`, `id_proof_document`, `address_proof_document`
- **Address**: `district`, `panchayat`, `address_line1`, `address_line2`, `city`, `state`, `postal_code`
- **Location**: `latitude`, `longitude`
- **Emergency Contact**: `emergency_contact`, `emergency_contact_name`, `emergency_contact_relationship`

### Approval System
- **Status**: `PENDING`, `APPROVED`, `REJECTED`
- **Tracking**: `approval_date`, `approved_by`, `rejection_reason`
- **Workflow**: Admin review and approval process
- **History**: Complete approval/rejection tracking

### Bank Details Table
- **Account Info**: `bank_name`, `account_holder_name`, `account_number`, `ifsc_code`
- **Branch Details**: `branch_name`, `branch_code`, `account_type`
- **Verification**: `is_verified` flag
- **Documents**: `bank_passbook_image`, `cancelled_cheque_image`
- **Timestamps**: `created_at`, `updated_at`

### Benefits
- **Complete Documentation**: All required documents and proofs
- **Address Management**: Detailed address with coordinates
- **Bank Integration**: Ready for payment processing
- **Verification System**: Document and bank verification workflow
- **Emergency Contacts**: Safety and communication features
- **Approval Workflow**: Structured admin review process
- **Status Tracking**: Complete approval history and audit trail
- **Consolidated Search**: Single API for all filtering needs including approval status

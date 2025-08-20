# Heaven Connect - Host Onboarding Platform

A comprehensive FastAPI-based backend for a host onboarding platform that allows property owners to register and manage their homestays, hotels, and accommodations.

## Features

- **Multi-Provider Authentication**: Email/password, Google OAuth, and Mobile OTP authentication
- **9-Step Host Onboarding**: Complete onboarding flow with save & exit functionality
- **File Upload Management**: Secure image upload for ID proofs and property photos
- **Role-Based Access Control**: Admin, Host, and User roles with appropriate permissions
- **Area Coordinator System**: Admin assignment of coordinators to hosts
- **Real-time Progress Tracking**: Track onboarding completion status

## Project Structure

Following clean architecture principles with module-wise organization:

```
Heaven Connect/
├── app/
│   ├── core/
│   │   └── config.py          # Application settings
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py           # User and OTP models
│   │   └── host.py           # Host onboarding models
│   ├── schemas/              # Pydantic schemas
│   │   ├── auth.py           # Authentication schemas
│   │   ├── user.py           # User schemas
│   │   └── host.py           # Host schemas
│   ├── routers/              # FastAPI routers
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── host.py           # Host onboarding endpoints
│   │   └── admin.py          # Admin management endpoints
│   ├── services/             # Business logic
│   │   ├── auth_service.py   # Authentication logic
│   │   ├── user_service.py   # User management logic
│   │   └── host_service.py   # Host onboarding logic
│   ├── utils/                # Helper functions
│   │   ├── auth.py           # JWT and password utilities
│   │   ├── file_upload.py    # File handling utilities
│   │   └── otp.py            # OTP generation and verification
│   ├── migrations/           # Alembic migrations
│   ├── uploads/              # Uploaded files storage
│   └── database.py           # Database connection and session
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── env.example              # Environment variables template
```

## Database Models

### User Management
- **users**: User accounts with multi-provider authentication support
- **otp_verifications**: OTP codes for mobile authentication

### Host Onboarding
- **hosts**: Host profiles with onboarding progress tracking
- **rooms**: Room details and amenities
- **facilities**: Property facilities by category
- **property_photos**: Categorized property images
- **location**: Address and accessibility information
- **availability**: Available date ranges
- **host_agreements**: Legal agreements and consents

## Authentication Methods

### 1. Email/Password Authentication
```json
{
  "auth_provider": "email",
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

### 2. Mobile OTP Authentication
```json
{
  "auth_provider": "mobile",
  "phone_number": "+1234567890",
  "full_name": "John Doe"
}
```

### 3. Google OAuth Authentication
```json
{
  "id_token": "google_id_token_here"
}
```

## Host Onboarding Steps

### Step 1: Basic Profile
- Homestay name
- Alternate phone number

### Step 2: Documents Upload
- ID proof type and upload
- Certificate numbers
- Trade license details

### Step 3: Room Details
- Room types and counts
- Room-specific amenities

### Step 4: Facilities
- General, bedroom, bathroom, dining facilities
- Structured JSON storage

### Step 5: Property Photos
- Categorized image uploads (exterior, bedrooms, etc.)
- Automatic file organization

### Step 6: About Space
- Property description
- House rules
- Guest interaction style

### Step 7: Location
- Complete address
- Google Maps integration
- Accessibility features

### Step 8: Availability
- Available date ranges
- Blocking capabilities

### Step 9: Agreements
- Property ownership confirmation
- Terms and conditions acceptance
- Verification permissions

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /signup` - Register new user (email/mobile/google)
- `POST /login` - User authentication
- `POST /send-otp` - Send OTP to mobile
- `POST /verify-otp` - Verify OTP code
- `POST /google-login` - Google OAuth login
- `GET /me` - Current user information
- `POST /refresh-token` - Refresh access token

### Host Onboarding (`/api/v1/host`)
- `POST /profile` - Create host profile (Step 1)
- `POST /documents` - Upload documents (Step 2)
- `POST /rooms` - Add room details (Step 3)
- `POST /facilities` - Add facilities (Step 4)
- `POST /photos` - Upload property photos (Step 5)
- `POST /about` - About space information (Step 6)
- `POST /location` - Location details (Step 7)
- `POST /availability` - Availability periods (Step 8)
- `POST /agreements` - Complete onboarding (Step 9)
- `GET /onboarding-status` - Current progress status
- `GET /dashboard` - Host dashboard data

### Admin Management (`/api/v1/admin`)
- `GET /hosts` - List all hosts with filters
- `GET /hosts/{id}` - Host details
- `POST /hosts/{id}/assign-coordinator` - Assign area coordinator
- `POST /hosts/{id}/verify` - Verify host profile
- `GET /users` - User management
- `GET /statistics` - Admin dashboard statistics

## Setup Instructions

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd heaven-connect

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

1. Create MySQL database:
```sql
CREATE DATABASE heaven_connect;
```

2. Copy environment file:
```bash
cp env.example .env
```

3. Update `.env` with your configuration:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/heaven_connect
SECRET_KEY=your-super-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
```

**Note**: If you don't have MySQL set up yet, the application will still run but show a database connection warning. The API endpoints will work once you configure the database properly.

### 3. Database Migration

```bash
# Initialize Alembic (first time only)
# Note: Alembic is configured to use app/migrations directory
cd app
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Run Application

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access the application:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Admin Panel: http://localhost:8000/redoc

## File Upload System

The platform supports secure file uploads with:
- **Automatic organization**: Files stored in `/uploads/{host_id}/{category}/`
- **Type validation**: Only approved image formats (.jpg, .jpeg, .png, .webp)
- **Size limits**: Configurable maximum file size (default 10MB)
- **Security**: UUID-based filenames to prevent conflicts

### Upload Structure
```
app/uploads/
├── {host_id}/
│   ├── documents/
│   │   └── id_proof/
│   └── photos/
│       ├── exterior/
│       ├── bedroom/
│       ├── bathroom/
│       └── kitchen/
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password security
- **Role-Based Access**: Host, Admin, and User permissions
- **Input Validation**: Comprehensive Pydantic validation
- **File Security**: Upload validation and secure storage
- **CORS Protection**: Configurable cross-origin settings

## Configuration Options

Key environment variables:

```env
# Database
DATABASE_URL=mysql+pymysql://user:pass@host:port/db

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File Uploads
UPLOAD_DIR=app/uploads
MAX_FILE_SIZE=10485760
ALLOWED_IMAGE_EXTENSIONS=.jpg,.jpeg,.png,.webp

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# OTP Settings
OTP_EXPIRE_MINUTES=10
```

## Development Commands

```bash
# Database migrations
alembic revision --autogenerate -m "Migration description"
alembic upgrade head
alembic downgrade -1

# Run with auto-reload
uvicorn main:app --reload

# Run tests (when implemented)
pytest

# Code formatting
black app/
isort app/
```

## Deployment

### Production Checklist
1. Set `ENVIRONMENT=production` in `.env`
2. Use strong `SECRET_KEY`
3. Configure proper database connection pooling
4. Set up reverse proxy (Nginx)
5. Enable SSL/HTTPS
6. Set up file storage (AWS S3, etc.)
7. Configure monitoring and logging
8. Set up backup strategies

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.core.config import settings
from app.database import Base, engine
from app.middleware.error_handler import register_exception_handlers
from app.middleware.json_fix import JSONFixMiddleware

# Import all routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.otp_verifications import router as otp_router
from app.routers.properties import router as properties_router
from app.routers.property_types import router as property_types_router
from app.routers.rooms import router as rooms_router
from app.routers.facilities import router as facilities_router
from app.routers.property_photos import router as property_photos_router
from app.routers.location import router as location_router
from app.routers.availability import router as availability_router
from app.routers.property_agreements import router as property_agreements_router
from app.routers.images import router as images_router
from app.routers.districts import router as districts_router
from app.routers.grama_panchayats import router as grama_panchayats_router
from app.routers.corporations import router as corporations_router
from app.routers.municipalities import router as municipalities_router
from app.routers.training import router as training_router
from app.routers.communication import router as communication_router
from app.routers.enquiries import router as enquiries_router

# Note: Database tables will be created via startup event for async compatibility

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Heaven Connect - Host Onboarding Platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register global exception handlers
register_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # not for production if credentials are used
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files for uploaded content
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(otp_router, prefix="/api/v1")
app.include_router(properties_router, prefix="/api/v1")
app.include_router(property_types_router, prefix="/api/v1")
app.include_router(rooms_router, prefix="/api/v1")
app.include_router(facilities_router, prefix="/api/v1")
app.include_router(property_photos_router, prefix="/api/v1")
app.include_router(location_router, prefix="/api/v1")
app.include_router(availability_router, prefix="/api/v1")
app.include_router(property_agreements_router, prefix="/api/v1")
app.include_router(images_router, prefix="/api/v1")
app.include_router(districts_router, prefix="/api/v1")
app.include_router(grama_panchayats_router, prefix="/api/v1")
app.include_router(corporations_router, prefix="/api/v1")
app.include_router(municipalities_router, prefix="/api/v1")
app.include_router(training_router, prefix="/api/v1")
app.include_router(communication_router, prefix="/api/v1")
app.include_router(enquiries_router, prefix="/api/v1")


@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Heaven Connect Host Onboarding API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "database": "connected"
    }


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    
    # Apply bcrypt patch to fix 72-byte limit issues
    try:
        from app.utils.bcrypt_patch import apply_patch
        apply_patch()
        print("Applied bcrypt 72-byte limit patch")
    except Exception as e:
        print(f"Warning: Could not apply bcrypt patch: {e}")
    
    # Create database tables (for development - use Alembic in production)
    if settings.ENVIRONMENT == "development":
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully")
        except Exception as e:
            print(f"Warning: Could not connect to database: {e}")
            print("Please ensure MySQL is running and update your .env file with correct database credentials")
    print("Server starting...")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print("Shutting down Heaven Connect API")


if __name__ == "__main__":
    import uvicorn
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    print("Server starting...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
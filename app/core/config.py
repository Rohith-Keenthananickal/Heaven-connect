from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/heaven_connect"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "heaven_connect"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for host onboarding
    
    # Application settings
    APP_NAME: str = "Heaven Connect Host Onboarding API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # File upload settings
    UPLOAD_DIR: str = "app/uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS_STR: str = ".jpg,.jpeg,.png,.webp"
    
    # Add fields to allow direct setting from env vars
    ALLOWED_IMAGE_EXTENSIONS: str = None
    
    # CORS settings
    CORS_ORIGINS_STR: str = "*"
    
    # Add fields to allow direct setting from env vars
    CORS_ORIGINS: str = None
    
    # OTP settings
    OTP_EXPIRE_MINUTES: int = 10
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # AWS S3 settings
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    S3_ENDPOINT_URL: str = ""
    S3_USE_SSL: bool = True
    S3_SIGNATURE_VERSION: str = "s3v4"
    
    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"
    
    # External communication service
    COMMUNICATION_SERVER_BASE_URL: str = "https://communications.heavenconnect.in"
    COMMUNICATION_TIMEOUT_SECONDS: int = 10
    
    def get_allowed_extensions(self) -> List[str]:
        extensions_str = self.ALLOWED_IMAGE_EXTENSIONS or self.ALLOWED_IMAGE_EXTENSIONS_STR
        return [ext.strip() for ext in extensions_str.split(',') if ext.strip()]
    
    def get_cors_origins(self) -> List[str]:
        origins_str = self.CORS_ORIGINS or self.CORS_ORIGINS_STR
        if origins_str.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in origins_str.split(',') if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

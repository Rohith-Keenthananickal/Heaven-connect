from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.app_config import (
    AppConfigResponse,
    AppConfigPublicResponse,
    AppConfigCreate,
    AppConfigUpdate,
    AppConfigData
)
from app.schemas.base import BaseResponse
from app.services.app_config_service import app_config_service
from typing import List, Optional


router = APIRouter(prefix="/app-config", tags=["App Configuration"])


@router.get("", response_model=BaseResponse[AppConfigPublicResponse])
async def get_app_config(db: AsyncSession = Depends(get_db)):
    """
    Get the currently active app configuration (public endpoint).
    
    This endpoint provides:
    - Environment information
    - Maintenance mode settings
    - Force update configurations for host_app and atp_app
    - Feature flags
    - Kill switches
    """
    try:
        db_config = await app_config_service.get_active_config(db)
        
        if not db_config:
            # Return default config if none exists
            from app.core.config import settings
            from typing import Literal
            
            env: Literal["development", "staging", "production"] = "development"
            if settings.ENVIRONMENT.lower() == "production":
                env = "production"
            elif settings.ENVIRONMENT.lower() == "staging":
                env = "staging"
            
            default_config = AppConfigPublicResponse(
                environment=env,
                maintenance={
                    "maintenance_mode": False,
                    "maintenance_message": "System under maintenance. Please try again later."
                },
                apps={
                    "host_app": {
                        "android": {
                            "latest_version": "2.1.0",
                            "minimum_version": "2.0.0",
                            "force_update": True,
                            "store_url": "https://play.google.com/store/apps/details?id=com.triphaven.host",
                            "update_message": "Please update your app to continue"
                        },
                        "ios": {
                            "latest_version": "2.1.0",
                            "minimum_version": "2.0.0",
                            "force_update": True,
                            "store_url": "https://apps.apple.com/app/id123456",
                            "update_message": "Please update from App Store"
                        }
                    },
                    "atp_app": {
                        "android": {
                            "latest_version": "1.5.0",
                            "minimum_version": "1.3.0",
                            "force_update": False,
                            "store_url": "https://play.google.com/store/apps/details?id=com.triphaven.atp"
                        },
                        "ios": {
                            "latest_version": "1.5.0",
                            "minimum_version": "1.4.0",
                            "force_update": False,
                            "store_url": "https://apps.apple.com/app/id654321"
                        }
                    }
                },
                feature_flags={
                    "new_booking_ui_enabled": True,
                    "chat_feature_enabled": True,
                    "payment_v2_enabled": False
                },
                kill_switch={
                    "disable_booking": False,
                    "disable_login": False
                }
            )
            
            return BaseResponse(
                data=default_config,
                message="App configuration retrieved successfully (default)"
            )
        
        # Convert config_data dict to AppConfigData model, then to AppConfigPublicResponse
        config_data = AppConfigData.model_validate(db_config.config_data)
        public_response = AppConfigPublicResponse.model_validate(config_data.model_dump())
        
        return BaseResponse(
            data=public_response,
            message="App configuration retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch app configuration: {str(e)}"
        )


@router.get("/admin", response_model=BaseResponse[List[AppConfigResponse]])
async def list_app_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List all app configurations (admin endpoint)"""
    try:
        configs = await app_config_service.get_multi(db, skip=skip, limit=limit)
        config_responses = []
        for config in configs:
            config_data = AppConfigData.model_validate(config.config_data)
            response = AppConfigResponse(
                id=config.id,
                name=config.name,
                is_active=config.is_active,
                config_data=config_data,
                created_at=config.created_at,
                updated_at=config.updated_at,
                created_by=config.created_by,
                updated_by=config.updated_by
            )
            config_responses.append(response)
        return BaseResponse(
            data=config_responses,
            message="App configurations retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch app configurations: {str(e)}"
        )


@router.get("/admin/{config_id}", response_model=BaseResponse[AppConfigResponse])
async def get_app_config_by_id(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific app configuration by ID (admin endpoint)"""
    try:
        db_config = await app_config_service.get_or_404(db, config_id, "App configuration not found")
        # Convert config_data dict to AppConfigData
        config_data = AppConfigData.model_validate(db_config.config_data)
        response = AppConfigResponse(
            id=db_config.id,
            name=db_config.name,
            is_active=db_config.is_active,
            config_data=config_data,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
            created_by=db_config.created_by,
            updated_by=db_config.updated_by
        )
        return BaseResponse(
            data=response,
            message="App configuration retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch app configuration: {str(e)}"
        )


@router.post("/admin", response_model=BaseResponse[AppConfigResponse], status_code=status.HTTP_201_CREATED)
async def create_app_config(
    config_create: AppConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new app configuration (admin endpoint)"""
    try:
        db_config = await app_config_service.create_config(db, obj_in=config_create)
        config_data = AppConfigData.model_validate(db_config.config_data)
        response = AppConfigResponse(
            id=db_config.id,
            name=db_config.name,
            is_active=db_config.is_active,
            config_data=config_data,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
            created_by=db_config.created_by,
            updated_by=db_config.updated_by
        )
        return BaseResponse(
            data=response,
            message="App configuration created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create app configuration: {str(e)}"
        )


@router.put("/admin/{config_id}", response_model=BaseResponse[AppConfigResponse])
async def update_app_config(
    config_id: int,
    config_update: AppConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing app configuration (admin endpoint)"""
    try:
        db_config = await app_config_service.update_config(
            db,
            config_id=config_id,
            obj_in=config_update
        )
        
        if not db_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App configuration not found"
            )
        
        config_data = AppConfigData.model_validate(db_config.config_data)
        response = AppConfigResponse(
            id=db_config.id,
            name=db_config.name,
            is_active=db_config.is_active,
            config_data=config_data,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
            created_by=db_config.created_by,
            updated_by=db_config.updated_by
        )
        return BaseResponse(
            data=response,
            message="App configuration updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update app configuration: {str(e)}"
        )


@router.patch("/admin/{config_id}/activate", response_model=BaseResponse[AppConfigResponse])
async def activate_app_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Set a specific app configuration as active (admin endpoint)"""
    try:
        db_config = await app_config_service.set_active(db, config_id=config_id)
        
        if not db_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App configuration not found"
            )
        
        config_data = AppConfigData.model_validate(db_config.config_data)
        response = AppConfigResponse(
            id=db_config.id,
            name=db_config.name,
            is_active=db_config.is_active,
            config_data=config_data,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
            created_by=db_config.created_by,
            updated_by=db_config.updated_by
        )
        return BaseResponse(
            data=response,
            message="App configuration activated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate app configuration: {str(e)}"
        )


@router.delete("/admin/{config_id}", response_model=BaseResponse[AppConfigResponse])
async def delete_app_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an app configuration (admin endpoint)"""
    try:
        db_config = await app_config_service.get_or_404(db, config_id, "App configuration not found")
        
        # Prevent deleting the active config
        if db_config.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the active configuration. Please activate another configuration first."
            )
        
        config_data = AppConfigData.model_validate(db_config.config_data)
        response = AppConfigResponse(
            id=db_config.id,
            name=db_config.name,
            is_active=db_config.is_active,
            config_data=config_data,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
            created_by=db_config.created_by,
            updated_by=db_config.updated_by
        )
        
        await app_config_service.delete(db, id=config_id)
        
        return BaseResponse(
            data=response,
            message="App configuration deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete app configuration: {str(e)}"
        )

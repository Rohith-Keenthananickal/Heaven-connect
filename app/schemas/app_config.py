from pydantic import BaseModel
from typing import Literal, Optional, Dict, Any
from datetime import datetime


class PlatformAppConfig(BaseModel):
    """Configuration for a specific platform (Android/iOS)"""
    latest_version: str
    minimum_version: str
    force_update: bool
    store_url: str
    update_message: Optional[str] = None


class AppVersionConfig(BaseModel):
    """Version configuration for an app across platforms"""
    android: PlatformAppConfig
    ios: PlatformAppConfig


class AppsConfig(BaseModel):
    """Configuration for all apps"""
    host_app: AppVersionConfig
    atp_app: AppVersionConfig


class MaintenanceConfig(BaseModel):
    """Maintenance mode configuration"""
    maintenance_mode: bool
    maintenance_message: str


class FeatureFlagsConfig(BaseModel):
    """Feature flags configuration"""
    new_booking_ui_enabled: bool = False
    chat_feature_enabled: bool = False
    payment_v2_enabled: bool = False


class KillSwitchConfig(BaseModel):
    """Kill switch configuration"""
    disable_booking: bool = False
    disable_login: bool = False


class AppConfigData(BaseModel):
    """Complete app configuration data structure"""
    environment: Literal["development", "staging", "production"]
    maintenance: MaintenanceConfig
    apps: AppsConfig
    feature_flags: FeatureFlagsConfig
    kill_switch: KillSwitchConfig


class AppConfigCreate(BaseModel):
    """Schema for creating app config"""
    name: str = "default"
    is_active: bool = True
    config_data: AppConfigData
    created_by: Optional[int] = None


class AppConfigUpdate(BaseModel):
    """Schema for updating app config"""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    config_data: Optional[AppConfigData] = None
    updated_by: Optional[int] = None


class AppConfigResponse(BaseModel):
    """Complete app configuration response with database fields"""
    id: int
    name: str
    is_active: bool
    config_data: AppConfigData
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class AppConfigPublicResponse(BaseModel):
    """Public app configuration response (only config data, no DB fields)"""
    environment: Literal["development", "staging", "production"]
    maintenance: MaintenanceConfig
    apps: AppsConfig
    feature_flags: FeatureFlagsConfig
    kill_switch: KillSwitchConfig

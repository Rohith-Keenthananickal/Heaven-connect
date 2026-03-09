from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.app_config import AppConfig
from app.schemas.app_config import AppConfigCreate, AppConfigUpdate
from app.services.base_service import BaseService
from fastapi import HTTPException, status


class AppConfigService(BaseService[AppConfig, AppConfigCreate, AppConfigUpdate]):
    def __init__(self):
        super().__init__(AppConfig)
    
    async def get_active_config(self, db: AsyncSession) -> Optional[AppConfig]:
        """Get the currently active app configuration"""
        query = select(self.model).where(self.model.is_active == True).order_by(self.model.created_at.desc())
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[AppConfig]:
        """Get app config by name"""
        query = select(self.model).where(self.model.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_config(
        self,
        db: AsyncSession,
        *,
        obj_in: AppConfigCreate
    ) -> AppConfig:
        """Create a new app configuration"""
        # If setting as active, deactivate all other configs
        if obj_in.is_active:
            await self._deactivate_all_configs(db)
        
        # Convert config_data to dict for JSON storage
        config_dict = obj_in.config_data.model_dump()
        
        db_obj = AppConfig(
            name=obj_in.name,
            is_active=obj_in.is_active,
            config_data=config_dict,
            created_by=obj_in.created_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_config(
        self,
        db: AsyncSession,
        *,
        config_id: int,
        obj_in: AppConfigUpdate
    ) -> Optional[AppConfig]:
        """Update an existing app configuration"""
        db_obj = await self.get(db, config_id)
        if not db_obj:
            return None
        
        # If setting as active, deactivate all other configs
        if obj_in.is_active is True:
            await self._deactivate_all_configs(db, exclude_id=config_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Handle config_data separately to convert Pydantic model to dict
        if "config_data" in update_data and update_data["config_data"] is not None:
            update_data["config_data"] = update_data["config_data"].model_dump()
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def set_active(
        self,
        db: AsyncSession,
        *,
        config_id: int
    ) -> Optional[AppConfig]:
        """Set a specific config as active and deactivate all others"""
        db_obj = await self.get(db, config_id)
        if not db_obj:
            return None
        
        await self._deactivate_all_configs(db, exclude_id=config_id)
        db_obj.is_active = True
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def _deactivate_all_configs(
        self,
        db: AsyncSession,
        *,
        exclude_id: Optional[int] = None
    ) -> None:
        """Deactivate all configs except the one with exclude_id"""
        query = select(self.model).where(self.model.is_active == True)
        if exclude_id:
            query = query.where(self.model.id != exclude_id)
        
        result = await db.execute(query)
        configs = result.scalars().all()
        
        for config in configs:
            config.is_active = False
        
        if configs:
            await db.commit()


# Create service instance
app_config_service = AppConfigService()

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import PropertyPhoto, PhotoCategory
from app.schemas.property_photos import PropertyPhotoCreate, PropertyPhotoUpdate
from app.services.base_service import BaseService


class PropertyPhotosService(BaseService[PropertyPhoto, PropertyPhotoCreate, PropertyPhotoUpdate]):
    def __init__(self):
        super().__init__(PropertyPhoto)

    async def get_by_property(self, db: AsyncSession, property_id: int) -> List[PropertyPhoto]:
        """Get all property photos for a specific property"""
        return await self.get_multi(db, filters={"property_id": property_id})

    async def get_by_property_and_category(
        self, 
        db: AsyncSession, 
        property_id: int, 
        category: PhotoCategory
    ) -> List[PropertyPhoto]:
        """Get property photos by property and category"""
        from sqlalchemy import select, and_
        result = await db.execute(
            select(PropertyPhoto).where(
                and_(
                    PropertyPhoto.property_id == property_id,
                    PropertyPhoto.category == category
                )
            )
        )
        return result.scalars().all()

    async def get_by_category(
        self, 
        db: AsyncSession, 
        category: PhotoCategory,
        skip: int = 0,
        limit: int = 100
    ) -> List[PropertyPhoto]:
        """Get property photos by category"""
        return await self.get_multi(db, skip=skip, limit=limit, filters={"category": category})


property_photos_service = PropertyPhotosService()

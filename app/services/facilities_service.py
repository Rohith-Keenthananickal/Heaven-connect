from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Facility, FacilityCategory
from app.schemas.facilities import FacilityCreate, FacilityUpdate
from app.services.base_service import BaseService


class FacilitiesService(BaseService[Facility, FacilityCreate, FacilityUpdate]):
    def __init__(self):
        super().__init__(Facility)

    async def get_by_property(self, db: AsyncSession, property_id: int) -> List[Facility]:
        """Get all facilities for a specific property"""
        return await self.get_multi(db, filters={"property_id": property_id})

    async def get_by_property_and_category(
        self, 
        db: AsyncSession, 
        property_id: int, 
        category: FacilityCategory
    ) -> List[Facility]:
        """Get facilities by property and category"""
        from sqlalchemy import select, and_
        result = await db.execute(
            select(Facility).where(
                and_(
                    Facility.property_id == property_id,
                    Facility.category == category
                )
            )
        )
        return result.scalars().all()

    async def get_by_category(
        self, 
        db: AsyncSession, 
        category: FacilityCategory,
        skip: int = 0,
        limit: int = 100
    ) -> List[Facility]:
        """Get facilities by category"""
        return await self.get_multi(db, skip=skip, limit=limit, filters={"category": category})


facilities_service = FacilitiesService()

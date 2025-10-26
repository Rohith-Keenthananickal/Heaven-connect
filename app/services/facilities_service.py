from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Facility, FacilityCategory, PropertyClassification
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

    async def get_common_facilities(
        self, 
        db: AsyncSession,
        property_classification: Optional[PropertyClassification] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Facility]:
        """Get common facilities available to all properties or specific classification"""
        filters = {"is_common": True}
        if property_classification:
            filters["property_classification"] = property_classification
        return await self.get_multi(db, skip=skip, limit=limit, filters=filters)

    async def get_by_name(
        self, 
        db: AsyncSession, 
        facility_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Facility]:
        """Get facilities by name (case-insensitive search)"""
        from sqlalchemy import select, func
        result = await db.execute(
            select(Facility).where(
                func.lower(Facility.facility_name).contains(facility_name.lower())
            ).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_facilities_for_property(
        self, 
        db: AsyncSession, 
        property_id: int,
        property_classification: Optional[PropertyClassification] = None
    ) -> List[Facility]:
        """Get all facilities available for a property (property-specific + common facilities)"""
        from sqlalchemy import select, or_, and_
        
        # Build conditions for property-specific and common facilities
        conditions = [Facility.property_id == property_id]
        
        if property_classification:
            # Add common facilities for this classification
            conditions.append(
                and_(
                    Facility.is_common == True,
                    Facility.property_classification == property_classification
                )
            )
        else:
            # Add all common facilities
            conditions.append(Facility.is_common == True)
        
        result = await db.execute(
            select(Facility).where(or_(*conditions))
        )
        return result.scalars().all()


facilities_service = FacilitiesService()

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date
from app.models.property import Availability
from app.schemas.availability import AvailabilityCreate, AvailabilityUpdate
from app.services.base_service import BaseService


class AvailabilityService(BaseService[Availability, AvailabilityCreate, AvailabilityUpdate]):
    def __init__(self):
        super().__init__(Availability)

    async def get_by_property(self, db: AsyncSession, property_id: int) -> List[Availability]:
        """Get all availability records for a specific property"""
        return await self.get_multi(db, filters={"property_id": property_id})

    async def get_available_dates(
        self, 
        db: AsyncSession, 
        property_id: int,
        from_date: date = None,
        to_date: date = None
    ) -> List[Availability]:
        """Get available (not blocked) dates for a property within a date range"""
        query = select(Availability).where(
            and_(
                Availability.property_id == property_id,
                Availability.is_blocked == False
            )
        )
        
        if from_date:
            query = query.where(Availability.available_to >= from_date)
        
        if to_date:
            query = query.where(Availability.available_from <= to_date)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_blocked_dates(
        self, 
        db: AsyncSession, 
        property_id: int,
        from_date: date = None,
        to_date: date = None
    ) -> List[Availability]:
        """Get blocked dates for a property within a date range"""
        query = select(Availability).where(
            and_(
                Availability.property_id == property_id,
                Availability.is_blocked == True
            )
        )
        
        if from_date:
            query = query.where(Availability.available_to >= from_date)
        
        if to_date:
            query = query.where(Availability.available_from <= to_date)
        
        result = await db.execute(query)
        return result.scalars().all()


availability_service = AvailabilityService()

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Location
from app.schemas.location import LocationCreate, LocationUpdate
from app.services.base_service import BaseService


class LocationService(BaseService[Location, LocationCreate, LocationUpdate]):
    def __init__(self):
        super().__init__(Location)

    async def get_by_property(self, db: AsyncSession, property_id: int) -> Optional[Location]:
        """Get location for a specific property (should be unique)"""
        locations = await self.get_multi(db, filters={"property_id": property_id})
        return locations[0] if locations else None

    async def get_elderly_friendly(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Location]:
        """Get all elderly-friendly locations"""
        return await self.get_multi(db, skip=skip, limit=limit, filters={"elderly_friendly": True})


location_service = LocationService()

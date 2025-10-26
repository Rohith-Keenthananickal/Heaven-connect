from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Room, BedType, RoomView
from app.schemas.rooms import RoomCreate, RoomUpdate
from app.services.base_service import BaseService


class RoomsService(BaseService[Room, RoomCreate, RoomUpdate]):
    def __init__(self):
        super().__init__(Room)

    async def get_by_property(self, db: AsyncSession, property_id: int) -> List[Room]:
        """Get all rooms for a specific property"""
        return await self.get_multi(db, filters={"property_id": property_id})

    async def get_by_property_and_type(
        self, 
        db: AsyncSession, 
        property_id: int, 
        room_type: str
    ) -> List[Room]:
        """Get rooms by property and room type"""
        from sqlalchemy import select, and_
        result = await db.execute(
            select(Room).where(
                and_(
                    Room.property_id == property_id,
                    Room.room_type == room_type
                )
            )
        )
        return result.scalars().all()

    async def get_by_bed_type(
        self, 
        db: AsyncSession, 
        bed_type: BedType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Room]:
        """Get rooms by bed type"""
        return await self.get_multi(db, skip=skip, limit=limit, filters={"bed_type": bed_type})

    async def get_by_view(
        self, 
        db: AsyncSession, 
        view: RoomView,
        skip: int = 0,
        limit: int = 100
    ) -> List[Room]:
        """Get rooms by view"""
        return await self.get_multi(db, skip=skip, limit=limit, filters={"view": view})

    async def get_by_occupancy(
        self, 
        db: AsyncSession, 
        min_occupancy: int,
        max_occupancy: int = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Room]:
        """Get rooms by occupancy range"""
        from sqlalchemy import select, and_
        query = select(Room).where(Room.max_occupancy >= min_occupancy)
        
        if max_occupancy is not None:
            query = query.where(Room.max_occupancy <= max_occupancy)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


rooms_service = RoomsService()

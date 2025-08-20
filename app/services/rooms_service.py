from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Room
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


rooms_service = RoomsService()

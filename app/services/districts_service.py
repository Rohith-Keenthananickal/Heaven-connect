from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.location import District
from app.schemas.districts import DistrictCreate, DistrictUpdate
from app.services.base_service import BaseService


class DistrictService(BaseService[District, DistrictCreate, DistrictUpdate]):
    def __init__(self):
        super().__init__(District)
    
    async def get_by_state(self, db: AsyncSession, state: str, skip: int = 0, limit: int = 100) -> List[District]:
        """Get districts by state"""
        query = select(self.model).where(self.model.state == state).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[District]:
        """Get district by code"""
        query = select(self.model).where(self.model.code == code)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_districts(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[District]:
        """Get only active districts"""
        query = select(self.model).where(self.model.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def search_districts(self, db: AsyncSession, search_term: str, skip: int = 0, limit: int = 100) -> List[District]:
        """Search districts by name or state"""
        query = select(self.model).where(
            (self.model.name.ilike(f"%{search_term}%")) |
            (self.model.state.ilike(f"%{search_term}%"))
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# Create service instance
district_service = DistrictService()

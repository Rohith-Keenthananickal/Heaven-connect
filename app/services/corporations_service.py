from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.location import Corporation
from app.schemas.corporations import CorporationCreate, CorporationUpdate
from app.services.base_service import BaseService


class CorporationService(BaseService[Corporation, CorporationCreate, CorporationUpdate]):
    def __init__(self):
        super().__init__(Corporation)
    
    async def get_by_district(self, db: AsyncSession, district_id: int, skip: int = 0, limit: int = 100) -> List[Corporation]:
        """Get corporations by district ID"""
        query = select(self.model).where(self.model.district_id == district_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Corporation]:
        """Get corporation by code"""
        query = select(self.model).where(self.model.code == code)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_corporations(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Corporation]:
        """Get only active corporations"""
        query = select(self.model).where(self.model.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def search_corporations(self, db: AsyncSession, search_term: str, skip: int = 0, limit: int = 100) -> List[Corporation]:
        """Search corporations by name"""
        query = select(self.model).where(
            self.model.name.ilike(f"%{search_term}%")
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_corporations_by_population_range(self, db: AsyncSession, min_population: int, max_population: int, skip: int = 0, limit: int = 100) -> List[Corporation]:
        """Get corporations within a population range"""
        query = select(self.model).where(
            (self.model.population >= min_population) &
            (self.model.population <= max_population)
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_corporations_by_established_year(self, db: AsyncSession, year: int, skip: int = 0, limit: int = 100) -> List[Corporation]:
        """Get corporations established in a specific year"""
        query = select(self.model).where(self.model.established_year == year).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_corporations_by_mayor(self, db: AsyncSession, mayor_name: str, skip: int = 0, limit: int = 100) -> List[Corporation]:
        """Get corporations by mayor name"""
        query = select(self.model).where(
            self.model.mayor_name.ilike(f"%{mayor_name}%")
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# Create service instance
corporation_service = CorporationService()

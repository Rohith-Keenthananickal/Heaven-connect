from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.location import GramaPanchayat
from app.schemas.grama_panchayats import GramaPanchayatCreate, GramaPanchayatUpdate
from app.services.base_service import BaseService


class GramaPanchayatService(BaseService[GramaPanchayat, GramaPanchayatCreate, GramaPanchayatUpdate]):
    def __init__(self):
        super().__init__(GramaPanchayat)
    
    async def get_by_district(self, db: AsyncSession, district_id: int, skip: int = 0, limit: int = 100) -> List[GramaPanchayat]:
        """Get grama panchayats by district ID"""
        query = select(self.model).where(self.model.district_id == district_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[GramaPanchayat]:
        """Get grama panchayat by code"""
        query = select(self.model).where(self.model.code == code)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_panchayats(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[GramaPanchayat]:
        """Get only active grama panchayats"""
        query = select(self.model).where(self.model.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def search_panchayats(self, db: AsyncSession, search_term: str, skip: int = 0, limit: int = 100) -> List[GramaPanchayat]:
        """Search grama panchayats by name"""
        query = select(self.model).where(
            self.model.name.ilike(f"%{search_term}%")
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_panchayats_by_population_range(self, db: AsyncSession, min_population: int, max_population: int, skip: int = 0, limit: int = 100) -> List[GramaPanchayat]:
        """Get grama panchayats within a population range"""
        query = select(self.model).where(
            (self.model.population >= min_population) &
            (self.model.population <= max_population)
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# Create service instance
grama_panchayat_service = GramaPanchayatService()

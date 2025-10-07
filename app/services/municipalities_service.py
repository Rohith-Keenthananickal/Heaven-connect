from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.location import Municipality
from app.schemas.municipalities import MunicipalityCreate, MunicipalityUpdate
from app.services.base_service import BaseService


class MunicipalityService(BaseService[Municipality, MunicipalityCreate, MunicipalityUpdate]):
    def __init__(self):
        super().__init__(Municipality)
    
    async def get_by_district(self, db: AsyncSession, district_id: int, skip: int = 0, limit: int = 100) -> List[Municipality]:
        """Get municipalities by district ID"""
        query = select(self.model).where(self.model.district_id == district_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Municipality]:
        """Get municipality by code"""
        query = select(self.model).where(self.model.code == code)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_municipalities(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Municipality]:
        """Get only active municipalities"""
        query = select(self.model).where(self.model.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def search_municipalities(self, db: AsyncSession, search_term: str, skip: int = 0, limit: int = 100) -> List[Municipality]:
        """Search municipalities by name"""
        query = select(self.model).where(
            self.model.name.ilike(f"%{search_term}%")
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_municipalities_by_population_range(self, db: AsyncSession, min_population: int, max_population: int, skip: int = 0, limit: int = 100) -> List[Municipality]:
        """Get municipalities within a population range"""
        query = select(self.model).where(
            (self.model.population >= min_population) &
            (self.model.population <= max_population)
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_municipalities_by_established_year(self, db: AsyncSession, year: int, skip: int = 0, limit: int = 100) -> List[Municipality]:
        """Get municipalities established in a specific year"""
        query = select(self.model).where(self.model.established_year == year).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_municipalities_by_chairman(self, db: AsyncSession, chairman_name: str, skip: int = 0, limit: int = 100) -> List[Municipality]:
        """Get municipalities by chairman name"""
        query = select(self.model).where(
            self.model.chairman_name.ilike(f"%{chairman_name}%")
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_municipalities_by_type(self, db: AsyncSession, municipality_type: str, skip: int = 0, limit: int = 100) -> List[Municipality]:
        """Get municipalities by type/grade"""
        query = select(self.model).where(
            self.model.municipality_type.ilike(f"%{municipality_type}%")
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# Create service instance
municipality_service = MunicipalityService()

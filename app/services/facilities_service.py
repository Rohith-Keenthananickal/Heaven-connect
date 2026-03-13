from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.property import Facility, FacilityCategory
from app.schemas.facilities import FacilityCreate, FacilityUpdate
from app.services.base_service import BaseService
from app.services.facility_master_service import facility_master_service


class FacilitiesService(BaseService[Facility, FacilityCreate, FacilityUpdate]):
    def __init__(self):
        super().__init__(Facility)

    async def create(self, db: AsyncSession, *, obj_in: FacilityCreate) -> Facility:
        """Create a facility after validating facility_master_id exists."""
        await facility_master_service.get_or_404(db, obj_in.facility_master_id, "Facility master not found")
        return await super().create(db, obj_in=obj_in)

    async def get_with_master(self, db: AsyncSession, id: int) -> Optional[Facility]:
        """Get a facility by ID with facility_master relationship loaded."""
        result = await db.execute(
            select(Facility).where(Facility.id == id).options(selectinload(Facility.facility_master))
        )
        return result.scalar_one_or_none()

    async def get_or_404_with_master(self, db: AsyncSession, id: int, detail: str = "Facility not found") -> Facility:
        """Get a facility by ID with master loaded, or raise 404."""
        db_obj = await self.get_with_master(db, id)
        if not db_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        return db_obj

    async def get_multi_with_master(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> List[Facility]:
        """Get facilities with facility_master relationship loaded."""
        query = select(Facility).options(selectinload(Facility.facility_master)).offset(skip).limit(limit)
        if filters:
            for field, value in filters.items():
                if hasattr(Facility, field) and value is not None:
                    query = query.where(getattr(Facility, field) == value)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update(self, db: AsyncSession, *, db_obj: Facility, obj_in: FacilityUpdate) -> Facility:
        """Update a facility; validate facility_master_id if provided."""
        update_data = obj_in.dict(exclude_unset=True)
        if "facility_master_id" in update_data:
            await facility_master_service.get_or_404(db, update_data["facility_master_id"], "Facility master not found")
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

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
        skip: int = 0,
        limit: int = 100,
    ) -> List[Facility]:
        """Get common facilities available to all properties."""
        return await self.get_multi(db, skip=skip, limit=limit, filters={"is_common": True})

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
    ) -> List[Facility]:
        """Get all facilities available for a property (property-specific + common facilities)."""
        from sqlalchemy import select, or_

        result = await db.execute(
            select(Facility).where(
                or_(
                    Facility.property_id == property_id,
                    Facility.is_common == True,
                )
            )
        )
        return list(result.scalars().all())


facilities_service = FacilitiesService()

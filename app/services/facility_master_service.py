from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import FacilityMaster, FacilityMasterType, FacilityMasterStatus
from app.schemas.facility_master import FacilityMasterCreate, FacilityMasterUpdate
from app.services.base_service import BaseService


class FacilityMasterService(BaseService[FacilityMaster, FacilityMasterCreate, FacilityMasterUpdate]):
    def __init__(self):
        super().__init__(FacilityMaster)

    async def get_by_type(
        self,
        db: AsyncSession,
        type: FacilityMasterType,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FacilityMaster]:
        """Get facility masters by type (PROPERTY or ROOM)."""
        return await self.get_multi(db, skip=skip, limit=limit, filters={"type": type})

    async def get_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        type: Optional[FacilityMasterType] = None,
    ) -> List[FacilityMaster]:
        """Get facility masters with status ACTIVE, optionally filtered by type."""
        filters = {"status": FacilityMasterStatus.ACTIVE}
        if type is not None:
            filters["type"] = type
        return await self.get_multi(db, skip=skip, limit=limit, filters=filters)


facility_master_service = FacilityMasterService()

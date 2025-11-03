from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
# from sqlalchemy.sql.expression import cast, String
from app.models.enquiry import Enquiry, EnquiryStatus
from app.schemas.enquiry import EnquiryCreate, EnquiryUpdate, EnquiryStatusUpdate
from app.services.base_service import BaseService


class EnquiryService(BaseService[Enquiry, EnquiryCreate, EnquiryUpdate]):
    def __init__(self):
        super().__init__(Enquiry)
    
    async def create_enquiry(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: EnquiryCreate
    ) -> Enquiry:
        """Create a new enquiry"""
        return await self.create(db, obj_in=obj_in)
    
    async def update_enquiry(
        self, 
        db: AsyncSession, 
        *, 
        enquiry_id: int, 
        obj_in: EnquiryUpdate
    ) -> Optional[Enquiry]:
        """Update an existing enquiry"""
        db_obj = await self.get(db, enquiry_id)
        if not db_obj:
            return None
        return await self.update(db, db_obj=db_obj, obj_in=obj_in)
    
    async def update_status(
        self, 
        db: AsyncSession, 
        *, 
        enquiry_id: int, 
        status_update: EnquiryStatusUpdate
    ) -> Optional[Enquiry]:
        """Update enquiry status and optional remarks"""
        db_obj = await self.get(db, enquiry_id)
        if not db_obj:
            return None
        
        update_data = {
            "status": status_update.status
        }
        
        if status_update.remarks is not None:
            update_data["remarks"] = status_update.remarks
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_enquiries_by_status(
        self, 
        db: AsyncSession, 
        *, 
        status: EnquiryStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Enquiry]:
        """Get enquiries by status"""
        query = select(self.model).where(self.model.status == status).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def search_enquiries(
        self, 
        db: AsyncSession, 
        *, 
        search_params: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search enquiries with pagination and filters"""
        page = search_params.get("page", 1)
        limit = search_params.get("limit", limit)
        skip = (page - 1) * limit
        
        # Base query
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)
        
        # Apply filters
        filters = []
        
        if search_params.get("status"):
            filters.append(self.model.status == search_params["status"])
        
        if search_params.get("phone_number"):
            filters.append(self.model.phone_number.contains(search_params["phone_number"]))
        
        if search_params.get("email"):
            filters.append(self.model.email.ilike(f"%{search_params['email']}%"))
        
        if search_params.get("host_name"):
            filters.append(self.model.host_name.ilike(f"%{search_params['host_name']}%"))
        
        if search_params.get("company_name"):
            filters.append(self.model.company_name.ilike(f"%{search_params['company_name']}%"))
        
        if search_params.get("id_card_number"):
            filters.append(self.model.id_card_number.contains(search_params["id_card_number"]))
        
        if search_params.get("atp_id"):
            filters.append(self.model.atp_id.ilike(f"%{search_params['atp_id']}%"))
        
        if filters:
            query = query.where(or_(*filters))
            count_query = count_query.where(or_(*filters))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Order by created_at descending (newest first)
        query = query.order_by(self.model.created_at.desc())
        
        # Execute queries
        result = await db.execute(query)
        count_result = await db.execute(count_query)
        
        total = count_result.scalar()
        enquiries = result.scalars().all()
        
        # Create pagination info
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        
        pagination = {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
        
        return {
            "enquiries": enquiries,
            "pagination": pagination
        }


# Create an instance of the service
enquiry_service = EnquiryService()

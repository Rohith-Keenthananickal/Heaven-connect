from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException, status
from datetime import datetime
from app.models.experience import (
    Experience, ExperienceStatus, ExperienceApprovalStatus, DurationUnit
)
from app.models.user import User
from app.schemas.experience import (
    ExperienceCreate, ExperienceUpdate, ExperienceResponse
)
from app.utils.error_handler import create_server_error_http_exception


class ExperienceService:
    @staticmethod
    async def create_experience(
        db: AsyncSession,
        experience_data: ExperienceCreate
    ) -> Experience:
        """Create a new experience"""
        try:
            # Verify user exists
            result = await db.execute(select(User).filter(User.id == experience_data.user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify area coordinator exists if provided
            if experience_data.area_coordinator_id:
                result = await db.execute(select(User).filter(User.id == experience_data.area_coordinator_id))
                coordinator = result.scalar_one_or_none()
                if not coordinator:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Area coordinator not found"
                    )
            
            # Create experience
            experience = Experience(
                user_id=experience_data.user_id,
                title=experience_data.title,
                category=experience_data.category,
                subcategory=experience_data.subcategory,
                duration=experience_data.duration,
                duration_unit=experience_data.duration_unit,
                group_size=experience_data.group_size,
                languages=experience_data.languages,
                description=experience_data.description,
                included=experience_data.included,
                photos=experience_data.photos,
                video_url=experience_data.video_url,
                safety_items=experience_data.safety_items,
                price=experience_data.price,
                is_price_by_guest=experience_data.is_price_by_guest,
                included_in_price=experience_data.included_in_price,
                legal_declarations=experience_data.legal_declarations,
                area_coordinator_id=experience_data.area_coordinator_id,
                status=experience_data.status,
                approval_status=experience_data.approval_status
            )
            
            db.add(experience)
            await db.commit()
            await db.refresh(experience)
            return experience
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to create experience: {str(e)}",
                component="experience_create"
            )
    
    @staticmethod
    async def get_experience(
        db: AsyncSession,
        experience_id: int
    ) -> Optional[Experience]:
        """Get experience by ID"""
        try:
            result = await db.execute(
                select(Experience)
                .options(selectinload(Experience.user), selectinload(Experience.area_coordinator))
                .filter(Experience.id == experience_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Failed to get experience: {str(e)}",
                component="experience_get"
            )
    
    @staticmethod
    async def update_experience(
        db: AsyncSession,
        experience_id: int,
        experience_update: ExperienceUpdate
    ) -> Optional[Experience]:
        """Update an experience"""
        try:
            result = await db.execute(select(Experience).filter(Experience.id == experience_id))
            experience = result.scalar_one_or_none()
            if not experience:
                return None
            
            # Update fields if provided
            update_data = experience_update.dict(exclude_unset=True)
            
            # Verify area coordinator exists if being updated
            if "area_coordinator_id" in update_data and update_data["area_coordinator_id"]:
                result = await db.execute(select(User).filter(User.id == update_data["area_coordinator_id"]))
                coordinator = result.scalar_one_or_none()
                if not coordinator:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Area coordinator not found"
                    )
            
            for field, value in update_data.items():
                if hasattr(experience, field):
                    setattr(experience, field, value)
            
            await db.commit()
            await db.refresh(experience)
            return experience
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to update experience: {str(e)}",
                component="experience_update"
            )
    
    @staticmethod
    async def delete_experience(
        db: AsyncSession,
        experience_id: int
    ) -> bool:
        """Delete an experience (soft delete by setting status to DELETED)"""
        try:
            result = await db.execute(select(Experience).filter(Experience.id == experience_id))
            experience = result.scalar_one_or_none()
            if not experience:
                return False
            
            experience.status = ExperienceStatus.DELETED
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to delete experience: {str(e)}",
                component="experience_delete"
            )
    
    @staticmethod
    async def get_all_experiences(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        area_coordinator_id: Optional[int] = None,
        status_filter: Optional[ExperienceStatus] = None,
        approval_status_filter: Optional[ExperienceApprovalStatus] = None
    ) -> List[Experience]:
        """Get all experiences with optional filters"""
        try:
            query = select(Experience).options(
                selectinload(Experience.user),
                selectinload(Experience.area_coordinator)
            )
            
            if user_id:
                query = query.filter(Experience.user_id == user_id)
            
            if area_coordinator_id:
                query = query.filter(Experience.area_coordinator_id == area_coordinator_id)
            
            if status_filter:
                query = query.filter(Experience.status == status_filter)
            
            if approval_status_filter:
                query = query.filter(Experience.approval_status == approval_status_filter)
            
            query = query.order_by(Experience.created_at.desc()).offset(skip).limit(limit)
            result = await db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Failed to get experiences: {str(e)}",
                component="experience_list"
            )
    
    @staticmethod
    def update_experience_status(
        db: Session,
        experience_id: int,
        new_status: ExperienceStatus
    ) -> Optional[Experience]:
        """Update experience status (ACTIVE, BLOCKED, DELETED)"""
        try:
            experience = db.query(Experience).filter(Experience.id == experience_id).first()
            if not experience:
                return None
            
            experience.status = new_status
            db.commit()
            db.refresh(experience)
            return experience
            
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to update experience status: {str(e)}",
                component="experience_status_update"
            )
    
    @staticmethod
    def update_experience_approval_status(
        db: Session,
        experience_id: int,
        new_approval_status: ExperienceApprovalStatus
    ) -> Optional[Experience]:
        """Update experience approval status (DRAFT, PENDING, APPROVED, REJECTED)"""
        try:
            experience = db.query(Experience).filter(Experience.id == experience_id).first()
            if not experience:
                return None
            
            experience.approval_status = new_approval_status
            db.commit()
            db.refresh(experience)
            return experience
            
        except Exception as e:
            db.rollback()
            raise create_server_error_http_exception(
                message=f"Failed to update experience approval status: {str(e)}",
                component="experience_approval_status_update"
            )
    
    @staticmethod
    def search_experiences(
        db: Session,
        search_request
    ) -> dict:
        """Search experiences with pagination and filters"""
        try:
            query = db.query(Experience).options(
                joinedload(Experience.user),
                joinedload(Experience.area_coordinator)
            )
            filters = []
            
            # Apply user ID filter
            if search_request.user_id:
                filters.append(Experience.user_id == search_request.user_id)
            
            # Apply area coordinator ID filter
            if search_request.area_coordinator_id:
                filters.append(Experience.area_coordinator_id == search_request.area_coordinator_id)
            
            # Apply category filter
            if search_request.category:
                filters.append(Experience.category.ilike(f"%{search_request.category}%"))
            
            # Apply status filter (array support)
            if search_request.status:
                if len(search_request.status) == 1:
                    filters.append(Experience.status == search_request.status[0])
                else:
                    filters.append(Experience.status.in_(search_request.status))
            
            # Apply approval status filter (array support)
            if search_request.approval_status:
                if len(search_request.approval_status) == 1:
                    filters.append(Experience.approval_status == search_request.approval_status[0])
                else:
                    filters.append(Experience.approval_status.in_(search_request.approval_status))
            
            # Apply search query filter
            if search_request.search_query:
                search_term = f"%{search_request.search_query}%"
                filters.append(Experience.title.ilike(search_term))
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by created_at desc BEFORE pagination
            query = query.order_by(Experience.created_at.desc())
            
            # Get total count for pagination
            total = query.count()
            
            # Calculate pagination
            total_pages = (total + search_request.limit - 1) // search_request.limit
            skip = (search_request.page - 1) * search_request.limit
            
            # Apply pagination AFTER ordering
            query = query.offset(skip).limit(search_request.limit)
            
            # Execute query
            experiences = query.all()
            
            # Convert Experience objects to ExperienceResponse format
            experience_responses = [
                ExperienceResponse(
                    id=exp.id,
                    user_id=exp.user_id,
                    area_coordinator_id=exp.area_coordinator_id,
                    title=exp.title,
                    category=exp.category,
                    subcategory=exp.subcategory,
                    duration=exp.duration,
                    duration_unit=exp.duration_unit,
                    group_size=exp.group_size,
                    languages=exp.languages,
                    description=exp.description,
                    included=exp.included,
                    photos=exp.photos,
                    video_url=exp.video_url,
                    safety_items=exp.safety_items,
                    price=exp.price,
                    is_price_by_guest=exp.is_price_by_guest,
                    included_in_price=exp.included_in_price,
                    legal_declarations=exp.legal_declarations,
                    status=exp.status,
                    approval_status=exp.approval_status,
                    created_at=exp.created_at,
                    updated_at=exp.updated_at
                )
                for exp in experiences
            ]
            
            # Build pagination info
            pagination_info = {
                "page": search_request.page,
                "limit": search_request.limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": search_request.page < total_pages,
                "has_prev": search_request.page > 1
            }
            
            return {
                "experiences": experience_responses,
                "pagination": pagination_info
            }
            
        except Exception as e:
            raise create_server_error_http_exception(
                message=f"Experience search failed: {str(e)}",
                component="experience_search"
            )

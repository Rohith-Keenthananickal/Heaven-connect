from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc
from sqlalchemy.orm import selectinload
from app.models.issue import (
    Issue, IssueActivity, IssueEscalation,
    IssueType, IssueStatus, IssueStatusEnum, Priority,
    ActivityType, EscalationLevel
)
from app.models.user import User
from app.models.property import Property
from app.schemas.issue import (
    IssueCreate, IssueUpdate, IssueStatusUpdate, IssueAssignmentUpdate,
    IssuePriorityUpdate, IssueActivityCreate, IssueEscalationCreate,
    IssueEscalationUpdate
)
from app.services.base_service import BaseService
from fastapi import HTTPException, status


class IssueService(BaseService[Issue, IssueCreate, IssueUpdate]):
    def __init__(self):
        super().__init__(Issue)
    
    async def _generate_issue_code(
        self,
        db: AsyncSession,
        issue_type: IssueType
    ) -> str:
        """Generate unique issue code based on type"""
        prefix = "CMP" if issue_type == IssueType.COMPLAINT else "TKT"
        
        # Find the highest number for this type
        query = select(Issue.issue_code).where(
            Issue.type == issue_type,
            Issue.issue_code.isnot(None),
            Issue.issue_code.like(f"{prefix}-%")
        )
        
        result = await db.execute(query)
        existing_codes = result.scalars().all()
        
        # Extract the highest number
        max_num = 999  # Start from 1000, so default is 999
        for code in existing_codes:
            if code and code.startswith(f"{prefix}-"):
                try:
                    num_part = int(code.split("-")[1])
                    max_num = max(max_num, num_part)
                except (ValueError, IndexError):
                    continue
        
        # Generate next number (will be 1000 for first issue, then increment)
        next_num = max_num + 1
        return f"{prefix}-{next_num}"
    
    async def create_issue(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: IssueCreate
    ) -> Issue:
        """Create a new issue and log initial activity"""
        # Verify created_by user exists
        created_by = await db.get(User, obj_in.created_by_id)
        if not created_by:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {obj_in.created_by_id} not found"
            )
        
        # Verify assigned_to user exists if provided
        if obj_in.assigned_to_id:
            assigned_to = await db.get(User, obj_in.assigned_to_id)
            if not assigned_to:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {obj_in.assigned_to_id} not found"
                )
        
        # Verify property exists if provided
        if obj_in.property_id:
            property_obj = await db.get(Property, obj_in.property_id)
            if not property_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Property with id {obj_in.property_id} not found"
                )
        
        # Generate unique issue code
        issue_code = await self._generate_issue_code(db, obj_in.type)
        
        # Create issue
        issue_data = obj_in.dict(exclude={"created_by_id", "issue_code"})
        issue_data["created_by_id"] = obj_in.created_by_id
        issue_data["issue_code"] = issue_code
        db_issue = Issue(**issue_data)
        db.add(db_issue)
        await db.flush()  # Flush to get the issue ID
        
        # Log creation activity
        activity = IssueActivity(
            issue_id=db_issue.id,
            activity_type=ActivityType.CREATED,
            performed_by_id=obj_in.created_by_id,
            description=f"Issue '{obj_in.issue}' created",
            new_value=obj_in.issue_status.value
        )
        db.add(activity)
        
        await db.commit()
        await db.refresh(db_issue)
        
        return db_issue
    
    async def get_issue_with_details(
        self,
        db: AsyncSession,
        issue_id: int
    ) -> Optional[Issue]:
        """Get issue with all relationships loaded"""
        query = select(Issue).where(Issue.id == issue_id).options(
            selectinload(Issue.created_by),
            selectinload(Issue.assigned_to),
            selectinload(Issue.property),
            selectinload(Issue.activities).selectinload(IssueActivity.performed_by),
            selectinload(Issue.escalations).selectinload(IssueEscalation.escalated_by),
            selectinload(Issue.escalations).selectinload(IssueEscalation.escalated_to),
            selectinload(Issue.escalations).selectinload(IssueEscalation.resolved_by)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_issue(
        self, 
        db: AsyncSession, 
        *, 
        issue_id: int, 
        obj_in: IssueUpdate,
        updated_by_id: int
    ) -> Optional[Issue]:
        """Update an existing issue and log changes"""
        db_issue = await self.get(db, issue_id)
        if not db_issue:
            return None
        
        # Track changes for activity log
        changes = []
        update_data = obj_in.dict(exclude_unset=True)
        
        # Verify assigned_to user exists if being updated
        if "assigned_to_id" in update_data and update_data["assigned_to_id"]:
            assigned_to = await db.get(User, update_data["assigned_to_id"])
            if not assigned_to:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {update_data['assigned_to_id']} not found"
                )
            if db_issue.assigned_to_id != update_data["assigned_to_id"]:
                changes.append(("ASSIGNED", f"Assigned to user {update_data['assigned_to_id']}"))
        
        # Verify property exists if being updated
        if "property_id" in update_data and update_data["property_id"]:
            property_obj = await db.get(Property, update_data["property_id"])
            if not property_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Property with id {update_data['property_id']} not found"
                )
        
        # Track status changes
        if "issue_status" in update_data:
            old_status = db_issue.issue_status.value
            new_status = update_data["issue_status"].value
            if old_status != new_status:
                changes.append(("STATUS_CHANGED", f"Status changed from {old_status} to {new_status}"))
        
        # Track priority changes
        if "priority" in update_data:
            old_priority = db_issue.priority.value
            new_priority = update_data["priority"].value
            if old_priority != new_priority:
                changes.append(("PRIORITY_CHANGED", f"Priority changed from {old_priority} to {new_priority}"))
        
        # Update the issue (exclude issue_code - it's system-generated and immutable)
        for field, value in update_data.items():
            if hasattr(db_issue, field) and field != "issue_code":
                setattr(db_issue, field, value)
        
        # Log update activity
        if changes or update_data:
            activity = IssueActivity(
                issue_id=db_issue.id,
                activity_type=ActivityType.UPDATED,
                performed_by_id=updated_by_id,
                description="Issue updated",
                activity_metadata={"changes": [{"type": c[0], "description": c[1]} for c in changes]}
            )
            db.add(activity)
        
        await db.commit()
        await db.refresh(db_issue)
        return db_issue
    
    async def update_issue_status(
        self,
        db: AsyncSession,
        *,
        issue_id: int,
        status_update: IssueStatusUpdate,
        updated_by_id: int
    ) -> Optional[Issue]:
        """Update issue status and log activity"""
        db_issue = await self.get(db, issue_id)
        if not db_issue:
            return None
        
        old_status = db_issue.issue_status.value
        new_status = status_update.issue_status.value
        
        db_issue.issue_status = status_update.issue_status
        
        # Log status change activity
        activity = IssueActivity(
            issue_id=db_issue.id,
            activity_type=ActivityType.STATUS_CHANGED,
            performed_by_id=updated_by_id,
            description=status_update.description or f"Status changed from {old_status} to {new_status}",
            old_value=old_status,
            new_value=new_status
        )
        db.add(activity)
        
        await db.commit()
        await db.refresh(db_issue)
        return db_issue
    
    async def assign_issue(
        self,
        db: AsyncSession,
        *,
        issue_id: int,
        assignment: IssueAssignmentUpdate,
        assigned_by_id: int
    ) -> Optional[Issue]:
        """Assign or unassign an issue"""
        db_issue = await self.get(db, issue_id)
        if not db_issue:
            return None
        
        if assignment.assigned_to_id:
            # Verify user exists
            assigned_to = await db.get(User, assignment.assigned_to_id)
            if not assigned_to:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {assignment.assigned_to_id} not found"
                )
        
        old_assigned_to = db_issue.assigned_to_id
        db_issue.assigned_to_id = assignment.assigned_to_id
        
        # Log assignment activity
        if old_assigned_to != assignment.assigned_to_id:
            if assignment.assigned_to_id:
                description = f"Issue assigned to user {assignment.assigned_to_id}"
            else:
                description = "Issue unassigned"
            
            activity = IssueActivity(
                issue_id=db_issue.id,
                activity_type=ActivityType.ASSIGNED,
                performed_by_id=assigned_by_id,
                description=description,
                old_value=str(old_assigned_to) if old_assigned_to else None,
                new_value=str(assignment.assigned_to_id) if assignment.assigned_to_id else None
            )
            db.add(activity)
        
        await db.commit()
        await db.refresh(db_issue)
        return db_issue
    
    async def update_priority(
        self,
        db: AsyncSession,
        *,
        issue_id: int,
        priority_update: IssuePriorityUpdate,
        updated_by_id: int
    ) -> Optional[Issue]:
        """Update issue priority and log activity"""
        db_issue = await self.get(db, issue_id)
        if not db_issue:
            return None
        
        old_priority = db_issue.priority.value
        new_priority = priority_update.priority.value
        
        db_issue.priority = priority_update.priority
        
        # Log priority change activity
        activity = IssueActivity(
            issue_id=db_issue.id,
            activity_type=ActivityType.PRIORITY_CHANGED,
            performed_by_id=updated_by_id,
            description=f"Priority changed from {old_priority} to {new_priority}",
            old_value=old_priority,
            new_value=new_priority
        )
        db.add(activity)
        
        await db.commit()
        await db.refresh(db_issue)
        return db_issue
    
    async def delete_issue(
        self,
        db: AsyncSession,
        *,
        issue_id: int,
        deleted_by_id: int
    ) -> Optional[Issue]:
        """Soft delete an issue by setting status to DELETED"""
        db_issue = await self.get(db, issue_id)
        if not db_issue:
            return None
        
        db_issue.status = IssueStatus.DELETED
        
        # Log deletion activity
        activity = IssueActivity(
            issue_id=db_issue.id,
            activity_type=ActivityType.STATUS_CHANGED,
            performed_by_id=deleted_by_id,
            description="Issue deleted",
            old_value=db_issue.status.value,
            new_value=IssueStatus.DELETED.value
        )
        db.add(activity)
        
        await db.commit()
        await db.refresh(db_issue)
        return db_issue
    
    async def search_issues(
        self,
        db: AsyncSession,
        *,
        search_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Search issues with pagination and filters"""
        page = search_params.get("page", 1)
        limit = search_params.get("limit", 10)
        skip = (page - 1) * limit
        
        # Base query
        query = select(Issue).options(
            selectinload(Issue.created_by),
            selectinload(Issue.assigned_to),
            selectinload(Issue.property)
        )
        count_query = select(func.count()).select_from(Issue)
        
        # Apply filters
        filters = []
        
        if search_params.get("type"):
            filters.append(Issue.type == search_params["type"])
        
        if search_params.get("status"):
            filters.append(Issue.status == search_params["status"])
        
        if search_params.get("issue_status"):
            filters.append(Issue.issue_status == search_params["issue_status"])
        
        if search_params.get("priority"):
            filters.append(Issue.priority == search_params["priority"])
        
        if search_params.get("created_by_id"):
            filters.append(Issue.created_by_id == search_params["created_by_id"])
        
        if search_params.get("assigned_to_id"):
            filters.append(Issue.assigned_to_id == search_params["assigned_to_id"])
        
        if search_params.get("property_id"):
            filters.append(Issue.property_id == search_params["property_id"])
        
        if search_params.get("issue"):
            filters.append(Issue.issue.ilike(f"%{search_params['issue']}%"))
        
        # Only show non-deleted issues by default
        filters.append(Issue.status != IssueStatus.DELETED)
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Order by created_on descending (newest first)
        query = query.order_by(Issue.created_on.desc())
        
        # Execute queries
        result = await db.execute(query)
        count_result = await db.execute(count_query)
        
        total = count_result.scalar()
        issues = result.scalars().all()
        
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
            "issues": issues,
            "pagination": pagination
        }
    
    # Activity methods
    async def create_activity(
        self,
        db: AsyncSession,
        *,
        issue_id: int,
        obj_in: IssueActivityCreate
    ) -> IssueActivity:
        """Create an activity log for an issue"""
        # Verify issue exists
        issue = await self.get(db, issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue with id {issue_id} not found"
            )
        
        # Verify user exists
        user = await db.get(User, obj_in.performed_by_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {obj_in.performed_by_id} not found"
            )
        
        activity_data = obj_in.dict()
        activity_data["issue_id"] = issue_id
        db_activity = IssueActivity(**activity_data)
        db.add(db_activity)
        await db.commit()
        await db.refresh(db_activity)
        return db_activity
    
    async def get_issue_activities(
        self,
        db: AsyncSession,
        *,
        issue_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[IssueActivity]:
        """Get activities for an issue"""
        query = select(IssueActivity).where(
            IssueActivity.issue_id == issue_id
        ).options(
            selectinload(IssueActivity.performed_by)
        ).offset(skip).limit(limit).order_by(IssueActivity.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    # Escalation methods
    async def create_escalation(
        self,
        db: AsyncSession,
        *,
        issue_id: int,
        obj_in: IssueEscalationCreate
    ) -> IssueEscalation:
        """Create an escalation for a complaint issue"""
        # Verify issue exists
        issue = await self.get(db, issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue with id {issue_id} not found"
            )
        
        # Only complaints can be escalated
        if issue.type != IssueType.COMPLAINT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only COMPLAINT type issues can be escalated"
            )
        
        # Verify users exist
        escalated_by = await db.get(User, obj_in.escalated_by_id)
        if not escalated_by:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {obj_in.escalated_by_id} not found"
            )
        
        escalated_to = await db.get(User, obj_in.escalated_to_id)
        if not escalated_to:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {obj_in.escalated_to_id} not found"
            )
        
        # Create escalation
        escalation_data = obj_in.dict()
        escalation_data["issue_id"] = issue_id
        db_escalation = IssueEscalation(**escalation_data)
        db.add(db_escalation)
        
        # Update issue status to ESCALATED
        issue.issue_status = IssueStatusEnum.ESCALATED
        
        # Log escalation activity
        activity = IssueActivity(
            issue_id=issue.id,
            activity_type=ActivityType.ESCALATED,
            performed_by_id=obj_in.escalated_by_id,
            description=f"Issue escalated to {obj_in.escalation_level.value}",
            new_value=IssueStatusEnum.ESCALATED.value
        )
        db.add(activity)
        
        await db.commit()
        await db.refresh(db_escalation)
        return db_escalation
    
    async def get_issue_escalations(
        self,
        db: AsyncSession,
        *,
        issue_id: int
    ) -> List[IssueEscalation]:
        """Get escalations for an issue"""
        query = select(IssueEscalation).where(
            IssueEscalation.issue_id == issue_id
        ).options(
            selectinload(IssueEscalation.escalated_by),
            selectinload(IssueEscalation.escalated_to),
            selectinload(IssueEscalation.resolved_by)
        ).order_by(IssueEscalation.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_escalation(
        self,
        db: AsyncSession,
        *,
        escalation_id: int,
        obj_in: IssueEscalationUpdate
    ) -> Optional[IssueEscalation]:
        """Update an escalation (e.g., mark as resolved)"""
        db_escalation = await db.get(IssueEscalation, escalation_id)
        if not db_escalation:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        
        # If resolving, set resolved_at
        if update_data.get("resolved") and not db_escalation.resolved:
            update_data["resolved_at"] = datetime.now(timezone.utc)
        
        for field, value in update_data.items():
            if hasattr(db_escalation, field):
                setattr(db_escalation, field, value)
        
        await db.commit()
        await db.refresh(db_escalation)
        return db_escalation


# Create an instance of the service
issue_service = IssueService()


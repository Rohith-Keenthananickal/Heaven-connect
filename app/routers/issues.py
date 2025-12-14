from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.issue import (
    IssueCreate, IssueUpdate, IssueStatusUpdate, IssueAssignmentUpdate,
    IssuePriorityUpdate, IssueSearchRequest, IssueSearchResponse,
    IssueCreateAPIResponse, IssueListAPIResponse, IssueGetAPIResponse,
    IssueUpdateAPIResponse, IssueDeleteAPIResponse, IssueStatusUpdateAPIResponse,
    IssueActivityCreate, IssueActivityCreateAPIResponse, IssueActivityListAPIResponse,
    IssueEscalationCreate, IssueEscalationCreateAPIResponse, IssueEscalationListAPIResponse,
    IssueEscalationUpdate, IssueEscalationUpdateAPIResponse
)
from app.models.issue import IssueStatus, IssueStatusEnum, IssueType, Priority
from app.services.issue_service import issue_service
from app.schemas.base import PaginationInfo


router = APIRouter(prefix="/issues", tags=["Issues"])


def format_issue_response(issue, db: AsyncSession):
    """Helper function to format issue response with related data"""
    from app.schemas.issue import IssueDetailResponse
    
    return IssueDetailResponse(
        id=issue.id,
        issue_code=issue.issue_code or "",
        issue=issue.issue,
        type=issue.type,
        created_by_id=issue.created_by_id,
        assigned_to_id=issue.assigned_to_id,
        status=issue.status,
        issue_status=issue.issue_status,
        priority=issue.priority,
        description=issue.description,
        property_id=issue.property_id,
        attachments=issue.attachments or [],
        created_on=issue.created_on,
        updated_at=issue.updated_at,
        created_by_name=issue.created_by.full_name if issue.created_by else None,
        assigned_to_name=issue.assigned_to.full_name if issue.assigned_to else None,
        property_name=issue.property.name if issue.property else None,
        activities_count=len(issue.activities) if hasattr(issue, 'activities') else 0,
        escalations_count=len(issue.escalations) if hasattr(issue, 'escalations') else 0
    )


def format_activity_response(activity):
    """Helper function to format activity response"""
    from app.schemas.issue import IssueActivityResponse
    
    return IssueActivityResponse(
        id=activity.id,
        issue_id=activity.issue_id,
        activity_type=activity.activity_type,
        performed_by_id=activity.performed_by_id,
        performed_by_name=activity.performed_by.full_name if activity.performed_by else None,
        description=activity.description,
        old_value=activity.old_value,
        new_value=activity.new_value,
        activity_metadata=activity.activity_metadata,
        created_at=activity.created_at
    )


def format_escalation_response(escalation):
    """Helper function to format escalation response"""
    from app.schemas.issue import IssueEscalationResponse
    
    return IssueEscalationResponse(
        id=escalation.id,
        issue_id=escalation.issue_id,
        escalation_level=escalation.escalation_level,
        escalated_by_id=escalation.escalated_by_id,
        escalated_by_name=escalation.escalated_by.full_name if escalation.escalated_by else None,
        escalated_to_id=escalation.escalated_to_id,
        escalated_to_name=escalation.escalated_to.full_name if escalation.escalated_to else None,
        reason=escalation.reason,
        notes=escalation.notes,
        resolved=escalation.resolved,
        resolved_at=escalation.resolved_at,
        resolved_by_id=escalation.resolved_by_id,
        resolved_by_name=escalation.resolved_by.full_name if escalation.resolved_by else None,
        created_at=escalation.created_at,
        updated_at=escalation.updated_at
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=IssueCreateAPIResponse)
async def create_issue(
    issue: IssueCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new issue
    
    Example for SUPPORT type issue:
    ```json
    {
        "issue": "WiFi Connection Issues",
        "type": "SUPPORT",
        "description": "Guest reporting intermittent WiFi connectivity in Room 101",
        "priority": "HIGH",
        "issue_status": "OPEN",
        "created_by_id": 1,
        "property_id": 1,
        "assigned_to_id": null,
        "attachments": []
    }
    ```
    
    Note: An initial activity log is automatically created when the issue is created.
    To add more activities, use the POST /issues/{issue_id}/activities endpoint.
    """
    try:
        db_issue = await issue_service.create_issue(db, obj_in=issue)
        db_issue = await issue_service.get_issue_with_details(db, db_issue.id)
        formatted_issue = format_issue_response(db_issue, db)
        return IssueCreateAPIResponse(data=formatted_issue)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create issue: {str(e)}"
        )


@router.post("/search", response_model=IssueSearchResponse)
async def search_issues(
    search_request: IssueSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Search issues with pagination and filters"""
    try:
        result = await issue_service.search_issues(
            db, 
            search_params=search_request.dict(exclude_unset=True)
        )
        
        # Format issues
        formatted_issues = [format_issue_response(issue, db) for issue in result["issues"]]
        
        # Convert pagination dict to PaginationInfo model
        pagination = PaginationInfo(**result["pagination"])
        
        return IssueSearchResponse(
            data=formatted_issues,
            pagination=pagination
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search issues: {str(e)}"
        )


@router.get("/", response_model=IssueListAPIResponse)
async def get_issues(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: str = Query(None, description="Filter by issue type (COMPLAINT, SUPPORT)"),
    issue_status: str = Query(None, description="Filter by issue status (OPEN, IN_PROGRESS, ESCALATED, CLOSED)"),
    priority: str = Query(None, description="Filter by priority (LOW, MEDIUM, HIGH, URGENT)"),
    created_by_id: int = Query(None, description="Filter by creator user ID"),
    assigned_to_id: int = Query(None, description="Filter by assigned user ID"),
    property_id: int = Query(None, description="Filter by property ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all issues with pagination and optional filtering"""
    try:
        filters = {}
        if type:
            try:
                filters["type"] = IssueType(type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid issue type: {type}"
                )
        if issue_status:
            try:
                filters["issue_status"] = IssueStatusEnum(issue_status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid issue status: {issue_status}"
                )
        if priority:
            try:
                filters["priority"] = Priority(priority)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid priority: {priority}"
                )
        if created_by_id:
            filters["created_by_id"] = created_by_id
        if assigned_to_id:
            filters["assigned_to_id"] = assigned_to_id
        if property_id:
            filters["property_id"] = property_id
        
        issues = await issue_service.get_multi(db, skip=skip, limit=limit, filters=filters)
        
        # Get full details for each issue
        formatted_issues = []
        for issue in issues:
            full_issue = await issue_service.get_issue_with_details(db, issue.id)
            if full_issue:
                formatted_issues.append(format_issue_response(full_issue, db))
        
        return IssueListAPIResponse(data=formatted_issues)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch issues: {str(e)}"
        )


@router.get("/{issue_id}", response_model=IssueGetAPIResponse)
async def get_issue(
    issue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific issue by ID"""
    try:
        db_issue = await issue_service.get_issue_with_details(db, issue_id)
        if not db_issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        formatted_issue = format_issue_response(db_issue, db)
        return IssueGetAPIResponse(data=formatted_issue)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch issue: {str(e)}"
        )


@router.put("/{issue_id}", response_model=IssueUpdateAPIResponse)
async def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    updated_by_id: int = Query(..., description="ID of user performing the update"),
    db: AsyncSession = Depends(get_db)
):
    """Update an issue"""
    try:
        updated_issue = await issue_service.update_issue(
            db, issue_id=issue_id, obj_in=issue_update, updated_by_id=updated_by_id
        )
        if not updated_issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        full_issue = await issue_service.get_issue_with_details(db, updated_issue.id)
        formatted_issue = format_issue_response(full_issue, db)
        return IssueUpdateAPIResponse(data=formatted_issue)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update issue: {str(e)}"
        )


@router.patch("/{issue_id}/status", response_model=IssueStatusUpdateAPIResponse)
async def update_issue_status(
    issue_id: int,
    status_update: IssueStatusUpdate,
    updated_by_id: int = Query(..., description="ID of user performing the update"),
    db: AsyncSession = Depends(get_db)
):
    """Update issue status"""
    try:
        updated_issue = await issue_service.update_issue_status(
            db, issue_id=issue_id, status_update=status_update, updated_by_id=updated_by_id
        )
        if not updated_issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        full_issue = await issue_service.get_issue_with_details(db, updated_issue.id)
        formatted_issue = format_issue_response(full_issue, db)
        return IssueStatusUpdateAPIResponse(data=formatted_issue)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update issue status: {str(e)}"
        )


@router.patch("/{issue_id}/assign", response_model=IssueUpdateAPIResponse)
async def assign_issue(
    issue_id: int,
    assignment: IssueAssignmentUpdate,
    assigned_by_id: int = Query(..., description="ID of user performing the assignment"),
    db: AsyncSession = Depends(get_db)
):
    """Assign or unassign an issue"""
    try:
        updated_issue = await issue_service.assign_issue(
            db, issue_id=issue_id, assignment=assignment, assigned_by_id=assigned_by_id
        )
        if not updated_issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        full_issue = await issue_service.get_issue_with_details(db, updated_issue.id)
        formatted_issue = format_issue_response(full_issue, db)
        return IssueUpdateAPIResponse(data=formatted_issue)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign issue: {str(e)}"
        )


@router.patch("/{issue_id}/priority", response_model=IssueUpdateAPIResponse)
async def update_priority(
    issue_id: int,
    priority_update: IssuePriorityUpdate,
    updated_by_id: int = Query(..., description="ID of user performing the update"),
    db: AsyncSession = Depends(get_db)
):
    """Update issue priority"""
    try:
        updated_issue = await issue_service.update_priority(
            db, issue_id=issue_id, priority_update=priority_update, updated_by_id=updated_by_id
        )
        if not updated_issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        full_issue = await issue_service.get_issue_with_details(db, updated_issue.id)
        formatted_issue = format_issue_response(full_issue, db)
        return IssueUpdateAPIResponse(data=formatted_issue)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update priority: {str(e)}"
        )


@router.delete("/{issue_id}", response_model=IssueDeleteAPIResponse)
async def delete_issue(
    issue_id: int,
    deleted_by_id: int = Query(..., description="ID of user performing the deletion"),
    db: AsyncSession = Depends(get_db)
):
    """Delete an issue (soft delete)"""
    try:
        deleted_issue = await issue_service.delete_issue(
            db, issue_id=issue_id, deleted_by_id=deleted_by_id
        )
        if not deleted_issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        return IssueDeleteAPIResponse(data={"issue_id": issue_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete issue: {str(e)}"
        )


# Activity endpoints
@router.post("/{issue_id}/activities", status_code=status.HTTP_201_CREATED, response_model=IssueActivityCreateAPIResponse)
async def create_activity(
    issue_id: int,
    activity: IssueActivityCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create an activity log for an issue"""
    try:
        db_activity = await issue_service.create_activity(db, issue_id=issue_id, obj_in=activity)
        
        # Get activity with relationships
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from app.models.issue import IssueActivity
        
        query = select(IssueActivity).where(IssueActivity.id == db_activity.id).options(
            selectinload(IssueActivity.performed_by)
        )
        result = await db.execute(query)
        full_activity = result.scalar_one()
        
        formatted_activity = format_activity_response(full_activity)
        return IssueActivityCreateAPIResponse(data=formatted_activity)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create activity: {str(e)}"
        )


@router.get("/{issue_id}/activities", response_model=IssueActivityListAPIResponse)
async def get_issue_activities(
    issue_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get activities for an issue"""
    try:
        activities = await issue_service.get_issue_activities(
            db, issue_id=issue_id, skip=skip, limit=limit
        )
        formatted_activities = [format_activity_response(activity) for activity in activities]
        return IssueActivityListAPIResponse(data=formatted_activities)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch activities: {str(e)}"
        )


# Escalation endpoints
@router.post("/{issue_id}/escalations", status_code=status.HTTP_201_CREATED, response_model=IssueEscalationCreateAPIResponse)
async def create_escalation(
    issue_id: int,
    escalation: IssueEscalationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create an escalation for a complaint issue"""
    try:
        db_escalation = await issue_service.create_escalation(db, issue_id=issue_id, obj_in=escalation)
        
        # Get escalation with relationships
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from app.models.issue import IssueEscalation
        
        query = select(IssueEscalation).where(IssueEscalation.id == db_escalation.id).options(
            selectinload(IssueEscalation.escalated_by),
            selectinload(IssueEscalation.escalated_to),
            selectinload(IssueEscalation.resolved_by)
        )
        result = await db.execute(query)
        full_escalation = result.scalar_one()
        
        formatted_escalation = format_escalation_response(full_escalation)
        return IssueEscalationCreateAPIResponse(data=formatted_escalation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create escalation: {str(e)}"
        )


@router.get("/{issue_id}/escalations", response_model=IssueEscalationListAPIResponse)
async def get_issue_escalations(
    issue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get escalations for an issue"""
    try:
        escalations = await issue_service.get_issue_escalations(db, issue_id=issue_id)
        formatted_escalations = [format_escalation_response(escalation) for escalation in escalations]
        return IssueEscalationListAPIResponse(data=formatted_escalations)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch escalations: {str(e)}"
        )


@router.patch("/escalations/{escalation_id}", response_model=IssueEscalationUpdateAPIResponse)
async def update_escalation(
    escalation_id: int,
    escalation_update: IssueEscalationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an escalation (e.g., mark as resolved)"""
    try:
        updated_escalation = await issue_service.update_escalation(
            db, escalation_id=escalation_id, obj_in=escalation_update
        )
        if not updated_escalation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Escalation not found"
            )
        
        # Get escalation with relationships
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from app.models.issue import IssueEscalation
        
        query = select(IssueEscalation).where(IssueEscalation.id == updated_escalation.id).options(
            selectinload(IssueEscalation.escalated_by),
            selectinload(IssueEscalation.escalated_to),
            selectinload(IssueEscalation.resolved_by)
        )
        result = await db.execute(query)
        full_escalation = result.scalar_one()
        
        formatted_escalation = format_escalation_response(full_escalation)
        return IssueEscalationUpdateAPIResponse(data=formatted_escalation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update escalation: {str(e)}"
        )


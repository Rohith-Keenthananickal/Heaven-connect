#!/usr/bin/env python3
"""
Script to seed sample SUPPORT type issues with related activities for the Heaven Connect platform
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import AsyncSessionLocal, engine
from app.services.issue_service import issue_service
from app.schemas.issue import IssueCreate, IssueActivityCreate
from app.models.issue import IssueType, IssueStatusEnum, Priority, ActivityType
from app.models.user import User
from app.models.property import Property


async def get_or_create_sample_user(db: AsyncSession, user_id: int = None) -> int:
    """Get an existing user or return a default user ID"""
    if user_id:
        user = await db.get(User, user_id)
        if user:
            return user_id
    
    # Try to get the first available user
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user:
        return user.id
    
    # If no users exist, we'll need to create one or use None
    print("Warning: No users found in database. Please create at least one user first.")
    return None


async def get_or_create_sample_property(db: AsyncSession, property_id: int = None) -> int:
    """Get an existing property or return None"""
    if property_id:
        prop = await db.get(Property, property_id)
        if prop:
            return property_id
    
    # Try to get the first available property
    result = await db.execute(select(Property).limit(1))
    prop = result.scalar_one_or_none()
    if prop:
        return prop.id
    
    return None


async def seed_support_issues():
    """Seed sample SUPPORT type issues with activities"""
    
    # Sample SUPPORT issues data
    support_issues_data = [
        {
            "issue": "WiFi Connection Issues",
            "description": "Guest reporting intermittent WiFi connectivity in Room 101. Connection drops frequently and speed is very slow. Affecting work productivity.",
            "priority": Priority.HIGH,
            "issue_status": IssueStatusEnum.OPEN,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Support ticket created for WiFi connectivity issues",
                    "activity_metadata": {"source": "guest_complaint", "room": "101"}
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Initial investigation: Router appears to be functioning. Checking signal strength in affected area.",
                    "activity_metadata": {"investigation_status": "in_progress"}
                }
            ]
        },
        {
            "issue": "Air Conditioning Not Working",
            "description": "AC unit in Room 205 is not cooling properly. Guest has reported room temperature is too high despite AC being set to lowest setting.",
            "priority": Priority.URGENT,
            "issue_status": IssueStatusEnum.IN_PROGRESS,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Support ticket created for AC malfunction",
                    "activity_metadata": {"room": "205", "equipment": "air_conditioning"}
                },
                {
                    "activity_type": ActivityType.STATUS_CHANGED,
                    "description": "Issue status changed to IN_PROGRESS",
                    "old_value": "OPEN",
                    "new_value": "IN_PROGRESS"
                },
                {
                    "activity_type": ActivityType.ASSIGNED,
                    "description": "Issue assigned to maintenance team",
                    "activity_metadata": {"assigned_team": "maintenance"}
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Maintenance team dispatched. Estimated resolution time: 2 hours.",
                    "activity_metadata": {"eta": "2_hours"}
                }
            ]
        },
        {
            "issue": "Hot Water Supply Problem",
            "description": "No hot water available in Room 312. Guest tried multiple times but only cold water comes from the tap. This is affecting their stay experience.",
            "priority": Priority.HIGH,
            "issue_status": IssueStatusEnum.OPEN,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Support ticket created for hot water supply issue",
                    "activity_metadata": {"room": "312", "utility": "hot_water"}
                },
                {
                    "activity_type": ActivityType.PRIORITY_CHANGED,
                    "description": "Priority escalated to HIGH due to guest discomfort",
                    "old_value": "MEDIUM",
                    "new_value": "HIGH"
                }
            ]
        },
        {
            "issue": "Room Key Card Not Working",
            "description": "Guest's key card stopped working after first use. Unable to access room. Need immediate replacement.",
            "priority": Priority.URGENT,
            "issue_status": IssueStatusEnum.OPEN,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Support ticket created for key card malfunction",
                    "activity_metadata": {"room": "108", "issue_type": "access_control"}
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Front desk notified. New key card being prepared.",
                    "activity_metadata": {"action": "key_replacement_initiated"}
                }
            ]
        },
        {
            "issue": "TV Remote Control Missing",
            "description": "Guest reports TV remote control is missing from Room 415. Need replacement remote or alternative solution.",
            "priority": Priority.LOW,
            "issue_status": IssueStatusEnum.OPEN,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Support ticket created for missing TV remote",
                    "activity_metadata": {"room": "415", "item": "tv_remote"}
                }
            ]
        },
        {
            "issue": "Room Service Order Delay",
            "description": "Guest placed room service order 45 minutes ago but food has not arrived yet. Order number: RS-2024-001",
            "priority": Priority.MEDIUM,
            "issue_status": IssueStatusEnum.IN_PROGRESS,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Support ticket created for room service delay",
                    "activity_metadata": {"order_number": "RS-2024-001", "delay_minutes": 45}
                },
                {
                    "activity_type": ActivityType.STATUS_CHANGED,
                    "description": "Issue status changed to IN_PROGRESS",
                    "old_value": "OPEN",
                    "new_value": "IN_PROGRESS"
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Contacted kitchen. Order is being prepared now. Estimated delivery: 15 minutes.",
                    "activity_metadata": {"eta": "15_minutes"}
                }
            ]
        },
        {
            "issue": "Bathroom Drain Clogged",
            "description": "Bathroom drain in Room 220 is clogged. Water is not draining properly, causing inconvenience.",
            "priority": Priority.MEDIUM,
            "issue_status": IssueStatusEnum.OPEN,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Support ticket created for bathroom drain issue",
                    "activity_metadata": {"room": "220", "area": "bathroom"}
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Plumbing team notified. Will inspect and resolve within 1 hour.",
                    "activity_metadata": {"team": "plumbing", "eta": "1_hour"}
                }
            ]
        },
        {
            "issue": "Request for Extra Towels",
            "description": "Guest requesting additional towels for Room 305. Standard room service request.",
            "priority": Priority.LOW,
            "issue_status": IssueStatusEnum.CLOSED,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Support ticket created for extra towels request",
                    "activity_metadata": {"room": "305", "item": "towels"}
                },
                {
                    "activity_type": ActivityType.ASSIGNED,
                    "description": "Request assigned to housekeeping",
                    "activity_metadata": {"department": "housekeeping"}
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Extra towels delivered to room. Guest confirmed receipt.",
                    "activity_metadata": {"status": "completed"}
                },
                {
                    "activity_type": ActivityType.STATUS_CHANGED,
                    "description": "Issue resolved and closed",
                    "old_value": "OPEN",
                    "new_value": "CLOSED"
                },
                {
                    "activity_type": ActivityType.CLOSED,
                    "description": "Support ticket closed - request fulfilled",
                    "activity_metadata": {"resolution": "successful"}
                }
            ]
        }
    ]
    
    try:
        print("Starting to seed SUPPORT issues...")
        
        async with AsyncSessionLocal() as db:
            # Get a sample user for created_by_id (you can modify this)
            created_by_id = await get_or_create_sample_user(db, user_id=1)
            if not created_by_id:
                print("Error: Cannot proceed without a valid user. Please create at least one user first.")
                return
            
            # Get a sample property (optional)
            property_id = await get_or_create_sample_property(db, property_id=1)
            
            issues_created = 0
            activities_created = 0
            
            for issue_data in support_issues_data:
                try:
                    # Check if issue with same title already exists
                    from app.models.issue import Issue
                    result = await db.execute(
                        select(Issue).where(Issue.issue == issue_data["issue"])
                    )
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        print(f"Support issue '{issue_data['issue']}' already exists, skipping...")
                        continue
                    
                    # Create the issue
                    issue_create = IssueCreate(
                        issue=issue_data["issue"],
                        type=IssueType.SUPPORT,
                        description=issue_data["description"],
                        priority=issue_data["priority"],
                        issue_status=issue_data["issue_status"],
                        created_by_id=created_by_id,
                        property_id=property_id,
                        assigned_to_id=None  # Can be assigned later
                    )
                    
                    db_issue = await issue_service.create_issue(db, obj_in=issue_create)
                    issues_created += 1
                    print(f"Created support issue: {db_issue.issue_code} - {db_issue.issue}")
                    
                    # Create activities for this issue
                    for activity_data in issue_data.get("activities", []):
                        activity_create = IssueActivityCreate(
                            activity_type=activity_data["activity_type"],
                            description=activity_data.get("description"),
                            old_value=activity_data.get("old_value"),
                            new_value=activity_data.get("new_value"),
                            activity_metadata=activity_data.get("activity_metadata"),
                            performed_by_id=created_by_id
                        )
                        
                        await issue_service.create_activity(
                            db,
                            issue_id=db_issue.id,
                            obj_in=activity_create
                        )
                        activities_created += 1
                    
                    print(f"  Added {len(issue_data.get('activities', []))} activities")
                    
                except Exception as e:
                    print(f"Error creating issue '{issue_data['issue']}': {e}")
                    continue
            
            await db.commit()
            print(f"\nSeeding completed successfully!")
            print(f"Total issues created: {issues_created}")
            print(f"Total activities created: {activities_created}")
            
    except Exception as e:
        print(f"Error seeding support issues: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(seed_support_issues())


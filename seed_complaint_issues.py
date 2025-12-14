#!/usr/bin/env python3
"""
Script to seed sample COMPLAINT type issues with related activities and escalations
for the Heaven Connect platform
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.services.issue_service import issue_service
from app.schemas.issue import IssueCreate, IssueActivityCreate, IssueEscalationCreate
from app.models.issue import IssueType, IssueStatusEnum, Priority, ActivityType, EscalationLevel
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
    
    print("Warning: No users found in database. Please create at least one user first.")
    return None


async def get_or_create_sample_property(db: AsyncSession, property_id: int = None) -> int:
    """Get an existing property or return None"""
    if property_id:
        prop = await db.get(Property, property_id)
        if prop:
            return property_id
    
    result = await db.execute(select(Property).limit(1))
    prop = result.scalar_one_or_none()
    if prop:
        return prop.id
    
    return None


async def seed_complaint_issues():
    """Seed sample COMPLAINT type issues with activities and escalations"""
    
    # Sample COMPLAINT issues data
    complaint_issues_data = [
        {
            "issue": "Noise Complaint - Loud Music from Neighboring Room",
            "description": "Guest in Room 201 complaining about excessive noise from Room 202. Music playing loudly past midnight, disturbing sleep. Multiple complaints from other guests as well.",
            "priority": Priority.HIGH,
            "issue_status": IssueStatusEnum.OPEN,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Complaint created for noise disturbance",
                    "activity_metadata": {"complaining_room": "201", "source_room": "202", "issue": "noise"}
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Security team notified. Investigating the situation.",
                    "activity_metadata": {"action": "security_notified"}
                },
                {
                    "activity_type": ActivityType.STATUS_CHANGED,
                    "description": "Status changed to IN_PROGRESS",
                    "old_value": "OPEN",
                    "new_value": "IN_PROGRESS"
                }
            ],
            "escalations": [
                {
                    "escalation_level": EscalationLevel.LEVEL_1,
                    "escalated_by_id": None,  # Will be set to created_by_id
                    "escalated_to_id": None,  # Will be set to a different user if available
                    "reason": "Issue not resolved after initial intervention. Guest still reporting noise.",
                    "notes": "Escalating to property manager for immediate action"
                }
            ]
        },
        {
            "issue": "Unsanitary Conditions in Common Areas",
            "description": "Guest complaint about unclean restrooms and common areas. Trash not being collected, floors dirty, and unpleasant odor in lobby area. Affecting overall guest experience.",
            "priority": Priority.URGENT,
            "issue_status": IssueStatusEnum.ESCALATED,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Complaint created for unsanitary conditions",
                    "activity_metadata": {"area": "common_areas", "issue_type": "cleanliness"}
                },
                {
                    "activity_type": ActivityType.PRIORITY_CHANGED,
                    "description": "Priority escalated to URGENT due to health concerns",
                    "old_value": "HIGH",
                    "new_value": "URGENT"
                },
                {
                    "activity_type": ActivityType.ESCALATED,
                    "description": "Issue escalated to management",
                    "activity_metadata": {"escalation_reason": "health_concerns"}
                },
                {
                    "activity_type": ActivityType.STATUS_CHANGED,
                    "description": "Status changed to ESCALATED",
                    "old_value": "IN_PROGRESS",
                    "new_value": "ESCALATED"
                }
            ],
            "escalations": [
                {
                    "escalation_level": EscalationLevel.LEVEL_1,
                    "escalated_by_id": None,
                    "escalated_to_id": None,
                    "reason": "Health and safety concern requiring immediate management attention",
                    "notes": "Housekeeping supervisor notified. Deep cleaning scheduled."
                },
                {
                    "escalation_level": EscalationLevel.LEVEL_2,
                    "escalated_by_id": None,
                    "escalated_to_id": None,
                    "reason": "Issue persists. Escalating to regional manager",
                    "notes": "Multiple guest complaints. Need higher level intervention."
                }
            ]
        },
        {
            "issue": "Billing Dispute - Incorrect Charges",
            "description": "Guest disputing charges on final bill. Claims they were charged for services not used. Extra charges for room service items they did not order. Requesting refund.",
            "priority": Priority.MEDIUM,
            "issue_status": IssueStatusEnum.IN_PROGRESS,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Complaint created for billing dispute",
                    "activity_metadata": {"issue_type": "billing", "dispute_amount": "unknown"}
                },
                {
                    "activity_type": ActivityType.ASSIGNED,
                    "description": "Complaint assigned to accounts department",
                    "activity_metadata": {"department": "accounts"}
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Reviewing transaction records and guest folio. Investigation in progress.",
                    "activity_metadata": {"status": "under_review"}
                },
                {
                    "activity_type": ActivityType.STATUS_CHANGED,
                    "description": "Status changed to IN_PROGRESS",
                    "old_value": "OPEN",
                    "new_value": "IN_PROGRESS"
                }
            ],
            "escalations": []
        },
        {
            "issue": "Property Damage - Broken Furniture",
            "description": "Guest reported damage to furniture in Room 315. Coffee table has broken leg, likely due to misuse. Need to assess damage and determine liability.",
            "priority": Priority.MEDIUM,
            "issue_status": IssueStatusEnum.OPEN,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Complaint created for property damage",
                    "activity_metadata": {"room": "315", "item": "coffee_table", "damage": "broken_leg"}
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "Maintenance team inspecting damage. Photos taken for documentation.",
                    "activity_metadata": {"action": "damage_assessment"}
                }
            ],
            "escalations": []
        },
        {
            "issue": "Discrimination Complaint",
            "description": "Guest filing formal complaint about discriminatory treatment by staff member. Claims staff was rude and made inappropriate comments based on guest's background. This is a serious matter requiring immediate attention.",
            "priority": Priority.URGENT,
            "issue_status": IssueStatusEnum.ESCALATED,
            "activities": [
                {
                    "activity_type": ActivityType.CREATED,
                    "description": "Serious complaint created for discrimination",
                    "activity_metadata": {"complaint_type": "discrimination", "severity": "high"}
                },
                {
                    "activity_type": ActivityType.PRIORITY_CHANGED,
                    "description": "Priority set to URGENT due to nature of complaint",
                    "old_value": "HIGH",
                    "new_value": "URGENT"
                },
                {
                    "activity_type": ActivityType.ESCALATED,
                    "description": "Immediately escalated to HR and management",
                    "activity_metadata": {"departments": ["HR", "management"]}
                },
                {
                    "activity_type": ActivityType.STATUS_CHANGED,
                    "description": "Status changed to ESCALATED",
                    "old_value": "OPEN",
                    "new_value": "ESCALATED"
                },
                {
                    "activity_type": ActivityType.COMMENT_ADDED,
                    "description": "HR department conducting investigation. Staff member temporarily suspended pending review.",
                    "activity_metadata": {"action": "investigation_started"}
                }
            ],
            "escalations": [
                {
                    "escalation_level": EscalationLevel.LEVEL_1,
                    "escalated_by_id": None,
                    "escalated_to_id": None,
                    "reason": "Serious discrimination complaint requiring immediate HR intervention",
                    "notes": "Escalated to HR manager and property director"
                },
                {
                    "escalation_level": EscalationLevel.LEVEL_2,
                    "escalated_by_id": None,
                    "escalated_to_id": None,
                    "reason": "Escalating to corporate level due to legal implications",
                    "notes": "Corporate compliance team notified"
                },
                {
                    "escalation_level": EscalationLevel.LEVEL_3,
                    "escalated_by_id": None,
                    "escalated_to_id": None,
                    "reason": "Maximum escalation level - CEO and legal team involved",
                    "notes": "Legal review in progress. Potential policy changes being considered."
                }
            ]
        }
    ]
    
    try:
        print("Starting to seed COMPLAINT issues with activities and escalations...")
        
        async with AsyncSessionLocal() as db:
            # Get users for created_by and escalated_to
            created_by_id = await get_or_create_sample_user(db, user_id=1)
            if not created_by_id:
                print("Error: Cannot proceed without a valid user. Please create at least one user first.")
                return
            
            # Try to get a second user for escalations (if available)
            result = await db.execute(select(User).offset(1).limit(1))
            escalated_to_user = result.scalar_one_or_none()
            escalated_to_id = escalated_to_user.id if escalated_to_user else created_by_id
            
            # Get a sample property (optional)
            property_id = await get_or_create_sample_property(db, property_id=1)
            
            issues_created = 0
            activities_created = 0
            escalations_created = 0
            
            for issue_data in complaint_issues_data:
                try:
                    # Check if issue with same title already exists
                    from app.models.issue import Issue
                    result = await db.execute(
                        select(Issue).where(Issue.issue == issue_data["issue"])
                    )
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        print(f"Complaint issue '{issue_data['issue']}' already exists, skipping...")
                        continue
                    
                    # Create the issue
                    issue_create = IssueCreate(
                        issue=issue_data["issue"],
                        type=IssueType.COMPLAINT,
                        description=issue_data["description"],
                        priority=issue_data["priority"],
                        issue_status=issue_data["issue_status"],
                        created_by_id=created_by_id,
                        property_id=property_id,
                        assigned_to_id=None
                    )
                    
                    db_issue = await issue_service.create_issue(db, obj_in=issue_create)
                    issues_created += 1
                    print(f"Created complaint issue: {db_issue.issue_code} - {db_issue.issue}")
                    
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
                    
                    # Create escalations for this issue (only for COMPLAINT type)
                    for escalation_data in issue_data.get("escalations", []):
                        # Set escalated_by_id and escalated_to_id
                        escalation_data["escalated_by_id"] = created_by_id
                        escalation_data["escalated_to_id"] = escalated_to_id
                        
                        escalation_create = IssueEscalationCreate(
                            escalation_level=escalation_data["escalation_level"],
                            escalated_by_id=escalation_data["escalated_by_id"],
                            escalated_to_id=escalation_data["escalated_to_id"],
                            reason=escalation_data.get("reason"),
                            notes=escalation_data.get("notes")
                        )
                        
                        await issue_service.create_escalation(
                            db,
                            issue_id=db_issue.id,
                            obj_in=escalation_create
                        )
                        escalations_created += 1
                    
                    if issue_data.get("escalations"):
                        print(f"  Added {len(issue_data.get('escalations', []))} escalations")
                    
                except Exception as e:
                    print(f"Error creating issue '{issue_data['issue']}': {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            await db.commit()
            print(f"\nSeeding completed successfully!")
            print(f"Total issues created: {issues_created}")
            print(f"Total activities created: {activities_created}")
            print(f"Total escalations created: {escalations_created}")
            
    except Exception as e:
        print(f"Error seeding complaint issues: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(seed_complaint_issues())


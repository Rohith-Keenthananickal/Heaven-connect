"""
Examples of how to use the refactored User models with class table inheritance.

This file demonstrates:
1. Creating users with type-specific profiles
2. Querying users and their profiles
3. Managing relationships between users and profiles
"""

from sqlalchemy.orm import Session
from .user import User, Guest, Host, AreaCoordinator, UserType, AuthProvider, UserStatus
from typing import Optional, List


def create_guest_user(
    db: Session,
    full_name: str,
    email: str,
    phone_number: str,
    passport_number: str,
    nationality: str,
    preferences: Optional[dict] = None
) -> User:
    """Create a guest user with guest profile."""
    
    # Create the base user
    user = User(
        auth_provider=AuthProvider.EMAIL,
        user_type=UserType.GUEST,
        email=email,
        phone_number=phone_number,
        full_name=full_name,
        status=UserStatus.ACTIVE
    )
    
    db.add(user)
    db.flush()  # Flush to get the user ID
    
    # Create the guest profile
    guest_profile = Guest(
        id=user.id,
        passport_number=passport_number,
        nationality=nationality,
        preferences=preferences or {}
    )
    
    db.add(guest_profile)
    db.commit()
    db.refresh(user)
    
    return user


def create_host_user(
    db: Session,
    full_name: str,
    email: str,
    phone_number: str,
    id_proof_type: str,
    id_proof_number: str,
    id_proof_images: List[str],
    experience_years: int,
    company_name: Optional[str] = None
) -> User:
    """Create a host user with host profile."""
    
    # Create the base user
    user = User(
        auth_provider=AuthProvider.EMAIL,
        user_type=UserType.HOST,
        email=email,
        phone_number=phone_number,
        full_name=full_name,
        status=UserStatus.ACTIVE
    )
    
    db.add(user)
    db.flush()  # Flush to get the user ID
    
    # Create the host profile
    host_profile = Host(
        id=user.id,
        id_proof_type=id_proof_type,
        id_proof_number=id_proof_number,
        id_proof_images=id_proof_images,
        experience_years=experience_years,
        company_name=company_name
    )
    
    db.add(host_profile)
    db.commit()
    db.refresh(user)
    
    return user


def create_area_coordinator_user(
    db: Session,
    full_name: str,
    email: str,
    phone_number: str,
    region: str,
    assigned_properties: int = 0
) -> User:
    """Create an area coordinator user with area coordinator profile."""
    
    # Create the base user
    user = User(
        auth_provider=AuthProvider.EMAIL,
        user_type=UserType.AREA_COORDINATOR,
        email=email,
        phone_number=phone_number,
        full_name=full_name,
        status=UserStatus.ACTIVE
    )
    
    db.add(user)
    db.flush()  # Flush to get the user ID
    
    # Create the area coordinator profile
    coordinator_profile = AreaCoordinator(
        id=user.id,
        region=region,
        assigned_properties=assigned_properties
    )
    
    db.add(coordinator_profile)
    db.commit()
    db.refresh(user)
    
    return user


def get_user_with_profile(db: Session, user_id: int) -> Optional[User]:
    """Get a user with their type-specific profile loaded."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # The profile will be automatically loaded based on user_type
    # You can access it via:
    # - user.guest_profile (if user_type is GUEST)
    # - user.host_profile (if user_type is HOST)
    # - user.area_coordinator_profile (if user_type is AREA_COORDINATOR)
    
    return user


def get_users_by_type(db: Session, user_type: UserType):
    """Get all users of a specific type with their profiles."""
    
    if user_type == UserType.GUEST:
        return db.query(User).filter(User.user_type == UserType.GUEST).all()
    elif user_type == UserType.HOST:
        return db.query(User).filter(User.user_type == UserType.HOST).all()
    elif user_type == UserType.AREA_COORDINATOR:
        return db.query(User).filter(User.user_type == UserType.AREA_COORDINATOR).all()
    else:
        return db.query(User).filter(User.user_type == user_type).all()


def update_guest_preferences(db: Session, user_id: int, preferences: dict) -> bool:
    """Update guest preferences."""
    
    guest = db.query(Guest).filter(Guest.id == user_id).first()
    if not guest:
        return False
    
    guest.preferences = preferences
    db.commit()
    return True


def update_host_experience(db: Session, user_id: int, experience_years: int) -> bool:
    """Update host experience years."""
    
    host = db.query(Host).filter(Host.id == user_id).first()
    if not host:
        return False
    
    host.experience_years = experience_years
    db.commit()
    return True


def update_coordinator_region(db: Session, user_id: int, region: str) -> bool:
    """Update area coordinator region."""
    
    coordinator = db.query(AreaCoordinator).filter(AreaCoordinator.id == user_id).first()
    if not coordinator:
        return False
    
    coordinator.region = region
    db.commit()
    return True


# Example usage patterns:
"""
# Creating users:
guest_user = create_guest_user(
    db=db,
    full_name="John Doe",
    email="john@example.com",
    phone_number="+1234567890",
    passport_number="A12345678",
    nationality="US"
)

host_user = create_host_user(
    db=db,
    full_name="Jane Smith",
    email="jane@example.com",
    phone_number="+0987654321",
    license_number="HOST123456",
    experience_years=5,
    company_name="Smith Properties"
)

coordinator_user = create_area_coordinator_user(
    db=db,
    full_name="Bob Wilson",
    email="bob@example.com",
    phone_number="+1122334455",
    region="Downtown",
    assigned_properties=10
)

# Querying users with profiles:
user = get_user_with_profile(db, guest_user.id)
if user.guest_profile:
    print(f"Passport: {user.guest_profile.passport_number}")
    print(f"Nationality: {user.guest_profile.nationality}")

# Updating profiles:
update_guest_preferences(db, guest_user.id, {"preferred_style": "modern", "max_price": 2000})
update_host_experience(db, host_user.id, 7)
update_coordinator_region(db, coordinator_user.id, "Uptown")
"""

"""
ATP UUID generation utility
Generates unique ATP UUIDs in the format ATP-01234
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer
from app.models.user import AreaCoordinator


async def generate_atp_uuid(db: AsyncSession) -> str:
    """
    Generate a unique ATP UUID in the format ATP-01234
    
    Args:
        db: Database session
        
    Returns:
        str: Unique ATP UUID like 'ATP-01234'
    """
    # Get the highest existing ATP number
    result = await db.execute(
        select(func.max(
            func.cast(
                func.substring(AreaCoordinator.atp_uuid, 5),  # Extract number part after 'ATP-'
                Integer
            )
        )).where(AreaCoordinator.atp_uuid.isnot(None))
    )
    max_number = result.scalar()
    
    # If no existing ATP UUIDs, start from 1
    if max_number is None:
        next_number = 1
    else:
        next_number = max_number + 1
    
    # Format as ATP-XXXXX (5 digits with leading zeros)
    atp_uuid = f"ATP-{next_number:05d}"
    
    # Double-check uniqueness (in case of race conditions)
    existing = await db.execute(
        select(AreaCoordinator.atp_uuid).where(AreaCoordinator.atp_uuid == atp_uuid)
    )
    if existing.scalar_one_or_none():
        # If somehow it exists, try the next number
        return await generate_atp_uuid(db)
    
    return atp_uuid


def generate_atp_uuid_sync() -> str:
    """
    Synchronous version for testing or non-async contexts
    Note: This doesn't check database uniqueness, use generate_atp_uuid for production
    """
    import random
    # Generate a random 5-digit number for testing
    number = random.randint(1, 99999)
    return f"ATP-{number:05d}"

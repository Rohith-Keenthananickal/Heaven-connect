from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db, engine
from app.schemas.property import (
    PropertyTypeCreate, PropertyTypeUpdate, PropertyTypeResponse, 
    PropertyTypeListResponse
)
from app.models.property import PropertyType


router = APIRouter(prefix="/property-types", tags=["Property Types"])


@router.post("/", response_model=PropertyTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_property_type(
    type_data: PropertyTypeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new property type"""
    try:
        # Check if property type already exists
        result = await db.execute(
            text("SELECT id FROM property_types WHERE name = :name"),
            {"name": type_data.name}
        )
        existing = result.fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property type already exists"
            )
        
        # Create property type using raw SQL
        await db.execute(
            text("""
                INSERT INTO property_types (name, description, is_active, created_at, updated_at)
                VALUES (:name, :description, :is_active, NOW(), NOW())
            """),
            {
                "name": type_data.name,
                "description": type_data.description,
                "is_active": type_data.is_active
            }
        )
        await db.commit()
        
        # Get the created property type
        result = await db.execute(
            text("SELECT * FROM property_types WHERE name = :name"),
            {"name": type_data.name}
        )
        property_type_data = result.fetchone()
        
        # Convert to PropertyTypeResponse format
        return PropertyTypeResponse(
            id=property_type_data[0],
            name=property_type_data[1],
            description=property_type_data[2],
            is_active=property_type_data[3],
            created_at=property_type_data[4],
            updated_at=property_type_data[5]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create property type: {str(e)}"
        )


@router.get("/", response_model=PropertyTypeListResponse)
async def get_property_types(
    active_only: bool = Query(True, description="Return only active property types"),
    db: AsyncSession = Depends(get_db)
):
    """Get all property types"""
    try:
        if active_only:
            result = await db.execute(
                text("SELECT * FROM property_types WHERE is_active = :is_active"),
                {"is_active": True}
            )
        else:
            result = await db.execute(text("SELECT * FROM property_types"))
        
        property_types_data = result.fetchall()
        
        property_types = []
        for row in property_types_data:
            property_types.append(PropertyTypeResponse(
                id=row[0],
                name=row[1],
                description=row[2],
                is_active=row[3],
                created_at=row[4],
                updated_at=row[5]
            ))
        
        return {
            "property_types": property_types,
            "total": len(property_types)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property types: {str(e)}"
        )


@router.get("/{type_id}", response_model=PropertyTypeResponse)
async def get_property_type(
    type_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific property type by ID"""
    try:
        result = await db.execute(
            text("SELECT * FROM property_types WHERE id = :type_id"),
            {"type_id": type_id}
        )
        property_type_data = result.fetchone()
        
        if not property_type_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property type not found"
            )
        
        return PropertyTypeResponse(
            id=property_type_data[0],
            name=property_type_data[1],
            description=property_type_data[2],
            is_active=property_type_data[3],
            created_at=property_type_data[4],
            updated_at=property_type_data[5]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property type: {str(e)}"
        )


@router.put("/{type_id}", response_model=PropertyTypeResponse)
async def update_property_type(
    type_id: int,
    type_data: PropertyTypeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a property type"""
    try:
        # Check if property type exists
        result = await db.execute(
            text("SELECT * FROM property_types WHERE id = :type_id"),
            {"type_id": type_id}
        )
        existing = result.fetchone()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property type not found"
            )
        
        # Build update query
        update_fields = []
        params = {"type_id": type_id}
        
        if type_data.name is not None:
            # Check if new name conflicts with existing
            result = await db.execute(
                text("SELECT id FROM property_types WHERE name = :name AND id != :type_id"),
                {"name": type_data.name, "type_id": type_id}
            )
            if result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Property type name already exists"
                )
            update_fields.append("name = :name")
            params["name"] = type_data.name
        
        if type_data.description is not None:
            update_fields.append("description = :description")
            params["description"] = type_data.description
        
        if type_data.is_active is not None:
            update_fields.append("is_active = :is_active")
            params["is_active"] = type_data.is_active
        
        if update_fields:
            update_fields.append("updated_at = NOW()")
            
            query = f"UPDATE property_types SET {', '.join(update_fields)} WHERE id = :type_id"
            await db.execute(text(query), params)
            await db.commit()
        
        # Get updated property type
        result = await db.execute(
            text("SELECT * FROM property_types WHERE id = :type_id"),
            {"type_id": type_id}
        )
        updated_data = result.fetchone()
        
        return PropertyTypeResponse(
            id=updated_data[0],
            name=updated_data[1],
            description=updated_data[2],
            is_active=updated_data[3],
            created_at=updated_data[4],
            updated_at=updated_data[5]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property type: {str(e)}"
        )


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property_type(
    type_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a property type (soft delete)"""
    try:
        # Check if property type exists
        result = await db.execute(
            text("SELECT * FROM property_types WHERE id = :type_id"),
            {"type_id": type_id}
        )
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property type not found"
            )
        
        # Check if any properties are using this type
        result = await db.execute(
            text("SELECT id FROM properties WHERE property_type_id = :type_id LIMIT 1"),
            {"type_id": type_id}
        )
        if result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete property type as it is being used by properties"
            )
        
        # Soft delete by setting is_active to False
        await db.execute(
            text("UPDATE property_types SET is_active = :is_active, updated_at = NOW() WHERE id = :type_id"),
            {"is_active": False, "type_id": type_id}
        )
        await db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete property type: {str(e)}"
        )

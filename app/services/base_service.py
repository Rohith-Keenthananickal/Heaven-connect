from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from fastapi import HTTPException, status

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: CreateSchemaType
    ) -> ModelType:
        """Create a new record"""
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self, 
        db: AsyncSession, 
        id: int
    ) -> Optional[ModelType]:
        """Get a single record by ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and optional filters"""
        query = select(self.model)
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record"""
        update_data = obj_in.dict(exclude_unset=True)
        
        if update_data:
            # Update the object attributes
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            await db.commit()
            await db.refresh(db_obj)
        
        return db_obj

    async def delete(
        self, 
        db: AsyncSession, 
        *, 
        id: int
    ) -> Optional[ModelType]:
        """Delete a record by ID"""
        db_obj = await self.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj

    async def get_or_404(
        self, 
        db: AsyncSession, 
        id: int,
        detail: str = "Record not found"
    ) -> ModelType:
        """Get a record by ID or raise 404 HTTPException"""
        db_obj = await self.get(db, id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail
            )
        return db_obj

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.rooms import RoomCreate, RoomUpdate, RoomResponse, RoomListResponse
from app.services.rooms_service import rooms_service


router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post("/")
async def create_room(room: RoomCreate, db: AsyncSession = Depends(get_db)):
    """Create a new room"""
    try:
        db_room = await rooms_service.create(db, obj_in=room)
        return {"status": "success", "data": db_room}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/")
async def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: int = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all rooms with pagination"""
    try:
        if property_id:
            rooms = await rooms_service.get_by_property(db, property_id)
        else:
            rooms = await rooms_service.get_multi(db, skip=skip, limit=limit)
        return {"status": "success", "data": rooms}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{room_id}")
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific room by ID"""
    try:
        db_room = await rooms_service.get_or_404(db, room_id, "Room not found")
        return {"status": "success", "data": db_room}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{room_id}")
async def update_room(room_id: int, room_update: RoomUpdate, db: AsyncSession = Depends(get_db)):
    """Update a room"""
    try:
        db_room = await rooms_service.get_or_404(db, room_id, "Room not found")
        updated_room = await rooms_service.update(db, db_obj=db_room, obj_in=room_update)
        return {"status": "success", "data": updated_room}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{room_id}")
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a room"""
    try:
        deleted_room = await rooms_service.delete(db, id=room_id)
        if not deleted_room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
        return {"status": "success", "data": {"message": "Room deleted successfully"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

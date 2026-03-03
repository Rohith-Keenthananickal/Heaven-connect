from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.schemas.property import (
    SegmentCreate,
    SegmentUpdate,
    SegmentResponse,
    SegmentListResponse,
)
from app.models.property import SegmentStatus


router = APIRouter(prefix="/segments", tags=["Segments"])


@router.post("", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED)
async def create_segment(
    segment_data: SegmentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new segment"""
    try:
        result = await db.execute(
            text("SELECT id FROM segments WHERE name = :name"),
            {"name": segment_data.name},
        )
        existing = result.fetchone()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Segment already exists",
            )

        await db.execute(
            text("""
                INSERT INTO segments (name, description, status, created_at, updated_at)
                VALUES (:name, :description, :status, NOW(), NOW())
            """),
            {
                "name": segment_data.name,
                "description": segment_data.description,
                "status": segment_data.status.value,
            },
        )
        await db.commit()

        result = await db.execute(
            text("SELECT * FROM segments WHERE name = :name"),
            {"name": segment_data.name},
        )
        row = result.fetchone()

        return SegmentResponse(
            id=row[0],
            name=row[1],
            description=row[2],
            status=SegmentStatus(row[3]),
            created_at=row[4],
            updated_at=row[5],
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create segment: {str(e)}",
        )


@router.get("", response_model=SegmentListResponse)
async def get_segments(
    active_only: bool = Query(True, description="Return only active segments"),
    db: AsyncSession = Depends(get_db),
):
    """Get all segments"""
    try:
        if active_only:
            result = await db.execute(
                text("SELECT * FROM segments WHERE status = :status"),
                {"status": SegmentStatus.ACTIVE.value},
            )
        else:
            result = await db.execute(text("SELECT * FROM segments"))

        rows = result.fetchall()
        segments = [
            SegmentResponse(
                id=row[0],
                name=row[1],
                description=row[2],
                status=SegmentStatus(row[3]),
                created_at=row[4],
                updated_at=row[5],
            )
            for row in rows
        ]

        return {"segments": segments, "total": len(segments)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch segments: {str(e)}",
        )


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(
    segment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific segment by ID"""
    try:
        result = await db.execute(
            text("SELECT * FROM segments WHERE id = :segment_id"),
            {"segment_id": segment_id},
        )
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found",
            )

        return SegmentResponse(
            id=row[0],
            name=row[1],
            description=row[2],
            status=SegmentStatus(row[3]),
            created_at=row[4],
            updated_at=row[5],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch segment: {str(e)}",
        )


@router.put("/{segment_id}", response_model=SegmentResponse)
async def update_segment(
    segment_id: int,
    segment_data: SegmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a segment"""
    try:
        result = await db.execute(
            text("SELECT * FROM segments WHERE id = :segment_id"),
            {"segment_id": segment_id},
        )
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found",
            )

        update_fields = []
        params = {"segment_id": segment_id}

        if segment_data.name is not None:
            result = await db.execute(
                text("SELECT id FROM segments WHERE name = :name AND id != :segment_id"),
                {"name": segment_data.name, "segment_id": segment_id},
            )
            if result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Segment name already exists",
                )
            update_fields.append("name = :name")
            params["name"] = segment_data.name

        if segment_data.description is not None:
            update_fields.append("description = :description")
            params["description"] = segment_data.description

        if segment_data.status is not None:
            update_fields.append("status = :status")
            params["status"] = segment_data.status.value

        if update_fields:
            update_fields.append("updated_at = NOW()")
            query = f"UPDATE segments SET {', '.join(update_fields)} WHERE id = :segment_id"
            await db.execute(text(query), params)
            await db.commit()

        result = await db.execute(
            text("SELECT * FROM segments WHERE id = :segment_id"),
            {"segment_id": segment_id},
        )
        row = result.fetchone()

        return SegmentResponse(
            id=row[0],
            name=row[1],
            description=row[2],
            status=SegmentStatus(row[3]),
            created_at=row[4],
            updated_at=row[5],
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update segment: {str(e)}",
        )


@router.delete("/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_segment(
    segment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a segment (soft delete by setting status to INACTIVE)"""
    try:
        result = await db.execute(
            text("SELECT * FROM segments WHERE id = :segment_id"),
            {"segment_id": segment_id},
        )
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found",
            )

        result = await db.execute(
            text("SELECT id FROM properties WHERE segment_id = :segment_id LIMIT 1"),
            {"segment_id": segment_id},
        )
        if result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete segment as it is being used by properties",
            )

        await db.execute(
            text("UPDATE segments SET status = :status, updated_at = NOW() WHERE id = :segment_id"),
            {"status": SegmentStatus.INACTIVE.value, "segment_id": segment_id},
        )
        await db.commit()

        return None

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete segment: {str(e)}",
        )

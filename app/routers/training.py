from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserType
from app.schemas.training import (
    TrainingModuleCreate, TrainingModuleUpdate, TrainingModuleResponse, TrainingModuleWithProgress,
    TrainingContentCreate, TrainingContentUpdate, TrainingContentResponse, TrainingContentWithProgress,
    TrainingProgressResponse, QuizSubmission, ProgressUpdate, TrainingStats, ModuleProgressSummary,
    QuizResult, TrainingModuleCreateAPIResponse, TrainingModuleGetAPIResponse, TrainingModuleListAPIResponse,
    TrainingModuleUpdateAPIResponse, TrainingModuleDeleteAPIResponse, TrainingContentCreateAPIResponse,
    TrainingContentGetAPIResponse, TrainingContentListAPIResponse, TrainingContentUpdateAPIResponse,
    TrainingContentDeleteAPIResponse, TrainingProgressUpdateAPIResponse, QuizSubmitAPIResponse,
    TrainingStatsAPIResponse, ModuleProgressAPIResponse, UserTrainingModulesAPIResponse,
    TrainingAnalyticsAPIResponse
)
from app.services.training_service import TrainingModuleService, TrainingContentService, TrainingProgressService

# Create separate routers for different groups
training_modules_router = APIRouter(prefix="/training", tags=["Training Modules Master"])
training_controller_router = APIRouter(prefix="/training", tags=["ATP Training Controller"])

# Initialize services
module_service = TrainingModuleService()
content_service = TrainingContentService()
progress_service = TrainingProgressService()


# Training Module Endpoints - Training Modules Master
@training_modules_router.post("/modules", response_model=TrainingModuleCreateAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_training_module(
    module_data: TrainingModuleCreate,
    created_by: int = Query(..., description="Admin user ID who is creating the module"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new training module"""
    # Verify the user exists and is an admin
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == created_by,
                User.user_type == UserType.ADMIN
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    module = await module_service.create_with_contents(
        db, module_data=module_data, created_by=created_by
    )
    return TrainingModuleCreateAPIResponse(data=module)


@training_modules_router.get("/modules", response_model=TrainingModuleListAPIResponse)
async def get_training_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """Get all training modules"""
    if active_only:
        modules = await module_service.get_active_modules(db, skip=skip, limit=limit)
    else:
        modules = await module_service.get_multi(db, skip=skip, limit=limit)
    
    return TrainingModuleListAPIResponse(data=modules)


@training_modules_router.get("/modules/{module_id}", response_model=TrainingModuleGetAPIResponse)
async def get_training_module(
    module_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific training module with contents"""
    module = await module_service.get_with_contents(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training module not found"
        )
    return TrainingModuleGetAPIResponse(data=module)


@training_modules_router.put("/modules/{module_id}", response_model=TrainingModuleUpdateAPIResponse)
async def update_training_module(
    module_id: int,
    module_data: TrainingModuleUpdate,
    admin_user_id: int = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Update a training module"""
    # Verify the user exists and is an admin
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == admin_user_id,
                User.user_type == UserType.ADMIN
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    module = await module_service.get_or_404(db, module_id, "Training module not found")
    updated_module = await module_service.update(db, db_obj=module, obj_in=module_data)
    return TrainingModuleUpdateAPIResponse(data=updated_module)


@training_modules_router.delete("/modules/{module_id}", response_model=TrainingModuleDeleteAPIResponse)
async def delete_training_module(
    module_id: int,
    admin_user_id: int = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a training module"""
    # Verify the user exists and is an admin
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == admin_user_id,
                User.user_type == UserType.ADMIN
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    await module_service.delete(db, id=module_id)
    return TrainingModuleDeleteAPIResponse(data={})


# Training Content Endpoints - Training Modules Master
@training_modules_router.post("/modules/{module_id}/contents", response_model=TrainingContentCreateAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_training_content(
    module_id: int,
    content_data: TrainingContentCreate,
    admin_user_id: int = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Create training content for a module"""
    # Verify the user exists and is an admin
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == admin_user_id,
                User.user_type == UserType.ADMIN
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Verify module exists
    module = await module_service.get_or_404(db, module_id, "Training module not found")
    
    content_dict = content_data.dict()
    content_dict['module_id'] = module_id
    content = await content_service.create(db, obj_in=content_data)
    return TrainingContentCreateAPIResponse(data=content)


@training_modules_router.get("/modules/{module_id}/contents", response_model=TrainingContentListAPIResponse)
async def get_module_contents(
    module_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all contents for a training module"""
    contents = await content_service.get_by_module(db, module_id)
    return TrainingContentListAPIResponse(data=contents)


@training_modules_router.get("/contents/{content_id}", response_model=TrainingContentGetAPIResponse)
async def get_training_content(
    content_id: int,
    user_id: int = Query(..., description="Area Coordinator user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get training content with user's progress"""
    # Verify the user exists and is an area coordinator
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.user_type == UserType.AREA_COORDINATOR
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area Coordinator user not found"
        )
    
    content = await content_service.get_with_user_progress(db, content_id, user_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training content not found"
        )
    return TrainingContentGetAPIResponse(data=content)


@training_modules_router.put("/contents/{content_id}", response_model=TrainingContentUpdateAPIResponse)
async def update_training_content(
    content_id: int,
    content_data: TrainingContentUpdate,
    admin_user_id: int = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Update training content"""
    # Verify the user exists and is an admin
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == admin_user_id,
                User.user_type == UserType.ADMIN
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    content = await content_service.get_or_404(db, content_id, "Training content not found")
    updated_content = await content_service.update(db, db_obj=content, obj_in=content_data)
    return TrainingContentUpdateAPIResponse(data=updated_content)


@training_modules_router.delete("/contents/{content_id}", response_model=TrainingContentDeleteAPIResponse)
async def delete_training_content(
    content_id: int,
    admin_user_id: int = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete training content"""
    # Verify the user exists and is an admin
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == admin_user_id,
                User.user_type == UserType.ADMIN
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    await content_service.delete(db, id=content_id)
    return TrainingContentDeleteAPIResponse(data={})


# Area Coordinator Training Endpoints - ATP Training Controller
@training_controller_router.get("/my-modules", response_model=UserTrainingModulesAPIResponse)
async def get_my_training_modules(
    user_id: int = Query(..., description="Area Coordinator user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get training modules with user's progress"""
    # Verify the user exists and is an area coordinator
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.user_type == UserType.AREA_COORDINATOR
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area Coordinator user not found"
        )
    
    modules = await module_service.get_modules_with_user_progress(
        db, user_id, skip=skip, limit=limit
    )
    return UserTrainingModulesAPIResponse(data=modules)


@training_controller_router.post("/progress", response_model=TrainingProgressUpdateAPIResponse)
async def update_training_progress(
    progress_data: ProgressUpdate,
    user_id: int = Query(..., description="Area Coordinator user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Update training progress"""
    # Verify the user exists and is an area coordinator
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.user_type == UserType.AREA_COORDINATOR
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area Coordinator user not found"
        )
    
    progress = await progress_service.update_progress(db, user_id, progress_data)
    return TrainingProgressUpdateAPIResponse(data=progress)


@training_controller_router.post("/quiz/submit", response_model=QuizSubmitAPIResponse)
async def submit_quiz(
    quiz_data: QuizSubmission,
    user_id: int = Query(..., description="Area Coordinator user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Submit quiz answers"""
    # Verify the user exists and is an area coordinator
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.user_type == UserType.AREA_COORDINATOR
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area Coordinator user not found"
        )
    
    result = await progress_service.submit_quiz(db, user_id, quiz_data)
    return QuizSubmitAPIResponse(data=result)


@training_controller_router.get("/stats", response_model=TrainingStatsAPIResponse)
async def get_training_stats(
    user_id: int = Query(..., description="Area Coordinator user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive training statistics"""
    # Verify the user exists and is an area coordinator
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.user_type == UserType.AREA_COORDINATOR
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area Coordinator user not found"
        )
    
    stats = await progress_service.get_user_stats(db, user_id)
    return TrainingStatsAPIResponse(data=stats)


@training_controller_router.get("/modules/{module_id}/progress", response_model=ModuleProgressAPIResponse)
async def get_module_progress(
    module_id: int,
    user_id: int = Query(..., description="Area Coordinator user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed progress for a specific module"""
    # Verify the user exists and is an area coordinator
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.user_type == UserType.AREA_COORDINATOR
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area Coordinator user not found"
        )
    
    progress = await progress_service.get_module_progress_summary(db, user_id, module_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or no progress recorded"
        )
    return ModuleProgressAPIResponse(data=progress)


# Admin Analytics Endpoints - ATP Training Controller
@training_controller_router.get("/admin/analytics", response_model=TrainingAnalyticsAPIResponse)
async def get_training_analytics(
    admin_user_id: int = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get training analytics for all users"""
    # Verify the user exists and is an admin
    user_result = await db.execute(
        select(User).where(
            and_(
                User.id == admin_user_id,
                User.user_type == UserType.ADMIN
            )
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # This would need to be implemented based on specific analytics requirements
    # For now, returning a placeholder
    return TrainingAnalyticsAPIResponse(data=[{"message": "Analytics endpoint - to be implemented based on requirements"}])


@training_controller_router.get("/admin/user/{user_id}/progress", response_model=TrainingStatsAPIResponse)
async def get_user_training_progress(
    user_id: int,
    admin_user_id: int = Query(..., description="Admin user ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get training progress for a specific user"""
    # Verify the admin user exists and is an admin
    admin_result = await db.execute(
        select(User).where(
            and_(
                User.id == admin_user_id,
                User.user_type == UserType.ADMIN
            )
        )
    )
    admin_user = admin_result.scalar_one_or_none()
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    stats = await progress_service.get_user_stats(db, user_id)
    return TrainingStatsAPIResponse(data=stats)


# Create a main router that combines both routers
router = APIRouter()
router.include_router(training_modules_router)
router.include_router(training_controller_router)

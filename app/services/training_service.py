from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status
from datetime import datetime

from app.models.training import TrainingModule, TrainingContent, TrainingProgress, ContentType, TrainingStatus
from app.schemas.training import (
    TrainingModuleCreate, TrainingModuleUpdate, TrainingContentCreate, TrainingContentUpdate,
    TrainingProgressCreate, TrainingProgressUpdate, QuizSubmission, ProgressUpdate,
    TrainingStats, ModuleProgressSummary, TrainingModuleWithProgress, TrainingContentWithProgress
)
from app.services.base_service import BaseService


class TrainingModuleService(BaseService[TrainingModule, TrainingModuleCreate, TrainingModuleUpdate]):
    def __init__(self):
        super().__init__(TrainingModule)

    async def create_with_contents(
        self, 
        db: AsyncSession, 
        *, 
        module_data: TrainingModuleCreate,
        created_by: Optional[int] = None
    ) -> TrainingModule:
        """Create a training module with its contents"""
        # Create the module
        module_dict = module_data.dict(exclude={'contents'})
        module_dict['created_by'] = created_by  # This can now be None
        
        module = TrainingModule(**module_dict)
        db.add(module)
        await db.flush()  # Get the module ID
        
        # Create contents if provided
        if module_data.contents:
            for content_data in module_data.contents:
                content_dict = content_data.dict()
                content_dict['module_id'] = module.id
                content = TrainingContent(**content_dict)
                db.add(content)
        
        await db.commit()
        
        # Refresh the module and eagerly load contents to avoid lazy loading issues
        await db.refresh(module)
        if module_data.contents:
            # Eagerly load the contents relationship
            from sqlalchemy.orm import selectinload
            result = await db.execute(
                select(TrainingModule)
                .options(selectinload(TrainingModule.contents))
                .where(TrainingModule.id == module.id)
            )
            module = result.scalar_one()
        
        return module

    async def get_with_contents(
        self, 
        db: AsyncSession, 
        module_id: int
    ) -> Optional[TrainingModule]:
        """Get a training module with its contents"""
        result = await db.execute(
            select(TrainingModule)
            .options(selectinload(TrainingModule.contents))
            .where(TrainingModule.id == module_id)
        )
        return result.scalar_one_or_none()

    async def get_active_modules(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[TrainingModule]:
        """Get active training modules ordered by module_order"""
        result = await db.execute(
            select(TrainingModule)
            .options(selectinload(TrainingModule.contents))
            .where(TrainingModule.is_active == True)
            .order_by(TrainingModule.module_order)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_modules_with_user_progress(
        self, 
        db: AsyncSession, 
        user_id: int, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[TrainingModuleWithProgress]:
        """Get training modules with user's progress"""
        # Get modules
        modules_result = await db.execute(
            select(TrainingModule)
            .options(selectinload(TrainingModule.contents))
            .where(TrainingModule.is_active == True)
            .order_by(TrainingModule.module_order)
            .offset(skip)
            .limit(limit)
        )
        modules = modules_result.scalars().all()
        
        # Get user progress for these modules
        module_ids = [m.id for m in modules]
        progress_result = await db.execute(
            select(TrainingProgress)
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.module_id.in_(module_ids)
                )
            )
        )
        progress_records = {p.module_id: p for p in progress_result.scalars().all()}
        
        # Build response
        result = []
        for module in modules:
            module_data = TrainingModuleWithProgress.model_validate(module)
            module_data.user_progress = progress_records.get(module.id)
            module_data.total_contents = len(module.contents)
            
            # Calculate completed contents
            if module_data.user_progress:
                completed_contents = await self._count_completed_contents(db, user_id, module.id)
                module_data.completed_contents = completed_contents
            else:
                module_data.completed_contents = 0
            
            result.append(module_data)
        
        return result

    async def _count_completed_contents(
        self, 
        db: AsyncSession, 
        user_id: int, 
        module_id: int
    ) -> int:
        """Count completed contents for a user in a module"""
        result = await db.execute(
            select(func.count(TrainingProgress.id))
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.module_id == module_id,
                    TrainingProgress.content_id.isnot(None),
                    TrainingProgress.status == TrainingStatus.COMPLETED
                )
            )
        )
        return result.scalar() or 0


class TrainingContentService(BaseService[TrainingContent, TrainingContentCreate, TrainingContentUpdate]):
    def __init__(self):
        super().__init__(TrainingContent)

    async def get_by_module(
        self, 
        db: AsyncSession, 
        module_id: int
    ) -> List[TrainingContent]:
        """Get all contents for a module"""
        result = await db.execute(
            select(TrainingContent)
            .where(TrainingContent.module_id == module_id)
            .order_by(TrainingContent.content_order)
        )
        return result.scalars().all()

    async def get_with_user_progress(
        self, 
        db: AsyncSession, 
        content_id: int, 
        user_id: int
    ) -> Optional[TrainingContentWithProgress]:
        """Get content with user's progress"""
        # Get content
        content_result = await db.execute(
            select(TrainingContent)
            .where(TrainingContent.id == content_id)
        )
        content = content_result.scalar_one_or_none()
        if not content:
            return None
        
        # Get user progress
        progress_result = await db.execute(
            select(TrainingProgress)
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.content_id == content_id
                )
            )
        )
        progress = progress_result.scalar_one_or_none()
        
        # Build response
        content_data = TrainingContentWithProgress.model_validate(content)
        content_data.user_progress = progress
        return content_data


class TrainingProgressService(BaseService[TrainingProgress, TrainingProgressCreate, TrainingProgressUpdate]):
    def __init__(self):
        super().__init__(TrainingProgress)

    async def get_or_create_progress(
        self, 
        db: AsyncSession, 
        user_id: int, 
        module_id: int, 
        content_id: Optional[int] = None
    ) -> TrainingProgress:
        """Get existing progress or create new one"""
        
        # Get existing progress
        query = select(TrainingProgress).where(
            and_(
                TrainingProgress.user_id == user_id,
                TrainingProgress.module_id == module_id
            )
        )
        if content_id:
            query = query.where(TrainingProgress.content_id == content_id)
        
        result = await db.execute(query)
        progress = result.scalar_one_or_none()
        
        if progress:
            return progress
        
        # Create new progress
        progress_data = TrainingProgressCreate(
            user_id=user_id,
            module_id=module_id,
            content_id=content_id,
            status=TrainingStatus.NOT_STARTED
        )
        return await self.create(db, obj_in=progress_data)

    async def update_progress(
        self, 
        db: AsyncSession, 
        user_id: int, 
        progress_data: ProgressUpdate
    ) -> TrainingProgress:
        """Update user's training progress"""
        # Get module_id from content if content_id is provided
        module_id = None
        if progress_data.content_id:
            # Get the content to find its module_id
            content_result = await db.execute(
                select(TrainingContent)
                .where(TrainingContent.id == progress_data.content_id)
            )
            content = content_result.scalar_one_or_none()
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Training content with id {progress_data.content_id} not found"
                )
            module_id = content.module_id
        else:
            # If content_id is None, we need module_id to be provided
            # But ProgressUpdate doesn't have module_id, so this is an error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="content_id is required to update progress"
            )
        
        # Get or create progress record with correct module_id
        progress = await self.get_or_create_progress(
            db, user_id, module_id, progress_data.content_id
        )
        
        # Update progress
        update_data = progress_data.dict(exclude_unset=True)
        # Remove user_id and content_id from update_data as they're not part of TrainingProgressUpdate
        update_data.pop('user_id', None)
        update_data.pop('content_id', None)
        
        if 'status' in update_data:
            if update_data['status'] == TrainingStatus.IN_PROGRESS and not progress.started_at:
                update_data['started_at'] = datetime.utcnow()
            elif update_data['status'] == TrainingStatus.COMPLETED and not progress.completed_at:
                update_data['completed_at'] = datetime.utcnow()
        
        update_data['last_accessed_at'] = datetime.utcnow()
        
        return await self.update(db, db_obj=progress, obj_in=TrainingProgressUpdate(**update_data))

    async def submit_quiz(
        self, 
        db: AsyncSession, 
        user_id: int, 
        quiz_data: QuizSubmission
    ) -> Dict[str, Any]:
        """Submit quiz answers and calculate score"""
        # Get content
        content_result = await db.execute(
            select(TrainingContent)
            .where(TrainingContent.id == quiz_data.content_id)
        )
        content = content_result.scalar_one_or_none()
        if not content or content.content_type != ContentType.QUIZ:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz content not found"
            )
        
        # Get or create progress
        progress = await self.get_or_create_progress(
            db, user_id, content.module_id, quiz_data.content_id
        )
        
        # Calculate score (simplified - you might want more complex logic)
        quiz_questions = content.quiz_questions or {}
        total_questions = len(quiz_questions)
        correct_answers = 0
        
        for question_id, correct_answer in quiz_questions.items():
            user_answer = quiz_data.answers.get(question_id)
            if user_answer == correct_answer:
                correct_answers += 1
        
        score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        passed = score >= (content.passing_score or 70)
        
        # Update progress
        new_status = TrainingStatus.COMPLETED if passed else TrainingStatus.FAILED
        update_data = TrainingProgressUpdate(
            status=new_status,
            progress_percentage=100 if passed else progress.progress_percentage,
            time_spent_seconds=progress.time_spent_seconds + quiz_data.time_spent_seconds,
            quiz_score=score,
            quiz_attempts=progress.quiz_attempts + 1,
            completed_at=datetime.utcnow() if passed else None
        )
        
        await self.update(db, db_obj=progress, obj_in=update_data)
        
        return {
            "content_id": quiz_data.content_id,
            "score": score,
            "passed": passed,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "attempts": progress.quiz_attempts + 1
        }

    async def get_user_stats(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> TrainingStats:
        """Get comprehensive training statistics for a user"""
        # Get total modules
        total_modules_result = await db.execute(
            select(func.count(TrainingModule.id))
            .where(TrainingModule.is_active == True)
        )
        total_modules = total_modules_result.scalar() or 0
        
        # Get completed modules
        completed_modules_result = await db.execute(
            select(func.count(TrainingProgress.id))
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.content_id.is_(None),  # Module-level progress
                    TrainingProgress.status == TrainingStatus.COMPLETED
                )
            )
        )
        completed_modules = completed_modules_result.scalar() or 0
        
        # Get total contents
        total_contents_result = await db.execute(
            select(func.count(TrainingContent.id))
            .join(TrainingModule)
            .where(TrainingModule.is_active == True)
        )
        total_contents = total_contents_result.scalar() or 0
        
        # Get completed contents
        completed_contents_result = await db.execute(
            select(func.count(TrainingProgress.id))
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.content_id.isnot(None),
                    TrainingProgress.status == TrainingStatus.COMPLETED
                )
            )
        )
        completed_contents = completed_contents_result.scalar() or 0
        
        # Get total time spent
        time_spent_result = await db.execute(
            select(func.sum(TrainingProgress.time_spent_seconds))
            .where(TrainingProgress.user_id == user_id)
        )
        total_time_spent = time_spent_result.scalar() or 0
        
        # Calculate overall progress
        overall_progress = (completed_contents / total_contents * 100) if total_contents > 0 else 0
        
        # Get current and next module
        current_module_result = await db.execute(
            select(TrainingProgress.module_id)
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.status == TrainingStatus.IN_PROGRESS
                )
            )
            .order_by(TrainingProgress.updated_at.desc())
            .limit(1)
        )
        current_module_id = current_module_result.scalar_one_or_none()
        
        next_module_result = await db.execute(
            select(TrainingModule.id)
            .where(
                and_(
                    TrainingModule.is_active == True,
                    TrainingModule.id.notin_(
                        select(TrainingProgress.module_id)
                        .where(
                            and_(
                                TrainingProgress.user_id == user_id,
                                TrainingProgress.status == TrainingStatus.COMPLETED
                            )
                        )
                    )
                )
            )
            .order_by(TrainingModule.module_order)
            .limit(1)
        )
        next_module_id = next_module_result.scalar_one_or_none()
        
        return TrainingStats(
            total_modules=total_modules,
            completed_modules=completed_modules,
            total_contents=total_contents,
            completed_contents=completed_contents,
            total_time_spent_seconds=total_time_spent,
            overall_progress_percentage=round(overall_progress, 2),
            current_module_id=current_module_id,
            next_module_id=next_module_id
        )

    async def get_module_progress_summary(
        self, 
        db: AsyncSession, 
        user_id: int, 
        module_id: int
    ) -> Optional[ModuleProgressSummary]:
        """Get detailed progress summary for a specific module"""
        # Get module
        module_result = await db.execute(
            select(TrainingModule)
            .where(TrainingModule.id == module_id)
        )
        module = module_result.scalar_one_or_none()
        if not module:
            return None
        
        # Get total contents
        total_contents_result = await db.execute(
            select(func.count(TrainingContent.id))
            .where(TrainingContent.module_id == module_id)
        )
        total_contents = total_contents_result.scalar() or 0
        
        # Get completed contents
        completed_contents_result = await db.execute(
            select(func.count(TrainingProgress.id))
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.module_id == module_id,
                    TrainingProgress.content_id.isnot(None),
                    TrainingProgress.status == TrainingStatus.COMPLETED
                )
            )
        )
        completed_contents = completed_contents_result.scalar() or 0
        
        # Get module-level progress
        module_progress_result = await db.execute(
            select(TrainingProgress)
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.module_id == module_id,
                    TrainingProgress.content_id.is_(None)
                )
            )
        )
        module_progress = module_progress_result.scalar_one_or_none()
        
        # Calculate progress percentage
        progress_percentage = (completed_contents / total_contents * 100) if total_contents > 0 else 0
        is_completed = progress_percentage >= 100
        
        # Get time spent
        time_spent_result = await db.execute(
            select(func.sum(TrainingProgress.time_spent_seconds))
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.module_id == module_id
                )
            )
        )
        time_spent = time_spent_result.scalar() or 0
        
        return ModuleProgressSummary(
            module_id=module.id,
            module_title=module.title,
            total_contents=total_contents,
            completed_contents=completed_contents,
            progress_percentage=round(progress_percentage, 2),
            status=module_progress.status if module_progress else TrainingStatus.NOT_STARTED,
            time_spent_seconds=time_spent,
            estimated_duration_minutes=module.estimated_duration_minutes,
            is_completed=is_completed,
            completed_at=module_progress.completed_at if module_progress else None
        )

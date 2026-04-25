from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status
from datetime import datetime

from app.models.training import TrainingModule, TrainingContent, TrainingProgress, ContentType, TrainingStatus
from app.models.user import User, UserType, UserStatus, AreaCoordinator
from app.schemas.training import (
    TrainingModuleCreate, TrainingModuleUpdate, TrainingContentCreate, TrainingContentUpdate,
    TrainingProgressCreate, TrainingProgressUpdate, QuizSubmission, ProgressUpdate,
    TrainingStats, ModuleProgressSummary, ModuleContentProgress, TrainingModuleWithProgress, TrainingContentWithProgress,
    TrainingAnalyticsData, TrainingAnalyticsSummary, TrainingAnalyticsUserRow,
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

    async def get_modules(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[TrainingModule]:
        """List training modules with optional active filter, contents eager-loaded."""
        stmt = (
            select(TrainingModule)
            .options(selectinload(TrainingModule.contents))
            .order_by(TrainingModule.module_order)
            .offset(skip)
            .limit(limit)
        )
        if active_only:
            stmt = stmt.where(TrainingModule.is_active == True)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_active_modules(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TrainingModule]:
        """Get active training modules ordered by module_order"""
        return await self.get_modules(db, skip=skip, limit=limit, active_only=True)

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
        if content_id is not None:
            query = query.where(TrainingProgress.content_id == content_id)
        else:
            query = query.where(TrainingProgress.content_id.is_(None))
        
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

    async def _check_and_update_module_completion(
        self,
        db: AsyncSession,
        user_id: int,
        module_id: int
    ) -> Optional[TrainingProgress]:
        """Check if all required contents in a module are completed and update module-level progress"""
        # Get all required contents for this module
        required_contents_result = await db.execute(
            select(TrainingContent)
            .where(
                and_(
                    TrainingContent.module_id == module_id,
                    TrainingContent.is_required == True
                )
            )
        )
        required_contents = required_contents_result.scalars().all()
        
        if not required_contents:
            # If no required contents, module is considered completed
            # Get or create module-level progress
            module_progress = await self.get_or_create_progress(
                db, user_id, module_id, content_id=None
            )
            if module_progress.status != TrainingStatus.COMPLETED:
                update_data = TrainingProgressUpdate(
                    status=TrainingStatus.COMPLETED,
                    progress_percentage=100,
                    completed_at=datetime.utcnow() if not module_progress.completed_at else module_progress.completed_at
                )
                return await self.update(db, db_obj=module_progress, obj_in=update_data)
            return module_progress
        
        # Check if all required contents are completed
        required_content_ids = [content.id for content in required_contents]
        completed_contents_result = await db.execute(
            select(func.count(TrainingProgress.id))
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.module_id == module_id,
                    TrainingProgress.content_id.in_(required_content_ids),
                    TrainingProgress.status == TrainingStatus.COMPLETED
                )
            )
        )
        completed_count = completed_contents_result.scalar() or 0
        
        # If all required contents are completed, update module-level progress
        if completed_count == len(required_contents):
            # Get or create module-level progress
            module_progress = await self.get_or_create_progress(
                db, user_id, module_id, content_id=None
            )
            
            # Only update if not already completed
            if module_progress.status != TrainingStatus.COMPLETED:
                # Calculate total time spent on all contents in the module
                time_spent_result = await db.execute(
                    select(func.sum(TrainingProgress.time_spent_seconds))
                    .where(
                        and_(
                            TrainingProgress.user_id == user_id,
                            TrainingProgress.module_id == module_id
                        )
                    )
                )
                total_time_spent = time_spent_result.scalar() or 0
                
                update_data = TrainingProgressUpdate(
                    status=TrainingStatus.COMPLETED,
                    progress_percentage=100,
                    time_spent_seconds=total_time_spent,
                    completed_at=datetime.utcnow() if not module_progress.completed_at else module_progress.completed_at
                )
                return await self.update(db, db_obj=module_progress, obj_in=update_data)
            return module_progress
        
        return None

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
        
        updated_progress = await self.update(db, db_obj=progress, obj_in=TrainingProgressUpdate(**update_data))
        
        # Check if content was marked as completed, then check module completion
        if 'status' in update_data and update_data['status'] == TrainingStatus.COMPLETED:
            await self._check_and_update_module_completion(db, user_id, module_id)
        
        return updated_progress

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
        
        # If quiz was passed (completed), check module completion
        if passed:
            await self._check_and_update_module_completion(db, user_id, content.module_id)
        
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
        
        # Get all module contents (ordered) for content-level status
        contents_result = await db.execute(
            select(TrainingContent)
            .where(TrainingContent.module_id == module_id)
            .order_by(TrainingContent.content_order)
        )
        module_contents = contents_result.scalars().all()
        total_contents = len(module_contents)
        
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

        # Get content-level progress records
        content_progress_result = await db.execute(
            select(TrainingProgress)
            .where(
                and_(
                    TrainingProgress.user_id == user_id,
                    TrainingProgress.module_id == module_id,
                    TrainingProgress.content_id.isnot(None)
                )
            )
        )
        content_progress_map = {
            progress.content_id: progress
            for progress in content_progress_result.scalars().all()
            if progress.content_id is not None
        }

        contents = []
        for content in module_contents:
            content_progress = content_progress_map.get(content.id)
            contents.append(
                ModuleContentProgress(
                    content_id=content.id,
                    title=content.title,
                    content_type=content.content_type,
                    content_order=content.content_order,
                    is_required=content.is_required,
                    status=content_progress.status if content_progress else TrainingStatus.NOT_STARTED,
                    progress_percentage=content_progress.progress_percentage if content_progress else 0,
                    time_spent_seconds=content_progress.time_spent_seconds if content_progress else 0,
                    completed_at=content_progress.completed_at if content_progress else None,
                )
            )
        
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
            completed_at=module_progress.completed_at if module_progress else None,
            contents=contents
        )

    async def get_admin_training_analytics(self, db: AsyncSession) -> TrainingAnalyticsData:
        """Roll up training progress for all active ATP (area coordinator) users against active modules."""
        total_modules_result = await db.execute(
            select(func.count())
            .select_from(TrainingModule)
            .where(TrainingModule.is_active == True)
        )
        total_active_modules = int(total_modules_result.scalar() or 0)

        atp_stmt = (
            select(User.id, User.full_name, User.email, User.phone_number, AreaCoordinator.atp_uuid)
            .join(AreaCoordinator, AreaCoordinator.id == User.id)
            .where(
                User.user_type == UserType.AREA_COORDINATOR,
                User.status == UserStatus.ACTIVE,
            )
            .order_by(User.full_name)
        )
        atp_result = await db.execute(atp_stmt)
        atp_rows = atp_result.all()
        atp_ids = [row.id for row in atp_rows]
        total_atps = len(atp_ids)

        if not atp_ids:
            summary = TrainingAnalyticsSummary(
                total_atps=0,
                total_active_training_modules=total_active_modules,
                total_module_enrollments=0,
                total_content_progress_rows=0,
                atps_completed_all_modules=0,
                completion_rate_percentage=0.0,
                avg_time_spent_seconds=0.0,
                users_not_started=0,
                users_in_progress=0,
                users_completed=0,
                users_failed=0,
                atps_with_any_failed_record=0,
            )
            return TrainingAnalyticsData(summary=summary, users=[])

        completed_stmt = (
            select(
                TrainingProgress.user_id,
                func.count(func.distinct(TrainingProgress.module_id)).label("n_completed"),
            )
            .join(TrainingModule, TrainingModule.id == TrainingProgress.module_id)
            .where(
                TrainingProgress.user_id.in_(atp_ids),
                TrainingModule.is_active == True,
                TrainingProgress.content_id.is_(None),
                TrainingProgress.status == TrainingStatus.COMPLETED,
            )
            .group_by(TrainingProgress.user_id)
        )
        completed_map = {
            uid: int(n or 0) for uid, n in (await db.execute(completed_stmt)).all()
        }

        failed_stmt = (
            select(TrainingProgress.user_id)
            .distinct()
            .join(TrainingModule, TrainingModule.id == TrainingProgress.module_id)
            .where(
                TrainingProgress.user_id.in_(atp_ids),
                TrainingModule.is_active == True,
                TrainingProgress.status == TrainingStatus.FAILED,
            )
        )
        failed_user_ids = {row[0] for row in (await db.execute(failed_stmt)).all()}

        activity_stmt = (
            select(TrainingProgress.user_id)
            .distinct()
            .join(TrainingModule, TrainingModule.id == TrainingProgress.module_id)
            .where(
                TrainingProgress.user_id.in_(atp_ids),
                TrainingModule.is_active == True,
                or_(
                    and_(
                        TrainingProgress.content_id.isnot(None),
                        TrainingProgress.status != TrainingStatus.NOT_STARTED,
                    ),
                    and_(
                        TrainingProgress.content_id.is_(None),
                        or_(
                            TrainingProgress.status != TrainingStatus.NOT_STARTED,
                            TrainingProgress.started_at.isnot(None),
                        ),
                    ),
                ),
            )
        )
        activity_user_ids = {row[0] for row in (await db.execute(activity_stmt)).all()}

        time_stmt = (
            select(
                TrainingProgress.user_id,
                func.coalesce(func.sum(TrainingProgress.time_spent_seconds), 0).label("total_seconds"),
            )
            .where(TrainingProgress.user_id.in_(atp_ids))
            .group_by(TrainingProgress.user_id)
        )
        time_map = {uid: int(t or 0) for uid, t in (await db.execute(time_stmt)).all()}

        last_stmt = (
            select(
                TrainingProgress.user_id,
                func.max(
                    func.coalesce(
                        TrainingProgress.last_accessed_at,
                        TrainingProgress.updated_at,
                    )
                ).label("last_ts"),
            )
            .where(TrainingProgress.user_id.in_(atp_ids))
            .group_by(TrainingProgress.user_id)
        )
        last_map = {
            uid: ts
            for uid, ts in (await db.execute(last_stmt)).all()
            if ts is not None
        }

        enroll_stmt = (
            select(func.count(TrainingProgress.id))
            .join(TrainingModule, TrainingModule.id == TrainingProgress.module_id)
            .where(
                TrainingProgress.user_id.in_(atp_ids),
                TrainingModule.is_active == True,
                TrainingProgress.content_id.is_(None),
            )
        )
        total_module_enrollments = int((await db.execute(enroll_stmt)).scalar() or 0)

        all_progress_stmt = select(func.count(TrainingProgress.id)).where(
            TrainingProgress.user_id.in_(atp_ids)
        )
        total_content_progress_rows = int((await db.execute(all_progress_stmt)).scalar() or 0)

        users_out: List[TrainingAnalyticsUserRow] = []
        users_not_started = 0
        users_in_progress = 0
        users_completed = 0
        users_failed = 0
        atps_completed_all_modules = 0

        for row in atp_rows:
            uid = row.id
            completed_modules = completed_map.get(uid, 0)
            has_failed = uid in failed_user_ids
            has_activity = uid in activity_user_ids
            total_time = time_map.get(uid, 0)
            last_activity_at = last_map.get(uid)

            if total_active_modules == 0:
                overall = TrainingStatus.NOT_STARTED
                progress_pct = 0.0
            elif completed_modules >= total_active_modules:
                overall = TrainingStatus.COMPLETED
                progress_pct = 100.0
                atps_completed_all_modules += 1
            elif has_failed:
                overall = TrainingStatus.FAILED
                progress_pct = round((completed_modules / total_active_modules) * 100, 2)
            elif has_activity:
                overall = TrainingStatus.IN_PROGRESS
                progress_pct = round((completed_modules / total_active_modules) * 100, 2)
            else:
                overall = TrainingStatus.NOT_STARTED
                progress_pct = round((completed_modules / total_active_modules) * 100, 2)

            if overall == TrainingStatus.NOT_STARTED:
                users_not_started += 1
            elif overall == TrainingStatus.IN_PROGRESS:
                users_in_progress += 1
            elif overall == TrainingStatus.COMPLETED:
                users_completed += 1
            else:
                users_failed += 1

            users_out.append(
                TrainingAnalyticsUserRow(
                    user_id=uid,
                    full_name=row.full_name,
                    email=row.email,
                    phone_number=row.phone_number,
                    atp_uuid=row.atp_uuid,
                    overall_training_status=overall,
                    completed_modules=completed_modules,
                    total_active_modules=total_active_modules,
                    overall_progress_percentage=progress_pct,
                    total_time_spent_seconds=total_time,
                    last_activity_at=last_activity_at,
                )
            )

        time_totals = [time_map.get(uid, 0) for uid in atp_ids]
        avg_time = sum(time_totals) / total_atps if total_atps else 0.0
        completion_rate = (
            (atps_completed_all_modules / total_atps) * 100.0 if total_atps else 0.0
        )

        summary = TrainingAnalyticsSummary(
            total_atps=total_atps,
            total_active_training_modules=total_active_modules,
            total_module_enrollments=total_module_enrollments,
            total_content_progress_rows=total_content_progress_rows,
            atps_completed_all_modules=atps_completed_all_modules,
            completion_rate_percentage=round(completion_rate, 2),
            avg_time_spent_seconds=round(avg_time, 2),
            users_not_started=users_not_started,
            users_in_progress=users_in_progress,
            users_completed=users_completed,
            users_failed=users_failed,
            atps_with_any_failed_record=len(failed_user_ids),
        )
        return TrainingAnalyticsData(summary=summary, users=users_out)

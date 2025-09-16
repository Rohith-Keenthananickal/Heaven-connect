from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.training import ContentType, TrainingStatus
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationInfo


# Base schemas
class TrainingContentBase(BaseModel):
    content_type: ContentType
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    content_order: int = Field(default=0, ge=0)
    is_required: bool = Field(default=True)
    video_duration_seconds: Optional[int] = Field(None, ge=0)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    quiz_questions: Optional[Dict[str, Any]] = None
    passing_score: Optional[int] = Field(None, ge=0, le=100)


class TrainingModuleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    module_order: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)


class TrainingProgressBase(BaseModel):
    user_id: int = Field(..., gt=0)
    module_id: int = Field(..., gt=0)
    content_id: Optional[int] = Field(None, gt=0)
    status: TrainingStatus = Field(default=TrainingStatus.NOT_STARTED)
    progress_percentage: int = Field(default=0, ge=0, le=100)
    time_spent_seconds: int = Field(default=0, ge=0)
    quiz_score: Optional[int] = Field(None, ge=0, le=100)
    quiz_attempts: int = Field(default=0, ge=0)


# Create schemas
class TrainingContentCreate(TrainingContentBase):
    pass


class TrainingModuleCreate(TrainingModuleBase):
    contents: Optional[List[TrainingContentCreate]] = None


class TrainingProgressCreate(TrainingProgressBase):
    pass


# Update schemas
class TrainingContentUpdate(BaseModel):
    content_type: Optional[ContentType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    content_order: Optional[int] = Field(None, ge=0)
    is_required: Optional[bool] = None
    video_duration_seconds: Optional[int] = Field(None, ge=0)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    quiz_questions: Optional[Dict[str, Any]] = None
    passing_score: Optional[int] = Field(None, ge=0, le=100)


class TrainingModuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    module_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)


class TrainingProgressUpdate(BaseModel):
    status: Optional[TrainingStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    time_spent_seconds: Optional[int] = Field(None, ge=0)
    quiz_score: Optional[int] = Field(None, ge=0, le=100)
    quiz_attempts: Optional[int] = Field(None, ge=0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None


# Response schemas
class TrainingContentResponse(TrainingContentBase):
    id: int
    module_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrainingModuleResponse(TrainingModuleBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    contents: Optional[List[TrainingContentResponse]] = None

    class Config:
        from_attributes = True


class TrainingProgressResponse(TrainingProgressBase):
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Detailed response schemas with relationships
class TrainingModuleWithProgress(TrainingModuleResponse):
    user_progress: Optional[TrainingProgressResponse] = None
    total_contents: int = 0
    completed_contents: int = 0


class TrainingContentWithProgress(TrainingContentResponse):
    user_progress: Optional[TrainingProgressResponse] = None


# Specialized schemas for specific operations
class QuizSubmission(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    content_id: int = Field(..., gt=0)
    answers: Dict[str, Any] = Field(..., description="User's answers to quiz questions")
    time_spent_seconds: int = Field(..., ge=0)


class QuizResult(BaseModel):
    content_id: int
    score: int
    passed: bool
    total_questions: int
    correct_answers: int
    attempts: int


class ProgressUpdate(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    content_id: Optional[int] = Field(None, gt=0)
    progress_percentage: int = Field(..., ge=0, le=100)
    time_spent_seconds: int = Field(..., ge=0)
    status: Optional[TrainingStatus] = None


class TrainingStats(BaseModel):
    total_modules: int
    completed_modules: int
    total_contents: int
    completed_contents: int
    total_time_spent_seconds: int
    overall_progress_percentage: float
    current_module_id: Optional[int] = None
    next_module_id: Optional[int] = None


class ModuleProgressSummary(BaseModel):
    module_id: int
    module_title: str
    total_contents: int
    completed_contents: int
    progress_percentage: float
    status: TrainingStatus
    time_spent_seconds: int
    estimated_duration_minutes: Optional[int] = None
    is_completed: bool = False
    completed_at: Optional[datetime] = None


# API Response Models following the established pattern
class TrainingModuleCreateAPIResponse(BaseModel):
    """Response schema for training module creation"""
    status: str = "success"
    data: 'TrainingModuleResponse'
    message: str = "Training module created successfully"


class TrainingModuleGetAPIResponse(BaseModel):
    """Response schema for single training module retrieval"""
    status: str = "success"
    data: 'TrainingModuleResponse'
    message: str = "Training module retrieved successfully"


class TrainingModuleListAPIResponse(BaseModel):
    """Response schema for training module list endpoints"""
    status: str = "success"
    data: List['TrainingModuleResponse']
    message: str = "Training modules retrieved successfully"


class TrainingModuleUpdateAPIResponse(BaseModel):
    """Response schema for training module updates"""
    status: str = "success"
    data: 'TrainingModuleResponse'
    message: str = "Training module updated successfully"


class TrainingModuleDeleteAPIResponse(BaseModel):
    """Response schema for training module deletion"""
    status: str = "success"
    data: dict
    message: str = "Training module deleted successfully"


class TrainingContentCreateAPIResponse(BaseModel):
    """Response schema for training content creation"""
    status: str = "success"
    data: 'TrainingContentResponse'
    message: str = "Training content created successfully"


class TrainingContentGetAPIResponse(BaseModel):
    """Response schema for single training content retrieval"""
    status: str = "success"
    data: 'TrainingContentWithProgress'
    message: str = "Training content retrieved successfully"


class TrainingContentListAPIResponse(BaseModel):
    """Response schema for training content list endpoints"""
    status: str = "success"
    data: List['TrainingContentResponse']
    message: str = "Training contents retrieved successfully"


class TrainingContentUpdateAPIResponse(BaseModel):
    """Response schema for training content updates"""
    status: str = "success"
    data: 'TrainingContentResponse'
    message: str = "Training content updated successfully"


class TrainingContentDeleteAPIResponse(BaseModel):
    """Response schema for training content deletion"""
    status: str = "success"
    data: dict
    message: str = "Training content deleted successfully"


class TrainingProgressUpdateAPIResponse(BaseModel):
    """Response schema for training progress updates"""
    status: str = "success"
    data: 'TrainingProgressResponse'
    message: str = "Training progress updated successfully"


class QuizSubmitAPIResponse(BaseModel):
    """Response schema for quiz submission"""
    status: str = "success"
    data: 'QuizResult'
    message: str = "Quiz submitted successfully"


class TrainingStatsAPIResponse(BaseModel):
    """Response schema for training statistics"""
    status: str = "success"
    data: 'TrainingStats'
    message: str = "Training statistics retrieved successfully"


class ModuleProgressAPIResponse(BaseModel):
    """Response schema for module progress summary"""
    status: str = "success"
    data: 'ModuleProgressSummary'
    message: str = "Module progress retrieved successfully"


class UserTrainingModulesAPIResponse(BaseModel):
    """Response schema for user training modules with progress"""
    status: str = "success"
    data: List['TrainingModuleWithProgress']
    message: str = "User training modules retrieved successfully"


class TrainingAnalyticsAPIResponse(BaseModel):
    """Response schema for training analytics"""
    status: str = "success"
    data: List[dict]
    message: str = "Training analytics retrieved successfully"

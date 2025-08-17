"""
Performance Management models for HRMS-SAAS system.
Handles performance reviews, goals, ratings, and feedback.
"""

from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .base import BaseUUIDModel

if TYPE_CHECKING:
    from .employee import Employee
    from .user import User


class ReviewStatus(str, enum.Enum):
    """Performance review status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ReviewType(str, enum.Enum):
    """Performance review type enumeration."""
    ANNUAL = "annual"
    SEMI_ANNUAL = "semi-annual"
    QUARTERLY = "quarterly"
    PROBATION = "probation"
    PROJECT_BASED = "project-based"
    EXIT = "exit"


class GoalStatus(str, enum.Enum):
    """Goal status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    ACHIEVED = "achieved"
    PARTIALLY_ACHIEVED = "partially-achieved"
    NOT_ACHIEVED = "not-achieved"
    CANCELLED = "cancelled"


class GoalPriority(str, enum.Enum):
    """Goal priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PerformanceReview(BaseUUIDModel):
    """Performance Review model for tracking employee evaluations."""
    __tablename__ = "performance_reviews"
    
    # Basic Information
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    reviewer_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    review_period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    review_period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("public.tenants.id"),
        nullable=False,
        index=True
    )
    
    # Review Details
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus), default=ReviewStatus.DRAFT, nullable=False)
    review_type: Mapped[ReviewType] = mapped_column(Enum(ReviewType), default=ReviewType.ANNUAL, nullable=False)
    overall_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Dates
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    submitted_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    approved_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Review Content
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    development_areas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    employee_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hr_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Ratings and Scores
    categories: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    competencies: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    kpis: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Goals for Next Period
    next_period_goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    career_development_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    training_recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    is_self_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_360_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id], back_populates="performance_reviews")
    reviewer: Mapped["Employee"] = relationship("Employee", foreign_keys=[reviewer_id])
    goals: Mapped[List["PerformanceGoal"]] = relationship("PerformanceGoal", back_populates="review")
    
    def __repr__(self):
        return f"<PerformanceReview(id={self.id}, employee_id='{self.employee_id}', status='{self.status}')>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if review is overdue."""
        if not self.due_date:
            return False
        return self.due_date < date.today() and self.status in [ReviewStatus.DRAFT, ReviewStatus.IN_PROGRESS]
    
    @property
    def duration_days(self) -> int:
        """Calculate review period duration in days."""
        return (self.review_period_end - self.review_period_start).days
    
    @property
    def is_completed(self) -> bool:
        """Check if review is completed."""
        return self.status == ReviewStatus.COMPLETED


class PerformanceGoal(BaseUUIDModel):
    """Performance Goal model for tracking employee objectives."""
    __tablename__ = "performance_goals"
    
    # Basic Information
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    review_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("performance_reviews.id"), nullable=True, index=True)
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("public.tenants.id"),
        nullable=False,
        index=True
    )
    
    # Goal Details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus), default=GoalStatus.DRAFT, nullable=False)
    priority: Mapped[GoalPriority] = mapped_column(Enum(GoalPriority), default=GoalPriority.MEDIUM, nullable=False)
    
    # Dates
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Progress and Measurement
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    measurement_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success_metrics: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Rating and Feedback
    achievement_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    manager_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    employee_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Goal Classification
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_stretch_goal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_team_goal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id], back_populates="goals")
    review: Mapped[Optional["PerformanceReview"]] = relationship("PerformanceReview", back_populates="goals")
    
    def __repr__(self):
        return f"<PerformanceGoal(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if goal is overdue."""
        if not self.target_date:
            return False
        return self.target_date < date.today() and self.status not in [GoalStatus.ACHIEVED, GoalStatus.CANCELLED]
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining to target date."""
        if not self.target_date:
            return None
        delta = self.target_date - date.today()
        return delta.days if delta.days > 0 else 0
    
    @property
    def is_completed(self) -> bool:
        """Check if goal is completed."""
        return self.status in [GoalStatus.ACHIEVED, GoalStatus.PARTIALLY_ACHIEVED, GoalStatus.NOT_ACHIEVED]


class PerformanceFeedback(BaseUUIDModel):
    """Performance Feedback model for continuous feedback."""
    __tablename__ = "performance_feedback"
    
    # Basic Information
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    feedback_giver_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    review_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("performance_reviews.id"), nullable=True, index=True)
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("public.tenants.id"),
        nullable=False,
        index=True
    )
    
    # Feedback Details
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'positive', 'constructive', 'recognition', etc.
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Context
    project_context: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    situation_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Privacy and Visibility
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    visibility_level: Mapped[str] = mapped_column(String(20), default="manager", nullable=False)  # 'employee', 'manager', 'hr', 'team'
    
    # Metadata
    tags: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    feedback_giver: Mapped["Employee"] = relationship("Employee", foreign_keys=[feedback_giver_id])
    review: Mapped[Optional["PerformanceReview"]] = relationship("PerformanceReview")
    
    def __repr__(self):
        return f"<PerformanceFeedback(id={self.id}, employee_id='{self.employee_id}', type='{self.feedback_type}')>"


class PerformanceMetric(BaseUUIDModel):
    """Performance Metric model for tracking KPIs and measurements."""
    __tablename__ = "performance_metrics"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    # Basic Information
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_category: Mapped[str] = mapped_column(String(50), nullable=False)  # 'sales', 'quality', 'efficiency', etc.
    
    # Metric Details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    measurement_unit: Mapped[str] = mapped_column(String(50), nullable=False)  # 'percentage', 'number', 'currency', etc.
    measurement_period: Mapped[str] = mapped_column(String(20), nullable=False)  # 'daily', 'weekly', 'monthly', 'quarterly', 'annually'
    
    # Values and Targets
    target_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Dates
    measurement_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    
    def __repr__(self):
        return f"<PerformanceMetric(id={self.id}, name='{self.metric_name}', value={self.current_value})>"
    
    @property
    def achievement_percentage(self) -> Optional[float]:
        """Calculate achievement percentage against target."""
        if not self.target_value or not self.current_value:
            return None
        return (self.current_value / self.target_value) * 100
    
    @property
    def is_target_met(self) -> Optional[bool]:
        """Check if target is met."""
        if not self.target_value or not self.current_value:
            return None
        return self.current_value >= self.target_value

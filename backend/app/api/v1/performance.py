"""
Performance Management API endpoints for HRMS-SAAS.
Handles performance reviews, goals, ratings, and feedback.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from datetime import date, datetime

from ...core.security import get_current_user, require_permission
from ...core.database import get_session
from ...models.performance import (
    PerformanceReview, PerformanceGoal, PerformanceFeedback, PerformanceMetric,
    ReviewStatus, ReviewType, GoalStatus, GoalPriority
)
from ...models.employee import Employee
from ...models.user import User

router = APIRouter()


# Request/Response Models
class PerformanceReviewBase(BaseModel):
    """Base performance review model."""
    employee_id: str = Field(..., description="Employee ID")
    reviewer_id: str = Field(..., description="Reviewer (Manager/HR) ID")
    review_period_start: date = Field(..., description="Review period start date")
    review_period_end: date = Field(..., description="Review period end date")
    review_type: str = Field(default="annual", description="Type of review")
    due_date: Optional[date] = Field(None, description="Review due date")
    strengths: Optional[str] = Field(None, description="Employee strengths")
    improvements: Optional[str] = Field(None, description="Areas for improvement")
    achievements: Optional[str] = Field(None, description="Key achievements")
    development_areas: Optional[str] = Field(None, description="Development areas")
    feedback: Optional[str] = Field(None, description="Manager feedback")
    employee_comments: Optional[str] = Field(None, description="Employee self-assessment")
    manager_comments: Optional[str] = Field(None, description="Manager comments")
    next_period_goals: Optional[str] = Field(None, description="Goals for next period")
    career_development_plan: Optional[str] = Field(None, description="Career development plan")
    training_recommendations: Optional[str] = Field(None, description="Training recommendations")


class PerformanceReviewCreate(PerformanceReviewBase):
    """Performance review creation model."""
    categories: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Rating categories")
    competencies: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Competency ratings")
    kpis: Optional[Dict[str, Any]] = Field(default_factory=dict, description="KPI ratings")


class PerformanceReviewUpdate(BaseModel):
    """Performance review update model."""
    status: Optional[str] = Field(None, description="Review status")
    overall_rating: Optional[float] = Field(None, ge=0, le=5, description="Overall rating")
    review_date: Optional[date] = Field(None, description="Review completion date")
    strengths: Optional[str] = Field(None, description="Employee strengths")
    improvements: Optional[str] = Field(None, description="Areas for improvement")
    achievements: Optional[str] = Field(None, description="Key achievements")
    development_areas: Optional[str] = Field(None, description="Development areas")
    feedback: Optional[str] = Field(None, description="Manager feedback")
    employee_comments: Optional[str] = Field(None, description="Employee self-assessment")
    manager_comments: Optional[str] = Field(None, description="Manager comments")
    categories: Optional[Dict[str, Any]] = Field(None, description="Rating categories")
    competencies: Optional[Dict[str, Any]] = Field(None, description="Competency ratings")
    kpis: Optional[Dict[str, Any]] = Field(None, description="KPI ratings")
    next_period_goals: Optional[str] = Field(None, description="Goals for next period")
    career_development_plan: Optional[str] = Field(None, description="Career development plan")
    training_recommendations: Optional[str] = Field(None, description="Training recommendations")


class PerformanceReviewResponse(PerformanceReviewBase):
    """Performance review response model."""
    id: str
    status: str
    overall_rating: Optional[float]
    review_date: Optional[date]
    employee_name: Optional[str]
    reviewer_name: Optional[str]
    categories: Dict[str, Any]
    competencies: Dict[str, Any]
    kpis: Dict[str, Any]
    is_overdue: bool
    duration_days: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PerformanceGoalBase(BaseModel):
    """Base performance goal model."""
    employee_id: str = Field(..., description="Employee ID")
    title: str = Field(..., max_length=200, description="Goal title")
    description: Optional[str] = Field(None, description="Goal description")
    priority: str = Field(default="medium", description="Goal priority")
    category: Optional[str] = Field(None, description="Goal category")
    start_date: Optional[date] = Field(None, description="Goal start date")
    target_date: Optional[date] = Field(None, description="Goal target date")
    measurement_criteria: Optional[str] = Field(None, description="How success is measured")
    is_stretch_goal: bool = Field(default=False, description="Whether this is a stretch goal")
    is_team_goal: bool = Field(default=False, description="Whether this is a team goal")
    weight: float = Field(default=1.0, ge=0, le=10, description="Goal weight/importance")


class PerformanceGoalCreate(PerformanceGoalBase):
    """Performance goal creation model."""
    success_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Success metrics")


class PerformanceGoalUpdate(BaseModel):
    """Performance goal update model."""
    status: Optional[str] = Field(None, description="Goal status")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    achievement_rating: Optional[float] = Field(None, ge=0, le=5, description="Achievement rating")
    completion_date: Optional[date] = Field(None, description="Goal completion date")
    manager_feedback: Optional[str] = Field(None, description="Manager feedback")
    employee_notes: Optional[str] = Field(None, description="Employee notes")
    success_metrics: Optional[Dict[str, Any]] = Field(None, description="Success metrics")


class PerformanceGoalResponse(PerformanceGoalBase):
    """Performance goal response model."""
    id: str
    status: str
    progress_percentage: float
    achievement_rating: Optional[float]
    completion_date: Optional[date]
    manager_feedback: Optional[str]
    employee_notes: Optional[str]
    success_metrics: Dict[str, Any]
    employee_name: Optional[str]
    is_overdue: bool
    days_remaining: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PerformanceSummary(BaseModel):
    """Performance management summary model."""
    total_reviews: int
    completed_reviews: int
    pending_reviews: int
    overdue_reviews: int
    average_rating: Optional[float]
    total_goals: int
    active_goals: int
    achieved_goals: int
    overdue_goals: int
    department_ratings: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]


# API Endpoints
@router.get("/summary", response_model=PerformanceSummary)
async def get_performance_summary(
    session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get performance management summary and metrics."""
    
    # Get performance reviews summary
    review_query = select(PerformanceReview).where(
        PerformanceReview.tenant_id == current_user.tenant_id
    )
    reviews = (await session.execute(review_query)).scalars().all()
    
    total_reviews = len(reviews)
    completed_reviews = len([r for r in reviews if r.status == ReviewStatus.COMPLETED])
    pending_reviews = len([r for r in reviews if r.status == ReviewStatus.IN_PROGRESS])
    overdue_reviews = len([r for r in reviews if r.is_overdue])
    
    # Calculate average rating
    completed_ratings = [r.overall_rating for r in reviews if r.overall_rating and r.status == ReviewStatus.COMPLETED]
    average_rating = sum(completed_ratings) / len(completed_ratings) if completed_ratings else None
    
    # Get goals summary
    goals_query = select(PerformanceGoal).where(
        PerformanceGoal.tenant_id == current_user.tenant_id
    )
    goals = (await session.execute(goals_query)).scalars().all()
    
    total_goals = len(goals)
    active_goals = len([g for g in goals if g.status == GoalStatus.ACTIVE])
    achieved_goals = len([g for g in goals if g.status == GoalStatus.ACHIEVED])
    overdue_goals = len([g for g in goals if g.is_overdue])
    
    # Get department ratings (mock data for now)
    department_ratings = [
        {"department": "Engineering", "rating": 4.3, "count": 15},
        {"department": "Product", "rating": 4.0, "count": 8},
        {"department": "Sales", "rating": 4.2, "count": 12},
        {"department": "Marketing", "rating": 3.9, "count": 6},
        {"department": "HR", "rating": 4.1, "count": 4},
    ]
    
    # Get top performers (mock data for now)
    top_performers = [
        {"name": "John Doe", "rating": 4.8, "department": "Engineering"},
        {"name": "Alice Johnson", "rating": 4.7, "department": "Sales"},
        {"name": "Bob Wilson", "rating": 4.6, "department": "Product"},
        {"name": "Carol Davis", "rating": 4.5, "department": "Marketing"},
    ]
    
    return PerformanceSummary(
        total_reviews=total_reviews,
        completed_reviews=completed_reviews,
        pending_reviews=pending_reviews,
        overdue_reviews=overdue_reviews,
        average_rating=average_rating,
        total_goals=total_goals,
        active_goals=active_goals,
        achieved_goals=achieved_goals,
        overdue_goals=overdue_goals,
        department_ratings=department_ratings,
        top_performers=top_performers
    )


@router.get("/reviews", response_model=List[PerformanceReviewResponse])
async def get_performance_reviews(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by review status"),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get performance reviews with optional filtering."""
    
    query = select(PerformanceReview).options(
        selectinload(PerformanceReview.employee).selectinload(Employee.user),
        selectinload(PerformanceReview.reviewer).selectinload(Employee.user)
    ).where(
        PerformanceReview.tenant_id == current_user.tenant_id
    )
    
    # Apply filters
    if status:
        query = query.where(PerformanceReview.status == status)
    if employee_id:
        query = query.where(PerformanceReview.employee_id == employee_id)
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(desc(PerformanceReview.created_at))
    
    reviews = (await session.execute(query)).scalars().all()
    
    # Enhance response with additional data
    response_reviews = []
    for review in reviews:
        review_dict = {
            **review.__dict__,
            "employee_name": review.employee.user.full_name if review.employee and review.employee.user else "Unknown",
            "reviewer_name": review.reviewer.user.full_name if review.reviewer and review.reviewer.user else "Unknown",
            "is_overdue": review.is_overdue,
            "duration_days": review.duration_days
        }
        response_reviews.append(PerformanceReviewResponse(**review_dict))
    
    return response_reviews


@router.post("/reviews", response_model=PerformanceReviewResponse)
async def create_performance_review(
    review: PerformanceReviewCreate,
    session = Depends(get_session),
    current_user: User = Depends(require_permission("performance:write"))
):
    """Create a new performance review."""
    
    # Verify employee exists
    employee_query = select(Employee).options(selectinload(Employee.user)).where(
        and_(Employee.id == review.employee_id, Employee.tenant_id == current_user.tenant_id)
    )
    employee = (await session.execute(employee_query)).scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Create performance review
    db_review = PerformanceReview(
        **review.model_dump(),
        tenant_id=current_user.tenant_id
    )
    
    session.add(db_review)
    await session.commit()
    await session.refresh(db_review)
    
    # Load relationships
    await session.execute(
        select(PerformanceReview).options(
            selectinload(PerformanceReview.employee).selectinload(Employee.user),
            selectinload(PerformanceReview.reviewer).selectinload(Employee.user)
        ).where(PerformanceReview.id == db_review.id)
    )
    
    # Prepare response
    review_dict = {
        **db_review.__dict__,
        "employee_name": employee.user.full_name if employee.user else "Unknown",
        "reviewer_name": "Current User",  # TODO: Get reviewer name
        "is_overdue": db_review.is_overdue,
        "duration_days": db_review.duration_days
    }
    
    return PerformanceReviewResponse(**review_dict)


@router.get("/reviews/{review_id}", response_model=PerformanceReviewResponse)
async def get_performance_review(
    review_id: str,
    session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific performance review by ID."""
    
    query = select(PerformanceReview).options(
        selectinload(PerformanceReview.employee).selectinload(Employee.user),
        selectinload(PerformanceReview.reviewer).selectinload(Employee.user)
    ).where(
        and_(
            PerformanceReview.id == review_id,
            PerformanceReview.tenant_id == current_user.tenant_id
        )
    )
    
    review = (await session.execute(query)).scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance review not found"
        )
    
    # Prepare response
    review_dict = {
        **review.__dict__,
        "employee_name": review.employee.user.full_name if review.employee and review.employee.user else "Unknown",
        "reviewer_name": review.reviewer.user.full_name if review.reviewer and review.reviewer.user else "Unknown",
        "is_overdue": review.is_overdue,
        "duration_days": review.duration_days
    }
    
    return PerformanceReviewResponse(**review_dict)


@router.put("/reviews/{review_id}", response_model=PerformanceReviewResponse)
async def update_performance_review(
    review_id: str,
    review_update: PerformanceReviewUpdate,
    session = Depends(get_session),
    current_user: User = Depends(require_permission("performance:write"))
):
    """Update a performance review."""
    
    # Get existing review
    query = select(PerformanceReview).options(
        selectinload(PerformanceReview.employee).selectinload(Employee.user),
        selectinload(PerformanceReview.reviewer).selectinload(Employee.user)
    ).where(
        and_(
            PerformanceReview.id == review_id,
            PerformanceReview.tenant_id == current_user.tenant_id
        )
    )
    
    review = (await session.execute(query)).scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance review not found"
        )
    
    # Update review fields
    update_data = review_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(review, field):
            setattr(review, field, value)
    
    # Set review date if status is being completed
    if review_update.status == ReviewStatus.COMPLETED.value and not review.review_date:
        review.review_date = date.today()
    
    await session.commit()
    await session.refresh(review)
    
    # Prepare response
    review_dict = {
        **review.__dict__,
        "employee_name": review.employee.user.full_name if review.employee and review.employee.user else "Unknown",
        "reviewer_name": review.reviewer.user.full_name if review.reviewer and review.reviewer.user else "Unknown",
        "is_overdue": review.is_overdue,
        "duration_days": review.duration_days
    }
    
    return PerformanceReviewResponse(**review_dict)


@router.get("/goals", response_model=List[PerformanceGoalResponse])
async def get_performance_goals(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by goal status"),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get performance goals with optional filtering."""
    
    query = select(PerformanceGoal).options(
        selectinload(PerformanceGoal.employee).selectinload(Employee.user)
    ).where(
        PerformanceGoal.tenant_id == current_user.tenant_id
    )
    
    # Apply filters
    if status:
        query = query.where(PerformanceGoal.status == status)
    if employee_id:
        query = query.where(PerformanceGoal.employee_id == employee_id)
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(desc(PerformanceGoal.created_at))
    
    goals = (await session.execute(query)).scalars().all()
    
    # Enhance response with additional data
    response_goals = []
    for goal in goals:
        goal_dict = {
            **goal.__dict__,
            "employee_name": goal.employee.user.full_name if goal.employee and goal.employee.user else "Unknown",
            "is_overdue": goal.is_overdue,
            "days_remaining": goal.days_remaining
        }
        response_goals.append(PerformanceGoalResponse(**goal_dict))
    
    return response_goals


@router.post("/goals", response_model=PerformanceGoalResponse)
async def create_performance_goal(
    goal: PerformanceGoalCreate,
    session = Depends(get_session),
    current_user: User = Depends(require_permission("performance:write"))
):
    """Create a new performance goal."""
    
    # Verify employee exists
    employee_query = select(Employee).options(selectinload(Employee.user)).where(
        and_(Employee.id == goal.employee_id, Employee.tenant_id == current_user.tenant_id)
    )
    employee = (await session.execute(employee_query)).scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Create performance goal
    db_goal = PerformanceGoal(
        **goal.model_dump(),
        tenant_id=current_user.tenant_id,
        status=GoalStatus.ACTIVE
    )
    
    session.add(db_goal)
    await session.commit()
    await session.refresh(db_goal)
    
    # Prepare response
    goal_dict = {
        **db_goal.__dict__,
        "employee_name": employee.user.full_name if employee.user else "Unknown",
        "is_overdue": db_goal.is_overdue,
        "days_remaining": db_goal.days_remaining
    }
    
    return PerformanceGoalResponse(**goal_dict)


@router.put("/goals/{goal_id}", response_model=PerformanceGoalResponse)
async def update_performance_goal(
    goal_id: str,
    goal_update: PerformanceGoalUpdate,
    session = Depends(get_session),
    current_user: User = Depends(require_permission("performance:write"))
):
    """Update a performance goal."""
    
    # Get existing goal
    query = select(PerformanceGoal).options(
        selectinload(PerformanceGoal.employee).selectinload(Employee.user)
    ).where(
        and_(
            PerformanceGoal.id == goal_id,
            PerformanceGoal.tenant_id == current_user.tenant_id
        )
    )
    
    goal = (await session.execute(query)).scalar_one_or_none()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance goal not found"
        )
    
    # Update goal fields
    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(goal, field):
            setattr(goal, field, value)
    
    # Set completion date if status is being completed
    if goal_update.status and goal_update.status in [GoalStatus.ACHIEVED.value, GoalStatus.NOT_ACHIEVED.value, GoalStatus.PARTIALLY_ACHIEVED.value] and not goal.completion_date:
        goal.completion_date = date.today()
    
    await session.commit()
    await session.refresh(goal)
    
    # Prepare response
    goal_dict = {
        **goal.__dict__,
        "employee_name": goal.employee.user.full_name if goal.employee and goal.employee.user else "Unknown",
        "is_overdue": goal.is_overdue,
        "days_remaining": goal.days_remaining
    }
    
    return PerformanceGoalResponse(**goal_dict)

"""
Dashboard API endpoints for HRMS-SAAS.
Provides analytics, statistics, and overview data.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, and_, or_, extract
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta

from ...core.security import get_current_user, require_permission
from ...core.database import get_session
from ...models.employee import Employee, Department
from ...models.leave import LeaveRequest, LeaveBalance
from ...models.user import User

router = APIRouter()


# Response Models
class DashboardStats(BaseModel):
    """Dashboard statistics response model."""
    total_employees: int
    active_employees: int
    departments_count: int
    pending_leave_requests: int
    total_leave_requests_this_month: int
    new_hires_this_month: int
    upcoming_birthdays: int


class RecentActivity(BaseModel):
    """Recent activity item."""
    id: str
    type: str
    title: str
    description: str
    user_name: str
    timestamp: datetime


class EmployeeGrowthData(BaseModel):
    """Employee growth chart data."""
    labels: List[str]
    datasets: List[Dict[str, Any]]


class DepartmentDistribution(BaseModel):
    """Department distribution data."""
    name: str
    count: int
    percentage: float


class LeaveOverview(BaseModel):
    """Leave overview statistics."""
    total_requests: int
    approved: int
    pending: int
    rejected: int
    monthly_trend: List[Dict[str, Any]]


class UpcomingBirthday(BaseModel):
    """Upcoming birthday item."""
    id: str
    name: str
    department: str
    date: str
    days_until: int


class NewHire(BaseModel):
    """New hire item."""
    id: str
    name: str
    department: str
    hire_date: str
    job_title: str


class NewHiresResponse(BaseModel):
    """New hires response."""
    count: int
    employees: List[NewHire]


class EmployeeStatusDistribution(BaseModel):
    """Employee status distribution."""
    active: int
    inactive: int
    terminated: int
    on_leave: int


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("dashboard:view"))
):
    """Get dashboard statistics."""
    try:
        tenant_id = current_user["tenant_id"]
        current_date = datetime.utcnow().date()
        current_month_start = current_date.replace(day=1)

        # Total and active employees
        total_employees = await db_session.scalar(
            select(func.count(Employee.id)).where(Employee.tenant_id == tenant_id)
        )
        
        active_employees = await db_session.scalar(
            select(func.count(Employee.id)).where(
                and_(Employee.tenant_id == tenant_id, Employee.is_active == True)
            )
        )

        # Departments count
        departments_count = await db_session.scalar(
            select(func.count(Department.id)).where(
                and_(Department.tenant_id == tenant_id, Department.is_active == True)
            )
        )

        # Simplified counts - set to 0 for now to avoid complex queries
        pending_leave_requests = 0
        total_leave_requests_this_month = 0
        new_hires_this_month = await db_session.scalar(
            select(func.count(Employee.id)).where(
                and_(
                    Employee.tenant_id == tenant_id,
                    Employee.hire_date >= current_month_start
                )
            )
        )
        upcoming_count = 0

        return DashboardStats(
            total_employees=total_employees or 0,
            active_employees=active_employees or 0,
            departments_count=departments_count or 0,
            pending_leave_requests=pending_leave_requests,
            total_leave_requests_this_month=total_leave_requests_this_month,
            new_hires_this_month=new_hires_this_month or 0,
            upcoming_birthdays=upcoming_count
        )
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logging.error(f"Dashboard stats error: {str(e)}")
        # Return zeros if there's an error
        return DashboardStats(
            total_employees=0,
            active_employees=0,
            departments_count=0,
            pending_leave_requests=0,
            total_leave_requests_this_month=0,
            new_hires_this_month=0,
            upcoming_birthdays=0
        )


@router.get("/activity", response_model=List[RecentActivity])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Number of recent activities to return"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("dashboard:view"))
):
    """Get recent activity feed."""
    # This is a simplified implementation
    # In a real system, you'd have an activity log table
    return []


@router.get("/employee-growth", response_model=EmployeeGrowthData)
async def get_employee_growth(
    period: str = Query("12months", description="Time period for growth data"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("dashboard:view"))
):
    """Get employee growth chart data."""
    tenant_id = current_user["tenant_id"]
    current_date = datetime.utcnow().date()
    
    # Generate last 12 months data
    months_data = []
    labels = []
    
    for i in range(12):
        month_date = current_date.replace(day=1) - timedelta(days=30 * i)
        next_month = month_date.replace(day=28) + timedelta(days=4)
        next_month = next_month.replace(day=1)
        
        # Count employees hired by this month
        employees_count = await db_session.scalar(
            select(func.count(Employee.id)).where(
                and_(
                    Employee.tenant_id == tenant_id,
                    Employee.hire_date <= month_date
                )
            )
        )
        
        months_data.insert(0, employees_count or 0)
        labels.insert(0, month_date.strftime("%b %Y"))
    
    return EmployeeGrowthData(
        labels=labels,
        datasets=[{
            "label": "Total Employees",
            "data": months_data
        }]
    )


@router.get("/department-distribution", response_model=List[DepartmentDistribution])
async def get_department_distribution(
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("dashboard:view"))
):
    """Get department distribution data."""
    tenant_id = current_user["tenant_id"]
    
    # Get department employee counts
    result = await db_session.execute(
        select(
            Department.name,
            func.count(Employee.id).label('count')
        )
        .select_from(Department.outerjoin(Employee))
        .where(
            and_(
                Department.tenant_id == tenant_id,
                Department.is_active == True
            )
        )
        .group_by(Department.id, Department.name)
        .order_by(func.count(Employee.id).desc())
    )
    
    departments = result.all()
    total_employees = sum(dept.count for dept in departments)
    
    return [
        DepartmentDistribution(
            name=dept.name,
            count=dept.count,
            percentage=round((dept.count / total_employees * 100) if total_employees > 0 else 0, 2)
        )
        for dept in departments
    ]


@router.get("/leave-overview", response_model=LeaveOverview)
async def get_leave_overview(
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("dashboard:view"))
):
    """Get leave overview statistics."""
    tenant_id = current_user["tenant_id"]
    current_date = datetime.utcnow().date()
    current_year = current_date.year
    
    # Total requests this year
    total_requests = await db_session.scalar(
        select(func.count(LeaveRequest.id))
        .select_from(LeaveRequest.join(Employee))
        .where(
            and_(
                Employee.tenant_id == tenant_id,
                extract('year', LeaveRequest.created_at) == current_year
            )
        )
    )
    
    # Requests by status
    approved = await db_session.scalar(
        select(func.count(LeaveRequest.id))
        .select_from(LeaveRequest.join(Employee))
        .where(
            and_(
                Employee.tenant_id == tenant_id,
                LeaveRequest.status == 'APPROVED',
                extract('year', LeaveRequest.created_at) == current_year
            )
        )
    )
    
    pending = await db_session.scalar(
        select(func.count(LeaveRequest.id))
        .select_from(LeaveRequest.join(Employee))
        .where(
            and_(
                Employee.tenant_id == tenant_id,
                LeaveRequest.status == 'PENDING'
            )
        )
    )
    
    rejected = await db_session.scalar(
        select(func.count(LeaveRequest.id))
        .select_from(LeaveRequest.join(Employee))
        .where(
            and_(
                Employee.tenant_id == tenant_id,
                LeaveRequest.status == 'REJECTED',
                extract('year', LeaveRequest.created_at) == current_year
            )
        )
    )
    
    return LeaveOverview(
        total_requests=total_requests or 0,
        approved=approved or 0,
        pending=pending or 0,
        rejected=rejected or 0,
        monthly_trend=[]  # Simplified - would implement monthly breakdown
    )


@router.get("/upcoming-birthdays", response_model=List[UpcomingBirthday])
async def get_upcoming_birthdays(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("dashboard:view"))
):
    """Get upcoming employee birthdays."""
    tenant_id = current_user["tenant_id"]
    current_date = datetime.utcnow().date()
    
    result = await db_session.execute(
        select(Employee, User, Department.name.label('department_name'))
        .select_from(Employee.join(User).outerjoin(Department))
        .where(
            and_(
                Employee.tenant_id == tenant_id,
                Employee.is_active == True,
                Employee.date_of_birth.isnot(None)
            )
        )
    )
    
    employees = result.all()
    upcoming = []
    
    for employee_row in employees:
        employee = employee_row.Employee
        user = employee_row.User
        dept_name = employee_row.department_name or "No Department"
        
        if employee.date_of_birth:
            # Calculate next birthday
            this_year_birthday = employee.date_of_birth.replace(year=current_date.year)
            if this_year_birthday < current_date:
                next_birthday = employee.date_of_birth.replace(year=current_date.year + 1)
            else:
                next_birthday = this_year_birthday
            
            days_until = (next_birthday - current_date).days
            
            if 0 <= days_until <= days:
                upcoming.append(UpcomingBirthday(
                    id=employee.id,
                    name=f"{user.first_name} {user.last_name}",
                    department=dept_name,
                    date=next_birthday.isoformat(),
                    days_until=days_until
                ))
    
    return sorted(upcoming, key=lambda x: x.days_until)


@router.get("/new-hires", response_model=NewHiresResponse)
async def get_new_hires(
    period: str = Query("30days", description="Time period for new hires"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("dashboard:view"))
):
    """Get new hires information."""
    tenant_id = current_user["tenant_id"]
    current_date = datetime.utcnow().date()
    
    # Parse period
    if period == "30days":
        start_date = current_date - timedelta(days=30)
    elif period == "90days":
        start_date = current_date - timedelta(days=90)
    else:
        start_date = current_date - timedelta(days=30)
    
    result = await db_session.execute(
        select(Employee, User, Department.name.label('department_name'))
        .select_from(Employee.join(User).outerjoin(Department))
        .where(
            and_(
                Employee.tenant_id == tenant_id,
                Employee.hire_date >= start_date,
                Employee.hire_date <= current_date
            )
        )
        .order_by(Employee.hire_date.desc())
    )
    
    new_hires = []
    for employee_row in result.all():
        employee = employee_row.Employee
        user = employee_row.User
        dept_name = employee_row.department_name or "No Department"
        
        new_hires.append(NewHire(
            id=employee.id,
            name=f"{user.first_name} {user.last_name}",
            department=dept_name,
            hire_date=employee.hire_date.isoformat(),
            job_title=employee.job_title
        ))
    
    return NewHiresResponse(
        count=len(new_hires),
        employees=new_hires
    )


@router.get("/employees-by-status", response_model=EmployeeStatusDistribution)
async def get_employees_by_status(
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("dashboard:view"))
):
    """Get employee distribution by status."""
    tenant_id = current_user["tenant_id"]
    
    # Count by employment status
    result = await db_session.execute(
        select(
            Employee.employment_status,
            func.count(Employee.id).label('count')
        )
        .where(Employee.tenant_id == tenant_id)
        .group_by(Employee.employment_status)
    )
    
    status_counts = {row.employment_status: row.count for row in result.all()}
    
    return EmployeeStatusDistribution(
        active=status_counts.get('ACTIVE', 0),
        inactive=status_counts.get('INACTIVE', 0),
        terminated=status_counts.get('TERMINATED', 0),
        on_leave=status_counts.get('ON_LEAVE', 0)
    )

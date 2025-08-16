"""
Leave Management API endpoints for HRMS-SAAS.
Handles leave requests, approvals, calendar integration, and management.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta
from enum import Enum

from ...core.security import get_current_user, require_permission
from ...core.database import get_session
from ...models.employee import Employee, Department
from ...models.leave import LeaveRequest, LeaveType, LeaveBalance

router = APIRouter()


# Enums
class LeaveStatus(str, Enum):
    """Leave request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveTypeEnum(str, Enum):
    """Leave types."""
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"
    OTHER = "other"


# Request/Response Models
class LeaveRequestBase(BaseModel):
    """Base leave request model."""
    leave_type: LeaveTypeEnum = Field(..., description="Type of leave")
    start_date: date = Field(..., description="Start date of leave")
    end_date: date = Field(..., description="End date of leave")
    start_time: Optional[str] = Field(None, description="Start time (HH:MM format)")
    end_time: Optional[str] = Field(None, description="End time (HH:MM format)")
    is_half_day: bool = Field(False, description="Whether this is a half-day leave")
    reason: str = Field(..., min_length=1, max_length=1000, description="Reason for leave")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")


class LeaveRequestCreate(LeaveRequestBase):
    """Leave request creation model."""
    employee_id: Optional[str] = Field(None, description="Employee ID (defaults to current user)")


class LeaveRequestUpdate(BaseModel):
    """Leave request update model."""
    start_date: Optional[date] = Field(None)
    end_date: Optional[date] = Field(None)
    start_time: Optional[str] = Field(None)
    end_time: Optional[str] = Field(None)
    is_half_day: Optional[bool] = Field(None)
    reason: Optional[str] = Field(None, min_length=1, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)


class LeaveRequestResponse(BaseModel):
    """Leave request response model."""
    id: str
    employee_id: str
    employee_name: str
    department_name: Optional[str]
    status: LeaveStatus
    requested_days: float
    approved_days: Optional[float]
    approver_id: Optional[str]
    approver_name: Optional[str]
    approval_date: Optional[datetime]
    approval_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveRequestListResponse(BaseModel):
    """Leave request list response model."""
    leave_requests: List[LeaveRequestResponse]
    total: int
    page: int
    size: int
    pages: int


class LeaveApprovalRequest(BaseModel):
    """Leave approval request model."""
    status: LeaveStatus = Field(..., description="Approval status")
    approved_days: Optional[float] = Field(None, ge=0, description="Number of days approved")
    approval_notes: Optional[str] = Field(None, max_length=1000, description="Approval notes")


class LeaveBalanceResponse(BaseModel):
    """Leave balance response model."""
    leave_type: str
    total_days: float
    used_days: float
    remaining_days: float
    pending_days: float


class LeaveCalendarResponse(BaseModel):
    """Leave calendar response model."""
    date: date
    leave_requests: List[LeaveRequestResponse]
    is_holiday: bool
    holiday_name: Optional[str]


# Validators
@validator('end_date')
def validate_end_date(cls, v, values):
    """Validate end date is after start date."""
    if 'start_date' in values and v <= values['start_date']:
        raise ValueError('End date must be after start date')
    return v


@router.post("/", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(
    leave_data: LeaveRequestCreate,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("leave:create"))
):
    """Create a new leave request."""
    try:
        # Determine employee ID
        employee_id = leave_data.employee_id or current_user.get("employee_id")
        if not employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID is required"
            )

        # Verify employee exists and belongs to the same tenant
        employee = await db_session.execute(
            select(Employee).where(
                and_(
                    Employee.id == employee_id,
                    Employee.tenant_id == current_user["tenant_id"]
                )
            )
        )
        employee = employee.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # Check if dates are valid
        if leave_data.start_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be in the past"
            )

        # Calculate requested days
        requested_days = _calculate_leave_days(
            leave_data.start_date,
            leave_data.end_date,
            leave_data.is_half_day
        )

        # Check leave balance
        leave_balance = await _get_leave_balance(employee_id, leave_data.leave_type, db_session)
        if leave_balance.remaining_days < requested_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient leave balance. Available: {leave_balance.remaining_days} days"
            )

        # Check for overlapping leave requests
        overlapping_requests = await _check_overlapping_requests(
            employee_id, leave_data.start_date, leave_data.end_date, db_session
        )
        if overlapping_requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request overlaps with existing approved or pending requests"
            )

        # Create leave request
        leave_request = LeaveRequest(
            employee_id=employee_id,
            leave_type=leave_data.leave_type,
            start_date=leave_data.start_date,
            end_date=leave_data.end_date,
            start_time=leave_data.start_time,
            end_time=leave_data.end_time,
            is_half_day=leave_data.is_half_day,
            reason=leave_data.reason,
            notes=leave_data.notes,
            requested_days=requested_days,
            status=LeaveStatus.PENDING,
            tenant_id=current_user["tenant_id"]
        )
        
        db_session.add(leave_request)
        await db_session.commit()
        await db_session.refresh(leave_request)
        
        return await _enrich_leave_request_response(leave_request, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create leave request"
        )


@router.get("/", response_model=LeaveRequestListResponse)
async def list_leave_requests(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[LeaveStatus] = Query(None, description="Filter by status"),
    leave_type: Optional[LeaveTypeEnum] = Query(None, description="Filter by leave type"),
    employee_id: Optional[str] = Query(None, description="Filter by employee"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("leave:read"))
):
    """List leave requests with filtering and pagination."""
    try:
        # Build query
        query = select(LeaveRequest).where(LeaveRequest.tenant_id == current_user["tenant_id"])
        
        # Apply filters
        if status:
            query = query.where(LeaveRequest.status == status)
        
        if leave_type:
            query = query.where(LeaveRequest.leave_type == leave_type)
        
        if employee_id:
            query = query.where(LeaveRequest.employee_id == employee_id)
        
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        
        # Get total count
        count_query = select(LeaveRequest.id).where(LeaveRequest.tenant_id == current_user["tenant_id"])
        total = await db_session.scalar(select(func.count()).select_from(count_query.subquery()))
        
        # Apply pagination and ordering
        query = query.order_by(LeaveRequest.created_at.desc()).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db_session.execute(query)
        leave_requests = result.scalars().all()
        
        # Enrich responses
        enriched_requests = []
        for request in leave_requests:
            enriched_requests.append(await _enrich_leave_request_response(request, db_session))
        
        return LeaveRequestListResponse(
            leave_requests=enriched_requests,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list leave requests"
        )


@router.get("/{leave_request_id}", response_model=LeaveRequestResponse)
async def get_leave_request(
    leave_request_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("leave:read"))
):
    """Get leave request by ID."""
    try:
        leave_request = await db_session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.id == leave_request_id,
                    LeaveRequest.tenant_id == current_user["tenant_id"]
                )
            )
        )
        leave_request = leave_request.scalar_one_or_none()
        
        if not leave_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )
        
        return await _enrich_leave_request_response(leave_request, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get leave request"
        )


@router.put("/{leave_request_id}", response_model=LeaveRequestResponse)
async def update_leave_request(
    leave_request_id: str,
    leave_data: LeaveRequestUpdate,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("leave:update"))
):
    """Update leave request (only pending requests can be updated)."""
    try:
        leave_request = await db_session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.id == leave_request_id,
                    LeaveRequest.tenant_id == current_user["tenant_id"]
                )
            )
        )
        leave_request = leave_request.scalar_one_or_none()
        
        if not leave_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )
        
        # Only pending requests can be updated
        if leave_request.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be updated"
            )
        
        # Update fields
        update_data = leave_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(leave_request, field, value)
        
        # Recalculate requested days if dates changed
        if 'start_date' in update_data or 'end_date' in update_data or 'is_half_day' in update_data:
            leave_request.requested_days = _calculate_leave_days(
                leave_request.start_date,
                leave_request.end_date,
                leave_request.is_half_day
            )
        
        await db_session.commit()
        await db_session.refresh(leave_request)
        
        return await _enrich_leave_request_response(leave_request, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update leave request"
        )


@router.post("/{leave_request_id}/approve", response_model=LeaveRequestResponse)
async def approve_leave_request(
    leave_request_id: str,
    approval_data: LeaveApprovalRequest,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("leave:approve"))
):
    """Approve or reject a leave request."""
    try:
        leave_request = await db_session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.id == leave_request_id,
                    LeaveRequest.tenant_id == current_user["tenant_id"]
                )
            )
        )
        leave_request = leave_request.scalar_one_or_none()
        
        if not leave_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )
        
        # Only pending requests can be approved/rejected
        if leave_request.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request is not pending approval"
            )
        
        # Update status and approval details
        leave_request.status = approval_data.status
        leave_request.approver_id = current_user["user_id"]
        leave_request.approval_date = datetime.utcnow()
        leave_request.approval_notes = approval_data.approval_notes
        
        if approval_data.approved_days is not None:
            leave_request.approved_days = approval_data.approved_days
        
        await db_session.commit()
        await db_session.refresh(leave_request)
        
        return await _enrich_leave_request_response(leave_request, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve leave request"
        )


@router.delete("/{leave_request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_leave_request(
    leave_request_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("leave:delete"))
):
    """Cancel a leave request (only pending requests can be cancelled)."""
    try:
        leave_request = await db_session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.id == leave_request_id,
                    LeaveRequest.tenant_id == current_user["tenant_id"]
                )
            )
        )
        leave_request = leave_request.scalar_one_or_none()
        
        if not leave_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found"
            )
        
        # Only pending requests can be cancelled
        if leave_request.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be cancelled"
            )
        
        # Cancel the request
        leave_request.status = LeaveStatus.CANCELLED
        await db_session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel leave request"
        )


@router.get("/balance/{employee_id}", response_model=List[LeaveBalanceResponse])
async def get_leave_balance(
    employee_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("leave:read"))
):
    """Get leave balance for an employee."""
    try:
        # Verify employee exists and belongs to the same tenant
        employee = await db_session.execute(
            select(Employee).where(
                and_(
                    Employee.id == employee_id,
                    Employee.tenant_id == current_user["tenant_id"]
                )
            )
        )
        if not employee.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Get leave balances for all types
        balances = []
        for leave_type in LeaveTypeEnum:
            balance = await _get_leave_balance(employee_id, leave_type, db_session)
            balances.append(balance)
        
        return balances
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get leave balance"
        )


@router.get("/calendar/{year}/{month}", response_model=List[LeaveCalendarResponse])
async def get_leave_calendar(
    year: int,
    month: int,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("leave:read"))
):
    """Get leave calendar for a specific month."""
    try:
        # Validate year and month
        if not (1 <= month <= 12):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month"
            )
        
        # Get first and last day of month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get leave requests for the month
        leave_requests = await db_session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.tenant_id == current_user["tenant_id"],
                    LeaveRequest.status == LeaveStatus.APPROVED,
                    or_(
                        and_(LeaveRequest.start_date <= end_date, LeaveRequest.end_date >= start_date)
                    )
                )
            )
        )
        leave_requests = leave_requests.scalars().all()
        
        # Build calendar
        calendar = []
        current_date = start_date
        while current_date <= end_date:
            # Get leave requests for this date
            date_requests = [
                req for req in leave_requests
                if req.start_date <= current_date <= req.end_date
            ]
            
            calendar.append(LeaveCalendarResponse(
                date=current_date,
                leave_requests=date_requests,
                is_holiday=False,  # TODO: Implement holiday checking
                holiday_name=None
            ))
            
            current_date += timedelta(days=1)
        
        return calendar
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get leave calendar"
        )


# Helper functions
def _calculate_leave_days(start_date: date, end_date: date, is_half_day: bool) -> float:
    """Calculate the number of leave days between two dates."""
    if start_date == end_date:
        return 0.5 if is_half_day else 1.0
    
    # Count business days (excluding weekends)
    current_date = start_date
    business_days = 0
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    return float(business_days)


async def _get_leave_balance(employee_id: str, leave_type: LeaveTypeEnum, db_session) -> LeaveBalanceResponse:
    """Get leave balance for an employee and leave type."""
    # TODO: Implement actual leave balance calculation from LeaveBalance model
    # For now, return default values
    return LeaveBalanceResponse(
        leave_type=leave_type.value,
        total_days=25.0,  # Default annual leave
        used_days=0.0,
        remaining_days=25.0,
        pending_days=0.0
    )


async def _check_overlapping_requests(
    employee_id: str, start_date: date, end_date: date, db_session
) -> bool:
    """Check if there are overlapping leave requests."""
    overlapping = await db_session.execute(
        select(LeaveRequest).where(
            and_(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
                or_(
                    and_(LeaveRequest.start_date <= end_date, LeaveRequest.end_date >= start_date)
                )
            )
        )
    )
    return overlapping.scalar_one_or_none() is not None


async def _enrich_leave_request_response(leave_request: LeaveRequest, db_session) -> LeaveRequestResponse:
    """Enrich leave request response with employee and department information."""
    # Get employee information
    employee_result = await db_session.execute(
        select(Employee.first_name, Employee.last_name, Employee.department_id).where(
            Employee.id == leave_request.employee_id
        )
    )
    employee = employee_result.first()
    
    employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"
    department_name = None
    
    if employee and employee.department_id:
        dept_result = await db_session.execute(
            select(Department.name).where(Department.id == employee.department_id)
        )
        department_name = dept_result.scalar_one_or_none()
    
    # Get approver information
    approver_name = None
    if leave_request.approver_id:
        approver_result = await db_session.execute(
            select(Employee.first_name, Employee.last_name).where(
                Employee.id == leave_request.approver_id
            )
        )
        approver = approver_result.first()
        if approver:
            approver_name = f"{approver.first_name} {approver.last_name}"
    
    return LeaveRequestResponse(
        id=leave_request.id,
        employee_id=leave_request.employee_id,
        employee_name=employee_name,
        department_name=department_name,
        leave_type=leave_request.leave_type,
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        start_time=leave_request.start_time,
        end_time=leave_request.end_time,
        is_half_day=leave_request.is_half_day,
        reason=leave_request.reason,
        notes=leave_request.notes,
        status=leave_request.status,
        requested_days=leave_request.requested_days,
        approved_days=leave_request.approved_days,
        approver_id=leave_request.approver_id,
        approver_name=approver_name,
        approval_date=leave_request.approval_date,
        approval_notes=leave_request.approval_notes,
        created_at=leave_request.created_at,
        updated_at=leave_request.updated_at
    )

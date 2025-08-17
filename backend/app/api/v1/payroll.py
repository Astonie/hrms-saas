"""
Payroll API endpoints for HRMS-SAAS.
Handles payroll processing, salary management, and payment operations.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from datetime import date, datetime

from ...core.security import get_current_user, require_permission
from ...core.database import get_session
from ...models.payroll import (
    PayrollEntry, PayrollRun, SalaryStructure,
    PayrollStatus, PaymentMethod, PayrollFrequency
)
from ...models.employee import Employee
from ...models.user import User

router = APIRouter()


# Request/Response Models
class PayrollEntryBase(BaseModel):
    """Base payroll entry model."""
    employee_id: str = Field(..., description="Employee ID")
    pay_period_start: date = Field(..., description="Pay period start date")
    pay_period_end: date = Field(..., description="Pay period end date")
    pay_date: Optional[date] = Field(None, description="Pay date")
    basic_salary: Decimal = Field(..., ge=0, description="Basic salary amount")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, description="Hourly rate")
    hours_worked: Optional[float] = Field(None, ge=0, description="Hours worked")
    overtime_hours: float = Field(default=0, ge=0, description="Overtime hours")
    overtime_rate_multiplier: float = Field(default=1.5, ge=1, description="Overtime rate multiplier")
    
    # Allowances
    housing_allowance: Decimal = Field(default=0, ge=0, description="Housing allowance")
    transport_allowance: Decimal = Field(default=0, ge=0, description="Transport allowance")
    meal_allowance: Decimal = Field(default=0, ge=0, description="Meal allowance")
    medical_allowance: Decimal = Field(default=0, ge=0, description="Medical allowance")
    communication_allowance: Decimal = Field(default=0, ge=0, description="Communication allowance")
    other_allowances: Decimal = Field(default=0, ge=0, description="Other allowances")
    
    # Bonuses
    performance_bonus: Decimal = Field(default=0, ge=0, description="Performance bonus")
    sales_commission: Decimal = Field(default=0, ge=0, description="Sales commission")
    attendance_bonus: Decimal = Field(default=0, ge=0, description="Attendance bonus")
    holiday_bonus: Decimal = Field(default=0, ge=0, description="Holiday bonus")
    other_bonuses: Decimal = Field(default=0, ge=0, description="Other bonuses")
    
    # Deductions
    income_tax: Decimal = Field(default=0, ge=0, description="Income tax")
    social_security: Decimal = Field(default=0, ge=0, description="Social security")
    pension_contribution: Decimal = Field(default=0, ge=0, description="Pension contribution")
    health_insurance: Decimal = Field(default=0, ge=0, description="Health insurance")
    life_insurance: Decimal = Field(default=0, ge=0, description="Life insurance")
    loan_deduction: Decimal = Field(default=0, ge=0, description="Loan deduction")
    advance_deduction: Decimal = Field(default=0, ge=0, description="Advance deduction")
    other_deductions: Decimal = Field(default=0, ge=0, description="Other deductions")
    
    # Payment details
    payment_method: str = Field(default="bank-transfer", description="Payment method")
    payment_notes: Optional[str] = Field(None, description="Payment notes")


class PayrollEntryCreate(PayrollEntryBase):
    """Payroll entry creation model."""
    pass


class PayrollEntryUpdate(BaseModel):
    """Payroll entry update model."""
    status: Optional[str] = Field(None, description="Payroll status")
    pay_date: Optional[date] = Field(None, description="Pay date")
    basic_salary: Optional[Decimal] = Field(None, ge=0, description="Basic salary amount")
    overtime_hours: Optional[float] = Field(None, ge=0, description="Overtime hours")
    housing_allowance: Optional[Decimal] = Field(None, ge=0, description="Housing allowance")
    transport_allowance: Optional[Decimal] = Field(None, ge=0, description="Transport allowance")
    meal_allowance: Optional[Decimal] = Field(None, ge=0, description="Meal allowance")
    performance_bonus: Optional[Decimal] = Field(None, ge=0, description="Performance bonus")
    income_tax: Optional[Decimal] = Field(None, ge=0, description="Income tax")
    social_security: Optional[Decimal] = Field(None, ge=0, description="Social security")
    pension_contribution: Optional[Decimal] = Field(None, ge=0, description="Pension contribution")
    health_insurance: Optional[Decimal] = Field(None, ge=0, description="Health insurance")
    payment_method: Optional[str] = Field(None, description="Payment method")
    payment_notes: Optional[str] = Field(None, description="Payment notes")


class PayrollEntryResponse(PayrollEntryBase):
    """Payroll entry response model."""
    id: str
    status: str
    employee_name: Optional[str]
    employee_position: Optional[str]
    employee_department: Optional[str]
    overtime_amount: Decimal
    total_allowances: Decimal
    total_bonuses: Decimal
    total_deductions: Decimal
    gross_pay: Decimal
    taxable_income: Decimal
    net_pay: Decimal
    ytd_gross_pay: Decimal
    ytd_tax_paid: Decimal
    ytd_net_pay: Decimal
    pay_period_days: int
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PayrollSummary(BaseModel):
    """Payroll summary model."""
    total_employees: int
    total_gross_pay: Decimal
    total_deductions: Decimal
    total_net_pay: Decimal
    average_salary: Decimal
    payroll_by_department: List[Dict[str, Any]]
    recent_payments: List[Dict[str, Any]]


class PayrollRunBase(BaseModel):
    """Base payroll run model."""
    run_name: str = Field(..., max_length=100, description="Payroll run name")
    description: Optional[str] = Field(None, description="Payroll run description")
    pay_period_start: date = Field(..., description="Pay period start date")
    pay_period_end: date = Field(..., description="Pay period end date")
    pay_date: date = Field(..., description="Pay date")
    frequency: str = Field(..., description="Payroll frequency")
    department_ids: Optional[List[str]] = Field(default_factory=list, description="Department IDs to include")
    employee_ids: Optional[List[str]] = Field(default_factory=list, description="Employee IDs to include")
    include_terminated: bool = Field(default=False, description="Include terminated employees")


class PayrollRunCreate(PayrollRunBase):
    """Payroll run creation model."""
    pass


class PayrollRunResponse(PayrollRunBase):
    """Payroll run response model."""
    id: str
    status: str
    total_employees: int
    total_gross_pay: Decimal
    total_deductions: Decimal
    total_net_pay: Decimal
    total_taxes: Decimal
    pay_period_days: int
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# API Endpoints
@router.get("/summary", response_model=PayrollSummary)
async def get_payroll_summary(
    session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get payroll summary and metrics."""
    
    # Get payroll entries for current month
    current_date = date.today()
    start_of_month = current_date.replace(day=1)
    
    query = select(PayrollEntry).options(
        selectinload(PayrollEntry.employee).selectinload(Employee.user),
        selectinload(PayrollEntry.employee).selectinload(Employee.department)
    ).where(
        and_(
            PayrollEntry.tenant_id == current_user.tenant_id,
            PayrollEntry.pay_period_start >= start_of_month
        )
    )
    
    payroll_entries = (await session.execute(query)).scalars().all()
    
    # Calculate summary metrics
    total_employees = len(set(entry.employee_id for entry in payroll_entries))
    total_gross_pay = sum(entry.gross_pay for entry in payroll_entries)
    total_deductions = sum(entry.total_deductions for entry in payroll_entries)
    total_net_pay = sum(entry.net_pay for entry in payroll_entries)
    average_salary = total_gross_pay / total_employees if total_employees > 0 else 0
    
    # Group by department
    dept_summary = {}
    for entry in payroll_entries:
        dept_name = entry.employee.department.name if entry.employee and entry.employee.department else "Unknown"
        if dept_name not in dept_summary:
            dept_summary[dept_name] = {
                "department": dept_name,
                "employees": set(),
                "total_pay": Decimal(0),
                "avg_pay": Decimal(0)
            }
        dept_summary[dept_name]["employees"].add(entry.employee_id)
        dept_summary[dept_name]["total_pay"] += entry.gross_pay
    
    # Calculate averages and convert to list
    payroll_by_department = []
    for dept_data in dept_summary.values():
        employee_count = len(dept_data["employees"])
        avg_pay = dept_data["total_pay"] / employee_count if employee_count > 0 else Decimal(0)
        payroll_by_department.append({
            "department": dept_data["department"],
            "employees": employee_count,
            "total_pay": float(dept_data["total_pay"]),
            "avg_pay": float(avg_pay)
        })
    
    # Recent payments (last 10)
    recent_payments = []
    recent_entries = sorted(
        [e for e in payroll_entries if e.status == PayrollStatus.PAID],
        key=lambda x: x.pay_date or x.created_at,
        reverse=True
    )[:10]
    
    for entry in recent_entries:
        recent_payments.append({
            "employee_name": entry.employee.user.full_name if entry.employee and entry.employee.user else "Unknown",
            "amount": float(entry.net_pay),
            "pay_date": entry.pay_date.isoformat() if entry.pay_date else None,
            "payment_method": entry.payment_method
        })
    
    return PayrollSummary(
        total_employees=total_employees,
        total_gross_pay=total_gross_pay,
        total_deductions=total_deductions,
        total_net_pay=total_net_pay,
        average_salary=average_salary,
        payroll_by_department=payroll_by_department,
        recent_payments=recent_payments
    )


@router.get("/entries", response_model=List[PayrollEntryResponse])
async def get_payroll_entries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by payroll status"),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    pay_period_start: Optional[date] = Query(None, description="Filter by pay period start"),
    pay_period_end: Optional[date] = Query(None, description="Filter by pay period end"),
    session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get payroll entries with optional filtering."""
    
    query = select(PayrollEntry).options(
        selectinload(PayrollEntry.employee).selectinload(Employee.user),
        selectinload(PayrollEntry.employee).selectinload(Employee.department)
    ).where(
        PayrollEntry.tenant_id == current_user.tenant_id
    )
    
    # Apply filters
    if status:
        query = query.where(PayrollEntry.status == status)
    if employee_id:
        query = query.where(PayrollEntry.employee_id == employee_id)
    if pay_period_start:
        query = query.where(PayrollEntry.pay_period_start >= pay_period_start)
    if pay_period_end:
        query = query.where(PayrollEntry.pay_period_end <= pay_period_end)
    if department:
        query = query.join(Employee).join(Employee.department).where(
            func.lower(Employee.department.name) == department.lower()
        )
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(desc(PayrollEntry.pay_period_start))
    
    payroll_entries = (await session.execute(query)).scalars().all()
    
    # Enhance response with additional data
    response_entries = []
    for entry in payroll_entries:
        entry_dict = {
            **entry.__dict__,
            "employee_name": entry.employee.user.full_name if entry.employee and entry.employee.user else "Unknown",
            "employee_position": entry.employee.job_title if entry.employee else "Unknown",
            "employee_department": entry.employee.department.name if entry.employee and entry.employee.department else "Unknown",
            "pay_period_days": entry.pay_period_days,
            "is_processed": entry.is_processed
        }
        response_entries.append(PayrollEntryResponse(**entry_dict))
    
    return response_entries


@router.post("/entries", response_model=PayrollEntryResponse)
async def create_payroll_entry(
    payroll_entry: PayrollEntryCreate,
    session = Depends(get_session),
    current_user: User = Depends(require_permission("payroll:write"))
):
    """Create a new payroll entry."""
    
    # Verify employee exists
    employee_query = select(Employee).options(
        selectinload(Employee.user),
        selectinload(Employee.department)
    ).where(
        and_(Employee.id == payroll_entry.employee_id, Employee.tenant_id == current_user.tenant_id)
    )
    employee = (await session.execute(employee_query)).scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Create payroll entry
    db_entry = PayrollEntry(
        **payroll_entry.model_dump(),
        tenant_id=current_user.tenant_id
    )
    
    # Calculate overtime amount
    if db_entry.hourly_rate and db_entry.overtime_hours > 0:
        db_entry.overtime_amount = db_entry.hourly_rate * db_entry.overtime_hours * db_entry.overtime_rate_multiplier
    
    # Calculate totals
    db_entry.calculate_totals()
    
    session.add(db_entry)
    await session.commit()
    await session.refresh(db_entry)
    
    # Prepare response
    entry_dict = {
        **db_entry.__dict__,
        "employee_name": employee.user.full_name if employee.user else "Unknown",
        "employee_position": employee.job_title,
        "employee_department": employee.department.name if employee.department else "Unknown",
        "pay_period_days": db_entry.pay_period_days,
        "is_processed": db_entry.is_processed
    }
    
    return PayrollEntryResponse(**entry_dict)


@router.get("/entries/{entry_id}", response_model=PayrollEntryResponse)
async def get_payroll_entry(
    entry_id: str,
    session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific payroll entry by ID."""
    
    query = select(PayrollEntry).options(
        selectinload(PayrollEntry.employee).selectinload(Employee.user),
        selectinload(PayrollEntry.employee).selectinload(Employee.department)
    ).where(
        and_(
            PayrollEntry.id == entry_id,
            PayrollEntry.tenant_id == current_user.tenant_id
        )
    )
    
    entry = (await session.execute(query)).scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll entry not found"
        )
    
    # Prepare response
    entry_dict = {
        **entry.__dict__,
        "employee_name": entry.employee.user.full_name if entry.employee and entry.employee.user else "Unknown",
        "employee_position": entry.employee.job_title if entry.employee else "Unknown",
        "employee_department": entry.employee.department.name if entry.employee and entry.employee.department else "Unknown",
        "pay_period_days": entry.pay_period_days,
        "is_processed": entry.is_processed
    }
    
    return PayrollEntryResponse(**entry_dict)


@router.put("/entries/{entry_id}", response_model=PayrollEntryResponse)
async def update_payroll_entry(
    entry_id: str,
    entry_update: PayrollEntryUpdate,
    session = Depends(get_session),
    current_user: User = Depends(require_permission("payroll:write"))
):
    """Update a payroll entry."""
    
    # Get existing entry
    query = select(PayrollEntry).options(
        selectinload(PayrollEntry.employee).selectinload(Employee.user),
        selectinload(PayrollEntry.employee).selectinload(Employee.department)
    ).where(
        and_(
            PayrollEntry.id == entry_id,
            PayrollEntry.tenant_id == current_user.tenant_id
        )
    )
    
    entry = (await session.execute(query)).scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll entry not found"
        )
    
    # Update entry fields
    update_data = entry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(entry, field):
            setattr(entry, field, value)
    
    # Recalculate overtime if relevant fields changed
    if any(field in update_data for field in ['overtime_hours', 'hourly_rate', 'overtime_rate_multiplier']):
        if entry.hourly_rate and entry.overtime_hours > 0:
            entry.overtime_amount = entry.hourly_rate * entry.overtime_hours * entry.overtime_rate_multiplier
    
    # Recalculate totals
    entry.calculate_totals()
    
    await session.commit()
    await session.refresh(entry)
    
    # Prepare response
    entry_dict = {
        **entry.__dict__,
        "employee_name": entry.employee.user.full_name if entry.employee and entry.employee.user else "Unknown",
        "employee_position": entry.employee.job_title if entry.employee else "Unknown",
        "employee_department": entry.employee.department.name if entry.employee and entry.employee.department else "Unknown",
        "pay_period_days": entry.pay_period_days,
        "is_processed": entry.is_processed
    }
    
    return PayrollEntryResponse(**entry_dict)


@router.post("/entries/{entry_id}/approve", response_model=PayrollEntryResponse)
async def approve_payroll_entry(
    entry_id: str,
    session = Depends(get_session),
    current_user: User = Depends(require_permission("payroll:approve"))
):
    """Approve a payroll entry for payment."""
    
    # Get existing entry
    query = select(PayrollEntry).options(
        selectinload(PayrollEntry.employee).selectinload(Employee.user),
        selectinload(PayrollEntry.employee).selectinload(Employee.department)
    ).where(
        and_(
            PayrollEntry.id == entry_id,
            PayrollEntry.tenant_id == current_user.tenant_id
        )
    )
    
    entry = (await session.execute(query)).scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll entry not found"
        )
    
    if entry.status != PayrollStatus.CALCULATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only calculated payroll entries can be approved"
        )
    
    # Update status and approval info
    entry.status = PayrollStatus.APPROVED
    entry.approved_by = current_user.id
    entry.approved_date = date.today()
    
    await session.commit()
    await session.refresh(entry)
    
    # Prepare response
    entry_dict = {
        **entry.__dict__,
        "employee_name": entry.employee.user.full_name if entry.employee and entry.employee.user else "Unknown",
        "employee_position": entry.employee.job_title if entry.employee else "Unknown",
        "employee_department": entry.employee.department.name if entry.employee and entry.employee.department else "Unknown",
        "pay_period_days": entry.pay_period_days,
        "is_processed": entry.is_processed
    }
    
    return PayrollEntryResponse(**entry_dict)


@router.post("/entries/{entry_id}/pay", response_model=PayrollEntryResponse)
async def mark_payroll_as_paid(
    entry_id: str,
    payment_reference: Optional[str] = None,
    session = Depends(get_session),
    current_user: User = Depends(require_permission("payroll:approve"))
):
    """Mark a payroll entry as paid."""
    
    # Get existing entry
    query = select(PayrollEntry).options(
        selectinload(PayrollEntry.employee).selectinload(Employee.user),
        selectinload(PayrollEntry.employee).selectinload(Employee.department)
    ).where(
        and_(
            PayrollEntry.id == entry_id,
            PayrollEntry.tenant_id == current_user.tenant_id
        )
    )
    
    entry = (await session.execute(query)).scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll entry not found"
        )
    
    if entry.status != PayrollStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved payroll entries can be marked as paid"
        )
    
    # Update status and payment info
    entry.status = PayrollStatus.PAID
    if payment_reference:
        entry.payment_reference = payment_reference
    if not entry.pay_date:
        entry.pay_date = date.today()
    
    await session.commit()
    await session.refresh(entry)
    
    # Prepare response
    entry_dict = {
        **entry.__dict__,
        "employee_name": entry.employee.user.full_name if entry.employee and entry.employee.user else "Unknown",
        "employee_position": entry.employee.job_title if entry.employee else "Unknown",
        "employee_department": entry.employee.department.name if entry.employee and entry.employee.department else "Unknown",
        "pay_period_days": entry.pay_period_days,
        "is_processed": entry.is_processed
    }
    
    return PayrollEntryResponse(**entry_dict)

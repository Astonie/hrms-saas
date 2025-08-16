"""
Employees API endpoints for HRMS-SAAS.
Handles employee CRUD operations, search, filtering, and management.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import date

from ...core.security import get_current_user, require_permission
from ...core.database import get_session
from ...models.employee import Employee, Department
from ...models.user import User

router = APIRouter()


# Request/Response Models
class EmployeeBase(BaseModel):
    """Base employee model."""
    employee_id: str = Field(..., description="Unique employee identifier")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., description="Employee email address")
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = Field(None, description="Employee date of birth")
    gender: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=100)


class EmployeeCreate(EmployeeBase):
    """Employee creation model."""
    user_id: Optional[str] = Field(None, description="Associated user account ID")
    department_id: Optional[str] = Field(None, description="Department ID")
    job_title: str = Field(..., max_length=200)
    employment_status: str = Field(..., description="Employment status")
    employment_type: str = Field(..., description="Employment type")
    hire_date: date = Field(..., description="Date of hire")
    salary: Optional[float] = Field(None, ge=0, description="Annual salary")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly rate")
    manager_id: Optional[str] = Field(None, description="Manager's employee ID")
    skills: Optional[List[str]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)


class EmployeeUpdate(BaseModel):
    """Employee update model."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, description="Employee email address")
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    department_id: Optional[str] = Field(None, description="Department ID")
    job_title: Optional[str] = Field(None, max_length=200)
    employment_status: Optional[str] = Field(None, description="Employment status")
    salary: Optional[float] = Field(None, ge=0, description="Annual salary")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly rate")
    manager_id: Optional[str] = Field(None, description="Manager's employee ID")
    skills: Optional[List[str]] = Field(None)
    certifications: Optional[List[str]] = Field(None)


class EmployeeResponse(EmployeeBase):
    """Employee response model."""
    id: str
    user_id: Optional[str]
    department_id: Optional[str]
    department_name: Optional[str]
    job_title: str
    employment_status: str
    employment_type: str
    hire_date: date
    termination_date: Optional[date]
    salary: Optional[float]
    hourly_rate: Optional[float]
    manager_id: Optional[str]
    manager_name: Optional[str]
    skills: List[str]
    certifications: List[str]
    is_active: bool
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Employee list response model."""
    employees: List[EmployeeResponse]
    total: int
    page: int
    size: int
    pages: int


class EmployeeSearchParams(BaseModel):
    """Employee search parameters."""
    query: Optional[str] = Field(None, description="Search query for name, email, or employee ID")
    department_id: Optional[str] = Field(None, description="Filter by department")
    employment_status: Optional[str] = Field(None, description="Filter by employment status")
    job_title: Optional[str] = Field(None, description="Filter by job title")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("employees:create"))
):
    """Create a new employee."""
    try:
        # Check if employee ID already exists
        existing_employee = await db_session.execute(
            select(Employee).where(Employee.employee_id == employee_data.employee_id)
        )
        if existing_employee.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists"
            )

        # Check if email already exists
        if employee_data.email:
            existing_email = await db_session.execute(
                select(Employee).where(Employee.email == employee_data.email)
            )
            if existing_email.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )

        # Create employee
        employee = Employee(
            **employee_data.dict(),
            tenant_id=current_user["tenant_id"]
        )
        
        db_session.add(employee)
        await db_session.commit()
        await db_session.refresh(employee)
        
        return await _enrich_employee_response(employee, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create employee"
        )


@router.get("/", response_model=EmployeeListResponse)
async def list_employees(
    search_params: EmployeeSearchParams = Depends(),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("employees:read"))
):
    """List employees with search and filtering."""
    try:
        # Build query
        query = select(Employee).where(Employee.tenant_id == current_user["tenant_id"])
        
        # Apply filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.where(
                or_(
                    Employee.first_name.ilike(search_term),
                    Employee.last_name.ilike(search_term),
                    Employee.email.ilike(search_term),
                    Employee.employee_id.ilike(search_term)
                )
            )
        
        if search_params.department_id:
            query = query.where(Employee.department_id == search_params.department_id)
        
        if search_params.employment_status:
            query = query.where(Employee.employment_status == search_params.employment_status)
        
        if search_params.job_title:
            query = query.where(Employee.job_title.ilike(f"%{search_params.job_title}%"))
        
        if search_params.is_active is not None:
            query = query.where(Employee.is_active == search_params.is_active)
        
        # Get total count
        count_query = select(Employee.id).where(Employee.tenant_id == current_user["tenant_id"])
        total = await db_session.scalar(select(func.count()).select_from(count_query.subquery()))
        
        # Apply pagination
        query = query.offset((search_params.page - 1) * search_params.size).limit(search_params.size)
        
        # Execute query
        result = await db_session.execute(query)
        employees = result.scalars().all()
        
        # Enrich responses
        enriched_employees = []
        for employee in employees:
            enriched_employees.append(await _enrich_employee_response(employee, db_session))
        
        return EmployeeListResponse(
            employees=enriched_employees,
            total=total,
            page=search_params.page,
            size=search_params.size,
            pages=(total + search_params.size - 1) // search_params.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list employees"
        )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("employees:read"))
):
    """Get employee by ID."""
    try:
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
        
        return await _enrich_employee_response(employee, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get employee"
        )


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("employees:update"))
):
    """Update employee."""
    try:
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
        
        # Update fields
        update_data = employee_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        await db_session.commit()
        await db_session.refresh(employee)
        
        return await _enrich_employee_response(employee, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update employee"
        )


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("employees:delete"))
):
    """Delete employee (soft delete)."""
    try:
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
        
        # Soft delete
        employee.soft_delete()
        await db_session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employee"
        )


@router.post("/{employee_id}/restore", response_model=EmployeeResponse)
async def restore_employee(
    employee_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("employees:update"))
):
    """Restore soft-deleted employee."""
    try:
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
        
        if employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee is already active"
            )
        
        # Restore employee
        employee.restore()
        await db_session.commit()
        await db_session.refresh(employee)
        
        return await _enrich_employee_response(employee, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore employee"
        )


# Helper function to enrich employee response with related data
async def _enrich_employee_response(employee: Employee, db_session) -> EmployeeResponse:
    """Enrich employee response with department and manager information."""
    department_name = None
    manager_name = None
    
    if employee.department_id:
        dept_result = await db_session.execute(
            select(Department.name).where(Department.id == employee.department_id)
        )
        department_name = dept_result.scalar_one_or_none()
    
    if employee.manager_id:
        manager_result = await db_session.execute(
            select(Employee.first_name, Employee.last_name).where(Employee.id == employee.manager_id)
        )
        manager = manager_result.first()
        if manager:
            manager_name = f"{manager.first_name} {manager.last_name}"
    
    return EmployeeResponse(
        id=employee.id,
        employee_id=employee.employee_id,
        user_id=employee.user_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        date_of_birth=employee.date_of_birth,
        gender=employee.gender,
        address=employee.address,
        city=employee.city,
        state=employee.state,
        postal_code=employee.postal_code,
        country=employee.country,
        emergency_contact_name=employee.emergency_contact_name,
        emergency_contact_phone=employee.emergency_contact_phone,
        emergency_contact_relationship=employee.emergency_contact_relationship,
        department_id=employee.department_id,
        department_name=department_name,
        job_title=employee.job_title,
        employment_status=employee.employment_status,
        employment_type=employee.employment_type,
        hire_date=employee.hire_date,
        termination_date=employee.termination_date,
        salary=employee.salary,
        hourly_rate=employee.hourly_rate,
        manager_id=employee.manager_id,
        manager_name=manager_name,
        skills=employee.skills or [],
        certifications=employee.certifications or [],
        is_active=employee.is_active,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )

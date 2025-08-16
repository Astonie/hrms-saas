"""
Departments API endpoints for HRMS-SAAS.
Handles department CRUD operations, hierarchical structure, and management.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import date

from ...core.security import get_current_user, require_permission
from ...core.database import get_session
from ...models.employee import Department, Employee

router = APIRouter()


# Request/Response Models
class DepartmentBase(BaseModel):
    """Base department model."""
    name: str = Field(..., min_length=1, max_length=255, description="Department name")
    description: Optional[str] = Field(None, max_length=1000, description="Department description")
    code: Optional[str] = Field(None, max_length=50, description="Department code")
    location: Optional[str] = Field(None, max_length=255, description="Department location")
    budget: Optional[float] = Field(None, ge=0, description="Department budget")
    parent_department_id: Optional[str] = Field(None, description="Parent department ID for hierarchy")


class DepartmentCreate(DepartmentBase):
    """Department creation model."""
    department_head_id: Optional[str] = Field(None, description="Department head employee ID")


class DepartmentUpdate(BaseModel):
    """Department update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    code: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    budget: Optional[float] = Field(None, ge=0)
    parent_department_id: Optional[str] = Field(None)
    department_head_id: Optional[str] = Field(None)


class DepartmentResponse(DepartmentBase):
    """Department response model."""
    id: str
    department_head_id: Optional[str]
    department_head_name: Optional[str]
    parent_department_id: Optional[str]
    parent_department_name: Optional[str]
    employee_count: int
    sub_departments: List["DepartmentResponse"] = []
    is_active: bool
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class DepartmentListResponse(BaseModel):
    """Department list response model."""
    departments: List[DepartmentResponse]
    total: int
    page: int
    size: int
    pages: int


class DepartmentTreeResponse(BaseModel):
    """Department tree response model."""
    departments: List[DepartmentResponse]


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("departments:create"))
):
    """Create a new department."""
    try:
        # Check if department name already exists in the tenant
        existing_dept = await db_session.execute(
            select(Department).where(
                and_(
                    Department.name == department_data.name,
                    Department.tenant_id == current_user["tenant_id"]
                )
            )
        )
        if existing_dept.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department name already exists"
            )

        # Check if parent department exists and belongs to the same tenant
        if department_data.parent_department_id:
            parent_dept = await db_session.execute(
                select(Department).where(
                    and_(
                        Department.id == department_data.parent_department_id,
                        Department.tenant_id == current_user["tenant_id"]
                    )
                )
            )
            if not parent_dept.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department not found"
                )

        # Check if department head exists and belongs to the same tenant
        if department_data.department_head_id:
            head_employee = await db_session.execute(
                select(Employee).where(
                    and_(
                        Employee.id == department_data.department_head_id,
                        Employee.tenant_id == current_user["tenant_id"]
                    )
                )
            )
            if not head_employee.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department head not found"
                )

        # Create department
        department = Department(
            **department_data.dict(),
            tenant_id=current_user["tenant_id"]
        )
        
        db_session.add(department)
        await db_session.commit()
        await db_session.refresh(department)
        
        return await _enrich_department_response(department, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create department"
        )


@router.get("/", response_model=DepartmentListResponse)
async def list_departments(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    include_inactive: bool = Query(False, description="Include inactive departments"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("departments:read"))
):
    """List departments with pagination."""
    try:
        # Build query
        query = select(Department).where(Department.tenant_id == current_user["tenant_id"])
        
        if not include_inactive:
            query = query.where(Department.is_active == True)
        
        # Get total count
        count_query = select(Department.id).where(Department.tenant_id == current_user["tenant_id"])
        if not include_inactive:
            count_query = count_query.where(Department.is_active == True)
        total = await db_session.scalar(select(func.count()).select_from(count_query.subquery()))
        
        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db_session.execute(query)
        departments = result.scalars().all()
        
        # Enrich responses
        enriched_departments = []
        for department in departments:
            enriched_departments.append(await _enrich_department_response(department, db_session))
        
        return DepartmentListResponse(
            departments=enriched_departments,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list departments"
        )


@router.get("/tree", response_model=DepartmentTreeResponse)
async def get_department_tree(
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("departments:read"))
):
    """Get department hierarchy tree."""
    try:
        # Get all active departments
        result = await db_session.execute(
            select(Department).where(
                and_(
                    Department.tenant_id == current_user["tenant_id"],
                    Department.is_active == True
                )
            )
        )
        departments = result.scalars().all()
        
        # Build hierarchy
        dept_dict = {dept.id: await _enrich_department_response(dept, db_session) for dept in departments}
        root_departments = []
        
        for dept in departments:
            if dept.parent_department_id is None:
                root_departments.append(dept_dict[dept.id])
            else:
                parent = dept_dict.get(dept.parent_department_id)
                if parent:
                    parent.sub_departments.append(dept_dict[dept.id])
        
        return DepartmentTreeResponse(departments=root_departments)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get department tree"
        )


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("departments:read"))
):
    """Get department by ID."""
    try:
        department = await db_session.execute(
            select(Department).where(
                and_(
                    Department.id == department_id,
                    Department.tenant_id == current_user["tenant_id"]
                )
            )
        )
        department = department.scalar_one_or_none()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        return await _enrich_department_response(department, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get department"
        )


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("departments:update"))
):
    """Update department."""
    try:
        department = await db_session.execute(
            select(Department).where(
                and_(
                    Department.id == department_id,
                    Department.tenant_id == current_user["tenant_id"]
                )
            )
        )
        department = department.scalar_one_or_none()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if new name conflicts with existing departments
        if department_data.name and department_data.name != department.name:
            existing_dept = await db_session.execute(
                select(Department).where(
                    and_(
                        Department.name == department_data.name,
                        Department.tenant_id == current_user["tenant_id"],
                        Department.id != department_id
                    )
                )
            )
            if existing_dept.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department name already exists"
                )
        
        # Check if parent department exists and doesn't create circular reference
        if department_data.parent_department_id:
            if department_data.parent_department_id == department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department cannot be its own parent"
                )
            
            # Check if parent department exists
            parent_dept = await db_session.execute(
                select(Department).where(
                    and_(
                        Department.id == department_data.parent_department_id,
                        Department.tenant_id == current_user["tenant_id"]
                    )
                )
            )
            if not parent_dept.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department not found"
                )
        
        # Update fields
        update_data = department_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(department, field, value)
        
        await db_session.commit()
        await db_session.refresh(department)
        
        return await _enrich_department_response(department, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update department"
        )


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("departments:delete"))
):
    """Delete department (soft delete)."""
    try:
        department = await db_session.execute(
            select(Department).where(
                and_(
                    Department.id == department_id,
                    Department.tenant_id == current_user["tenant_id"]
                )
            )
        )
        department = department.scalar_one_or_none()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        # Check if department has employees
        employee_count = await db_session.scalar(
            select(func.count(Employee.id)).where(
                and_(
                    Employee.department_id == department_id,
                    Employee.tenant_id == current_user["tenant_id"],
                    Employee.is_active == True
                )
            )
        )
        
        if employee_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete department with {employee_count} active employees"
            )
        
        # Check if department has sub-departments
        sub_dept_count = await db_session.scalar(
            select(func.count(Department.id)).where(
                and_(
                    Department.parent_department_id == department_id,
                    Department.tenant_id == current_user["tenant_id"],
                    Department.is_active == True
                )
            )
        )
        
        if sub_dept_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete department with {sub_dept_count} sub-departments"
            )
        
        # Soft delete
        department.soft_delete()
        await db_session.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete department"
        )


@router.post("/{department_id}/restore", response_model=DepartmentResponse)
async def restore_department(
    department_id: str,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session),
    _: list = Depends(require_permission("departments:update"))
):
    """Restore soft-deleted department."""
    try:
        department = await db_session.execute(
            select(Department).where(
                and_(
                    Department.id == department_id,
                    Department.tenant_id == current_user["tenant_id"]
                )
            )
        )
        department = department.scalar_one_or_none()
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        if department.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department is already active"
            )
        
        # Restore department
        department.restore()
        await db_session.commit()
        await db_session.refresh(department)
        
        return await _enrich_department_response(department, db_session)
        
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore department"
        )


# Helper function to enrich department response with related data
async def _enrich_department_response(department: Department, db_session) -> DepartmentResponse:
    """Enrich department response with related information."""
    department_head_name = None
    parent_department_name = None
    employee_count = 0
    
    # Get department head name
    if department.department_head_id:
        head_result = await db_session.execute(
            select(Employee.first_name, Employee.last_name).where(Employee.id == department.department_head_id)
        )
        head = head_result.first()
        if head:
            department_head_name = f"{head.first_name} {head.last_name}"
    
    # Get parent department name
    if department.parent_department_id:
        parent_result = await db_session.execute(
            select(Department.name).where(Department.id == department.parent_department_id)
        )
        parent_department_name = parent_result.scalar_one_or_none()
    
    # Get employee count
    employee_count = await db_session.scalar(
        select(func.count(Employee.id)).where(
            and_(
                Employee.department_id == department.id,
                Employee.is_active == True
            )
        )
    )
    
    return DepartmentResponse(
        id=department.id,
        name=department.name,
        description=department.description,
        code=department.code,
        location=department.location,
        budget=department.budget,
        parent_department_id=department.parent_department_id,
        parent_department_name=parent_department_name,
        department_head_id=department.department_head_id,
        department_head_name=department_head_name,
        employee_count=employee_count,
        sub_departments=[],
        is_active=department.is_active,
        created_at=department.created_at,
        updated_at=department.updated_at
    )

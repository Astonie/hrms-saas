"""
Employee model for HRMS-SAAS system.
Represents detailed employee information and HR data.
"""

from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Enum, ForeignKey, Date, Numeric, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .base import BaseUUIDModel

if TYPE_CHECKING:
    from .user import User
    from .leave import LeaveRequest, LeaveBalance
    from .performance import PerformanceReview, PerformanceGoal
    from .payroll import PayrollEntry


class EmploymentStatus(str, enum.Enum):
    """Employment status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    RETIRED = "retired"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"
    CONTRACT = "contract"
    INTERN = "intern"


class EmploymentType(str, enum.Enum):
    """Employment type enumeration."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    SEASONAL = "seasonal"


class MaritalStatus(str, enum.Enum):
    """Marital status enumeration."""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"
    CIVIL_PARTNERSHIP = "civil_partnership"


class BloodType(str, enum.Enum):
    """Blood type enumeration."""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class Employee(BaseUUIDModel):
    """
    Employee model representing detailed HR information for employees.
    
    This model extends the basic user information with comprehensive
    HR-specific data and relationships.
    """
    
    __tablename__ = "employees"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    # Reference to User
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id"), 
        nullable=False, 
        unique=True
    )
    
    # Employee Identification
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    badge_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    ssn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    
    # Employment Information
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        Enum(EmploymentStatus), 
        default=EmploymentStatus.ACTIVE, 
        nullable=False
    )
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType), 
        default=EmploymentType.FULL_TIME, 
        nullable=False
    )
    
    # Dates
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    probation_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contract_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contract_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    termination_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    retirement_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Position and Department
    job_title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    department_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("departments.id"), nullable=True)
    supervisor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    manager_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    
    # Work Schedule
    work_schedule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    standard_hours_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    overtime_eligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Compensation
    base_salary: Mapped[Optional[Numeric]] = mapped_column(Numeric(10, 2), nullable=True)
    # Tests expect a `salary` attribute
    @property
    def salary(self) -> Optional[float]:
        return float(self.base_salary) if self.base_salary is not None else None
    
    @salary.setter
    def salary(self, value):
        try:
            self.base_salary = value
        except Exception:
            self.base_salary = None
    hourly_rate: Mapped[Optional[Numeric]] = mapped_column(Numeric(8, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    pay_frequency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Personal Information
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    marital_status: Mapped[Optional[MaritalStatus]] = mapped_column(Enum(MaritalStatus), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    blood_type: Mapped[Optional[BloodType]] = mapped_column(Enum(BloodType), nullable=True)
    
    # Emergency Contact Information
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    emergency_contact_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Address Information
    residential_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mailing_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Bank and Tax Information
    bank_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_routing_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Benefits and Insurance
    benefits_enrolled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    benefits_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    health_insurance_provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    health_insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Skills and Certifications
    skills: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    certifications: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Performance and Development
    performance_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    career_goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    training_needs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Custom Fields
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", backref="employee")
    department: Mapped[Optional["Department"]] = relationship(
        "Department",
        back_populates="employees",
        foreign_keys=[department_id]
    )
    supervisor: Mapped[Optional["Employee"]] = relationship(
        "Employee", 
        remote_side="Employee.id",
        foreign_keys=[supervisor_id],
        backref="subordinates"
    )
    manager: Mapped[Optional["Employee"]] = relationship(
        "Employee", 
        remote_side="Employee.id",
        foreign_keys=[manager_id],
        backref="team_members"
    )
    
    # Leave Management Relationships
    leave_requests: Mapped[List["LeaveRequest"]] = relationship("LeaveRequest", back_populates="employee", foreign_keys="LeaveRequest.employee_id")
    leave_balances: Mapped[List["LeaveBalance"]] = relationship("LeaveBalance", back_populates="employee")
    
    # Performance Management Relationships
    performance_reviews: Mapped[List["PerformanceReview"]] = relationship("PerformanceReview", foreign_keys="PerformanceReview.employee_id", back_populates="employee")
    goals: Mapped[List["PerformanceGoal"]] = relationship("PerformanceGoal", foreign_keys="PerformanceGoal.employee_id", back_populates="employee")
    
    # Payroll Relationships
    payroll_entries: Mapped[List["PayrollEntry"]] = relationship("PayrollEntry", foreign_keys="PayrollEntry.employee_id", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, employee_id='{self.employee_id}', name='{self.user.full_name if self.user else 'Unknown'}')>"
    
    @property
    def full_name(self) -> str:
        """Get employee's full name from user."""
        return self.user.full_name if self.user else "Unknown"
    
    @property
    def email(self) -> str:
        """Get employee's email from user."""
        return self.user.email if self.user else ""
    
    @property
    def is_active_employee(self) -> bool:
        """Check if employee is currently active."""
        return self.employment_status == EmploymentStatus.ACTIVE

    @property
    def employment_length_days(self) -> Optional[int]:
        """Calculate employment length in days between hire and termination."""
        if not self.hire_date or not self.termination_date:
            return None
        delta = self.termination_date - self.hire_date
        return delta.days
    
    @property
    def is_on_probation(self) -> bool:
        """Check if employee is on probation."""
        if not self.probation_end_date:
            return False
        return date.today() <= self.probation_end_date
    
    @property
    def is_contract_employee(self) -> bool:
        """Check if employee is a contract worker."""
        return self.employment_type == EmploymentType.CONTRACT
    
    @property
    def years_of_service(self) -> int:
        """Calculate years of service."""
        if not self.hire_date:
            return 0
        today = date.today()
        return today.year - self.hire_date.year - ((today.month, today.day) < (self.hire_date.month, self.hire_date.day))
    
    @property
    def is_eligible_for_benefits(self) -> bool:
        """Check if employee is eligible for benefits."""
        if not self.benefits_enrolled:
            return False
        if not self.benefits_start_date:
            return False
        return date.today() >= self.benefits_start_date
    
    def get_skill_level(self, skill_name: str) -> Optional[str]:
        """Get the level of a specific skill."""
        return self.skills.get(skill_name, {}).get('level')
    
    def add_skill(self, skill_name: str, level: str, years_experience: Optional[int] = None):
        """Add or update a skill."""
        if not self.skills:
            self.skills = {}
        self.skills[skill_name] = {
            'level': level,
            'years_experience': years_experience,
            'added_date': date.today().isoformat()
        }
    
    def add_certification(self, cert_name: str, issuing_organization: str, issue_date: date, expiry_date: Optional[date] = None):
        """Add a certification."""
        if not self.certifications:
            self.certifications = {}
        self.certifications[cert_name] = {
            'issuing_organization': issuing_organization,
            'issue_date': issue_date.isoformat(),
            'expiry_date': expiry_date.isoformat() if expiry_date else None
        }
    
    def is_certification_valid(self, cert_name: str) -> bool:
        """Check if a certification is still valid."""
        if cert_name not in self.certifications:
            return False
        cert = self.certifications[cert_name]
        if not cert.get('expiry_date'):
            return True
        return date.today() <= datetime.fromisoformat(cert['expiry_date']).date()
    
    def get_custom_field(self, field_name: str, default=None):
        """Get a custom field value."""
        return self.custom_fields.get(field_name, default)
    
    def set_custom_field(self, field_name: str, value):
        """Set a custom field value."""
        if not self.custom_fields:
            self.custom_fields = {}
        self.custom_fields[field_name] = value


class Department(BaseUUIDModel):
    """
    Department model representing organizational structure.
    
    Departments are used to group employees and define reporting hierarchies.
    """
    
    __tablename__ = "departments"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Department Hierarchy
    parent_department_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("departments.id"), 
        nullable=True
    )
    
    # Department Head
    department_head_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("employees.id"), 
        nullable=True
    )
    
    # Department Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    budget: Mapped[Optional[Numeric]] = mapped_column(Numeric(15, 2), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    parent_department: Mapped[Optional["Department"]] = relationship(
        "Department", 
        remote_side="Department.id",
        back_populates="child_departments"
    )
    child_departments: Mapped[List["Department"]] = relationship(
        "Department", 
        back_populates="parent_department"
    )
    department_head: Mapped[Optional["Employee"]] = relationship(
        "Employee", 
        foreign_keys=[department_head_id]
    )
    employees: Mapped[List["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        foreign_keys="[Employee.department_id]"
    )
    
    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    @property
    def employee_count(self) -> int:
        """Get the number of active employees in the department."""
        return len([emp for emp in self.employees if emp.is_active_employee])
    
    @property
    def full_name(self) -> str:
        """Get the full department name including parent departments."""
        if self.parent_department:
            return f"{self.parent_department.full_name} > {self.name}"
        return self.name
    
    def get_all_employees(self) -> List["Employee"]:
        """Get all employees in this department and sub-departments."""
        employees = list(self.employees)
        for child_dept in self.child_departments:
            employees.extend(child_dept.get_all_employees())
        return employees

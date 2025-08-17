"""
Payroll models for HRMS-SAAS system.
Handles salary processing, deductions, allowances, and payroll management.
"""

from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Date, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .base import BaseUUIDModel

if TYPE_CHECKING:
    from .employee import Employee


class PayrollStatus(str, enum.Enum):
    """Payroll status enumeration."""
    DRAFT = "draft"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration."""
    BANK_TRANSFER = "bank-transfer"
    CHECK = "check"
    CASH = "cash"
    MOBILE_MONEY = "mobile-money"
    CRYPTO = "crypto"


class PayrollFrequency(str, enum.Enum):
    """Payroll frequency enumeration."""
    WEEKLY = "weekly"
    BI_WEEKLY = "bi-weekly"
    SEMI_MONTHLY = "semi-monthly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class TaxStatus(str, enum.Enum):
    """Tax status enumeration."""
    SINGLE = "single"
    MARRIED_JOINTLY = "married-jointly"
    MARRIED_SEPARATELY = "married-separately"
    HEAD_OF_HOUSEHOLD = "head-of-household"


class PayrollEntry(BaseUUIDModel):
    """Payroll Entry model for individual employee payroll records."""
    __tablename__ = "payroll_entries"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    # Basic Information
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    payroll_run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("payroll_runs.id"), nullable=True, index=True)
    
    # Pay Period
    pay_period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pay_period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pay_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Status and Processing
    status: Mapped[PayrollStatus] = mapped_column(Enum(PayrollStatus), default=PayrollStatus.DRAFT, nullable=False)
    processed_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    processed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    approved_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Basic Salary Components
    basic_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    hourly_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    hours_worked: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Overtime
    overtime_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overtime_rate_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.5)
    overtime_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    
    # Allowances
    housing_allowance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    transport_allowance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    meal_allowance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    medical_allowance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    communication_allowance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    other_allowances: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_allowances: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    
    # Bonuses and Incentives
    performance_bonus: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    sales_commission: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    attendance_bonus: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    holiday_bonus: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    other_bonuses: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_bonuses: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    
    # Deductions
    income_tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    social_security: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    pension_contribution: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    health_insurance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    life_insurance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    loan_deduction: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    advance_deduction: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    other_deductions: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    
    # Calculated Totals
    gross_pay: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    taxable_income: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    net_pay: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    
    # Payment Details
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), default=PaymentMethod.BANK_TRANSFER, nullable=False)
    bank_account_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Tax Information
    tax_status: Mapped[Optional[TaxStatus]] = mapped_column(Enum(TaxStatus), nullable=True)
    tax_exemptions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ytd_gross_pay: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    ytd_tax_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    ytd_net_pay: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    
    # Metadata
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    calculation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id], back_populates="payroll_entries")
    payroll_run: Mapped[Optional["PayrollRun"]] = relationship("PayrollRun", back_populates="entries")
    
    def __repr__(self):
        return f"<PayrollEntry(id={self.id}, employee_id='{self.employee_id}', period={self.pay_period_start}-{self.pay_period_end})>"
    
    @property
    def pay_period_days(self) -> int:
        """Calculate number of days in pay period."""
        return (self.pay_period_end - self.pay_period_start).days + 1
    
    @property
    def is_processed(self) -> bool:
        """Check if payroll is processed."""
        return self.status in [PayrollStatus.CALCULATED, PayrollStatus.APPROVED, PayrollStatus.PAID]
    
    def calculate_totals(self):
        """Calculate payroll totals."""
        # Calculate total allowances
        self.total_allowances = (
            self.housing_allowance + self.transport_allowance + self.meal_allowance +
            self.medical_allowance + self.communication_allowance + self.other_allowances
        )
        
        # Calculate total bonuses
        self.total_bonuses = (
            self.performance_bonus + self.sales_commission + self.attendance_bonus +
            self.holiday_bonus + self.other_bonuses
        )
        
        # Calculate total deductions
        self.total_deductions = (
            self.income_tax + self.social_security + self.pension_contribution +
            self.health_insurance + self.life_insurance + self.loan_deduction +
            self.advance_deduction + self.other_deductions
        )
        
        # Calculate gross pay
        self.gross_pay = self.basic_salary + self.total_allowances + self.total_bonuses + self.overtime_amount
        
        # Calculate taxable income (gross pay minus non-taxable allowances)
        self.taxable_income = self.gross_pay - (self.meal_allowance + self.medical_allowance)
        
        # Calculate net pay
        self.net_pay = self.gross_pay - self.total_deductions


class PayrollRun(BaseUUIDModel):
    """Payroll Run model for batch payroll processing."""
    __tablename__ = "payroll_runs"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    # Basic Information
    run_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pay Period
    pay_period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pay_period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pay_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Processing Information
    status: Mapped[PayrollStatus] = mapped_column(Enum(PayrollStatus), default=PayrollStatus.DRAFT, nullable=False)
    frequency: Mapped[PayrollFrequency] = mapped_column(Enum(PayrollFrequency), nullable=False)
    
    # Processing Dates and Users
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    processed_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    processed_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    approved_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Summary Totals
    total_employees: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_gross_pay: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total_net_pay: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total_taxes: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    
    # Filters and Criteria
    department_ids: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    employee_ids: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    include_terminated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metadata
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    processing_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Relationships
    entries: Mapped[List["PayrollEntry"]] = relationship("PayrollEntry", back_populates="payroll_run")
    
    def __repr__(self):
        return f"<PayrollRun(id={self.id}, name='{self.run_name}', status='{self.status}')>"
    
    @property
    def pay_period_days(self) -> int:
        """Calculate number of days in pay period."""
        return (self.pay_period_end - self.pay_period_start).days + 1
    
    @property
    def is_processed(self) -> bool:
        """Check if payroll run is processed."""
        return self.status in [PayrollStatus.CALCULATED, PayrollStatus.APPROVED, PayrollStatus.PAID]
    
    @property
    def average_salary(self) -> Optional[Decimal]:
        """Calculate average salary for the payroll run."""
        if self.total_employees == 0:
            return None
        return self.total_gross_pay / self.total_employees


class SalaryStructure(BaseUUIDModel):
    """Salary Structure model for defining pay components."""
    __tablename__ = "salary_structures"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Structure Details
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Pay Components
    base_salary_component: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    allowance_components: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    deduction_components: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Rules and Calculations
    calculation_rules: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    tax_rules: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    overtime_rules: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Applicability
    department_ids: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    job_grades: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    employee_types: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    # Metadata
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    def __repr__(self):
        return f"<SalaryStructure(id={self.id}, name='{self.name}', active={self.is_active})>"
    
    @property
    def is_current(self) -> bool:
        """Check if salary structure is currently active."""
        today = date.today()
        if not self.is_active:
            return False
        if today < self.effective_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        return True


class PayrollAuditLog(BaseUUIDModel):
    """Payroll Audit Log model for tracking payroll changes."""
    __tablename__ = "payroll_audit_logs"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    # Reference Information
    payroll_entry_id: Mapped[str] = mapped_column(String(36), ForeignKey("payroll_entries.id"), nullable=False, index=True)
    payroll_run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("payroll_runs.id"), nullable=True, index=True)
    
    # Audit Details
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # 'create', 'update', 'delete', 'approve', 'pay'
    changed_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    change_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Change Details
    field_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    def __repr__(self):
        return f"<PayrollAuditLog(id={self.id}, action='{self.action}', changed_by='{self.changed_by}')>"

"""
Leave Management Models for HRMS-SAAS.
Defines models for leave requests, types, and balances.
"""

from typing import Optional, List
from sqlalchemy import String, Date, DateTime, Float, Boolean, Text, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import date, datetime
import enum

from .base import BaseUUIDModel


class LeaveStatus(str, enum.Enum):
    """Leave request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveType(str, enum.Enum):
    """Leave types."""
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"
    OTHER = "other"


class LeaveRequest(BaseUUIDModel):
    """Leave request model."""
    __tablename__ = "leave_requests"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    leave_type: Mapped[LeaveType] = mapped_column(SQLEnum(LeaveType), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM format
    end_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)    # HH:MM format
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[LeaveStatus] = mapped_column(SQLEnum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False, index=True)
    requested_days: Mapped[float] = mapped_column(Float, nullable=False)
    approved_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    approver_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    approval_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id], back_populates="leave_requests")
    approver: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[approver_id])


class LeaveBalance(BaseUUIDModel):
    """Leave balance model for tracking employee leave entitlements."""
    __tablename__ = "leave_balances"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    leave_type: Mapped[LeaveType] = mapped_column(SQLEnum(LeaveType), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    total_days: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    used_days: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pending_days: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carried_over_days: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_carry_over: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="leave_balances")
    
    @property
    def remaining_days(self) -> float:
        """Calculate remaining leave days."""
        return self.total_days + self.carried_over_days - self.used_days - self.pending_days


class LeavePolicy(BaseUUIDModel):
    """Leave policy model for defining leave rules and entitlements."""
    __tablename__ = "leave_policies"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    leave_type: Mapped[LeaveType] = mapped_column(SQLEnum(LeaveType), nullable=False, index=True)
    default_days: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_notice_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_consecutive_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_documentation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rules: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)  # Additional policy rules


class LeaveCalendar(BaseUUIDModel):
    """Leave calendar model for tracking holidays and company events."""
    __tablename__ = "leave_calendars"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    holiday_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_working_day: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    working_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Hours for partial working days
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Annual holidays
    recurrence_pattern: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # Recurrence rules


class LeaveApprovalWorkflow(BaseUUIDModel):
    """Leave approval workflow model for defining approval chains."""
    __tablename__ = "leave_approval_workflows"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    leave_type: Mapped[LeaveType] = mapped_column(SQLEnum(LeaveType), nullable=False, index=True)
    department_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("departments.id"), nullable=True)
    min_days_for_approval: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    approval_levels: Mapped[List[dict]] = mapped_column(JSONB, default=list, nullable=False)  # Approval chain
    auto_approve: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    department: Mapped[Optional["Department"]] = relationship("Department")


class LeaveNotification(BaseUUIDModel):
    """Leave notification model for tracking notifications sent to approvers and employees."""
    __tablename__ = "leave_notifications"
    
    # Multi-tenant isolation
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    
    leave_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("leave_requests.id"), nullable=False, index=True)
    recipient_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id"), nullable=False, index=True)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # email, sms, in_app
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, sent, delivered, failed
    
    # Relationships
    leave_request: Mapped["LeaveRequest"] = relationship("LeaveRequest")
    recipient: Mapped["Employee"] = relationship("Employee", foreign_keys=[recipient_id])

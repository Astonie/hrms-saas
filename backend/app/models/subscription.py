"""
Subscription Plan Models for HRMS-SAAS.
Defines subscription plans, features, and module access configurations.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Integer, DateTime, Boolean, Enum as SQLEnum, ForeignKey, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, date
import enum

from .base import BaseIntegerModel


class PlanType(str, enum.Enum):
    """Plan type enumeration."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingFrequency(str, enum.Enum):
    """Billing frequency enumeration."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class SubscriptionPlan(BaseIntegerModel):
    """Subscription plan configuration model."""
    __tablename__ = "subscription_plans"
    __table_args__ = {
        'schema': 'public',
        'comment': 'Available subscription plans and their configurations'
    }
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    plan_type: Mapped[PlanType] = mapped_column(SQLEnum(PlanType), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Pricing
    monthly_price: Mapped[Optional[Numeric(10, 2)]] = mapped_column(Numeric(10, 2), nullable=True)
    yearly_price: Mapped[Optional[Numeric(10, 2)]] = mapped_column(Numeric(10, 2), nullable=True)
    setup_fee: Mapped[Optional[Numeric(10, 2)]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Limits & Quotas
    max_users: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_employees: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    max_storage_gb: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_projects: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_departments: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    
    # Module Access
    enabled_modules: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    module_limits: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    feature_flags: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Trial & Contract
    trial_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contract_min_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Support & SLA
    support_tier: Mapped[str] = mapped_column(String(50), default="basic", nullable=False)
    response_time_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    uptime_guarantee: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)  # 99.99%
    
    # Custom Fields
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    tenants: Mapped[List["Tenant"]] = relationship(
        "Tenant",
        back_populates="subscription_plan",
        foreign_keys="[Tenant.subscription_plan_id]"
    )
    plan_features: Mapped[List["PlanFeature"]] = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")

    @property
    def is_free(self) -> bool:
        """Check if plan is free."""
        return self.plan_type == PlanType.FREE

    @property
    def has_trial(self) -> bool:
        """Check if plan has trial period."""
        return self.trial_days > 0

    def get_module_limit(self, module: str, limit_type: str) -> Any:
        """Get module-specific limits."""
        return self.module_limits.get(module, {}).get(limit_type)

    def has_module_access(self, module: str) -> bool:
        """Check if plan has access to a specific module."""
        return module in self.enabled_modules

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled."""
        return self.feature_flags.get(feature, False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'plan_type': self.plan_type.value,
            'description': self.description,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'monthly_price': float(self.monthly_price) if self.monthly_price else None,
            'yearly_price': float(self.yearly_price) if self.yearly_price else None,
            'setup_fee': float(self.setup_fee) if self.setup_fee else None,
            'currency': self.currency,
            'max_users': self.max_users,
            'max_employees': self.max_employees,
            'max_storage_gb': self.max_storage_gb,
            'enabled_modules': self.enabled_modules,
            'trial_days': self.trial_days,
            'support_tier': self.support_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PlanFeature(BaseIntegerModel):
    """Individual features available in subscription plans."""
    __tablename__ = "plan_features"
    __table_args__ = {
        'schema': 'public',
        'comment': 'Features available in subscription plans'
    }
    
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.subscription_plans.id"), nullable=False, index=True)
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    feature_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    limit_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    limit_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # count, size, time, etc.
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", back_populates="plan_features", foreign_keys="[PlanFeature.plan_id]")


class ModuleDefinition(BaseIntegerModel):
    """Module definitions for the HRMS system."""
    __tablename__ = "module_definitions"
    __table_args__ = {
        'schema': 'public',
        'comment': 'Available modules in the HRMS system'
    }
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_core: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Core modules always available
    dependencies: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    permissions: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    features: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    route_path: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Module Configuration
    config_schema: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    default_settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert module to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'is_core': self.is_core,
            'dependencies': self.dependencies,
            'permissions': self.permissions,
            'features': self.features,
            'icon': self.icon,
            'route_path': self.route_path,
            'sort_order': self.sort_order
        }


# Default module definitions
DEFAULT_MODULES = [
    {
        "name": "core",
        "display_name": "Core System",
        "description": "Basic system functionality and user management",
        "is_core": True,
        "permissions": ["users:read", "users:write", "profile:read", "profile:write"],
        "features": ["user_management", "profile_management", "basic_reporting"]
    },
    {
        "name": "employees",
        "display_name": "Employee Management",
        "description": "Comprehensive employee lifecycle management",
        "is_core": False,
        "permissions": ["employees:read", "employees:write", "employees:delete", "employees:approve"],
        "features": ["employee_records", "onboarding", "offboarding", "employee_directory"]
    },
    {
        "name": "departments",
        "display_name": "Department Management",
        "description": "Organizational structure and department management",
        "is_core": False,
        "permissions": ["departments:read", "departments:write", "departments:delete"],
        "features": ["org_chart", "department_hierarchy", "headcount_planning"]
    },
    {
        "name": "leave",
        "display_name": "Leave Management",
        "description": "Leave requests, approvals, and calendar management",
        "is_core": False,
        "permissions": ["leave:read", "leave:write", "leave:approve", "leave:delete"],
        "features": ["leave_requests", "leave_calendar", "leave_balances", "approval_workflows"]
    },
    {
        "name": "attendance",
        "display_name": "Attendance Tracking",
        "description": "Time tracking, attendance monitoring, and reporting",
        "is_core": False,
        "permissions": ["attendance:read", "attendance:write", "attendance:approve"],
        "features": ["time_tracking", "attendance_reports", "overtime_management"]
    },
    {
        "name": "payroll",
        "display_name": "Payroll Management",
        "description": "Salary processing, tax calculations, and payroll reports",
        "is_core": False,
        "permissions": ["payroll:read", "payroll:write", "payroll:approve"],
        "features": ["salary_processing", "tax_calculations", "payroll_reports"]
    },
    {
        "name": "performance",
        "display_name": "Performance Management",
        "description": "Performance reviews, goal setting, and feedback systems",
        "is_core": False,
        "permissions": ["performance:read", "performance:write", "performance:approve"],
        "features": ["performance_reviews", "goal_management", "feedback_system"]
    },
    {
        "name": "recruitment",
        "display_name": "Recruitment & Hiring",
        "description": "Job posting, candidate management, and hiring workflows",
        "is_core": False,
        "permissions": ["recruitment:read", "recruitment:write", "recruitment:approve"],
        "features": ["job_postings", "candidate_tracking", "interview_scheduling"]
    },
    {
        "name": "training",
        "display_name": "Training & Development",
        "description": "Training programs, skill development, and certifications",
        "is_core": False,
        "permissions": ["training:read", "training:write", "training:approve"],
        "features": ["training_programs", "skill_assessments", "certification_tracking"]
    },
    {
        "name": "documents",
        "display_name": "Document Management",
        "description": "Document storage, version control, and compliance",
        "is_core": False,
        "permissions": ["documents:read", "documents:write", "documents:delete"],
        "features": ["document_storage", "version_control", "compliance_tracking"]
    }
]

# Default subscription plans
DEFAULT_PLANS = [
    {
        "name": "Free",
        "plan_type": "free",
        "description": "Basic HRMS functionality for small teams",
        "monthly_price": 0,
        "yearly_price": 0,
        "max_users": 3,
        "max_employees": 10,
        "max_storage_gb": 1,
        "enabled_modules": ["core", "employees", "departments"],
        "trial_days": 0,
        "support_tier": "community"
    },
    {
        "name": "Basic",
        "plan_type": "basic",
        "description": "Essential HR tools for growing businesses",
        "monthly_price": 29,
        "yearly_price": 290,
        "max_users": 10,
        "max_employees": 50,
        "max_storage_gb": 5,
        "enabled_modules": ["core", "employees", "departments", "leave", "attendance"],
        "trial_days": 14,
        "support_tier": "email"
    },
    {
        "name": "Professional",
        "plan_type": "professional",
        "description": "Complete HR solution for established companies",
        "monthly_price": 79,
        "yearly_price": 790,
        "max_users": 25,
        "max_employees": 200,
        "max_storage_gb": 20,
        "enabled_modules": ["core", "employees", "departments", "leave", "attendance", "payroll", "performance"],
        "trial_days": 14,
        "support_tier": "priority"
    },
    {
        "name": "Enterprise",
        "plan_type": "enterprise",
        "description": "Advanced HRMS with custom features and dedicated support",
        "monthly_price": 199,
        "yearly_price": 1990,
        "max_users": 100,
        "max_employees": 1000,
        "max_storage_gb": 100,
        "enabled_modules": ["core", "employees", "departments", "leave", "attendance", "payroll", "performance", "recruitment", "training", "documents"],
        "trial_days": 30,
        "support_tier": "dedicated"
    }
]

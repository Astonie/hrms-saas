"""
Tenant Management Models for HRMS-SAAS.
Defines tenant organization, subscription plans, and module access control.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Integer, DateTime, Boolean, Enum as SQLEnum, ForeignKey, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, date
import enum

from .base import BaseIntegerModel


class TenantStatus(str, enum.Enum):
    """Tenant status enumeration."""
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TenantPlan(str, enum.Enum):
    """Subscription plan enumeration."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingCycle(str, enum.Enum):
    """Billing cycle enumeration."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class Tenant(BaseIntegerModel):
    """Tenant organization model."""
    __tablename__ = "tenants"
    __table_args__ = {
        'schema': 'public',  # Tenants are always in public schema
        'comment': 'Tenant organizations using the HRMS platform'
    }
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Contact Information
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Company Information
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Subscription & Billing
    plan: Mapped[TenantPlan] = mapped_column(SQLEnum(TenantPlan), default=TenantPlan.FREE, nullable=False, index=True)
    # Link to subscription plan record (optional)
    subscription_plan_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("public.subscription_plans.id"), nullable=True, index=True)
    status: Mapped[TenantStatus] = mapped_column(SQLEnum(TenantStatus), default=TenantStatus.ACTIVE, nullable=False, index=True)
    billing_cycle: Mapped[BillingCycle] = mapped_column(SQLEnum(BillingCycle), default=BillingCycle.MONTHLY, nullable=False)
    # Tests expect these field names
    trial_ends_at: Mapped[Optional[date]] = mapped_column(DateTime, nullable=True)
    subscription_ends_at: Mapped[Optional[date]] = mapped_column(DateTime, nullable=True)
    subscription_start_date: Mapped[Optional[date]] = mapped_column(DateTime, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Limits & Usage
    max_users: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_employees: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    max_storage_gb: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_employees: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_storage_gb: Mapped[Numeric(10, 2)] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    
    # Module Access Control
    enabled_modules: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    module_limits: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    feature_flags: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Billing Information
    billing_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    billing_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    monthly_rate: Mapped[Optional[Numeric(10, 2)]] = mapped_column(Numeric(10, 2), nullable=True)
    setup_fee: Mapped[Optional[Numeric(10, 2)]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Configuration & Branding
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en-US", nullable=False)
    date_format: Mapped[str] = mapped_column(String(20), default="MM/DD/YYYY", nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    secondary_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    # Integration Settings
    integrations: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    webhook_urls: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    api_keys: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Support & Onboarding
    support_tier: Mapped[str] = mapped_column(String(50), default="basic", nullable=False)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    onboarding_steps: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    assigned_account_manager: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Compliance & Security
    data_retention_days: Mapped[int] = mapped_column(Integer, default=2555, nullable=False)  # 7 years
    backup_frequency: Mapped[str] = mapped_column(String(50), default="daily", nullable=False)
    encryption_level: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
    compliance_certifications: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    # Analytics & Metrics
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_calls_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_usage_history: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    
    # Custom Fields
    custom_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    # Link back to subscription plan
    subscription_plan: Mapped[Optional["SubscriptionPlan"]] = relationship("SubscriptionPlan", back_populates="tenants", foreign_keys=[subscription_plan_id])
    subscription_history: Mapped[List["TenantSubscriptionHistory"]] = relationship("TenantSubscriptionHistory", back_populates="tenant", cascade="all, delete-orphan")
    billing_invoices: Mapped[List["TenantBillingInvoice"]] = relationship("TenantBillingInvoice", back_populates="tenant", cascade="all, delete-orphan")
    usage_logs: Mapped[List["TenantUsageLog"]] = relationship("TenantUsageLog", back_populates="tenant", cascade="all, delete-orphan")

    @property
    def is_active(self) -> bool:
        """Check if tenant is active."""
        return self.status in [TenantStatus.ACTIVE, TenantStatus.TRIAL]

    @property
    def is_trial(self) -> bool:
        """Check if tenant is in trial period."""
        return self.status == TenantStatus.TRIAL

    @property
    def is_subscription_expired(self) -> bool:
        """Check if subscription has expired."""
        if not self.subscription_end_date:
            return False
        return datetime.now().date() > self.subscription_end_date

    @property
    def days_until_trial_end(self) -> Optional[int]:
        """Get days until trial ends."""
        if not self.trial_end_date:
            return None
        delta = self.trial_end_date - datetime.now().date()
        return max(0, delta.days)

    @property
    def usage_percentage(self) -> Dict[str, float]:
        """Get usage percentages for limits."""
        return {
            'users': (self.current_users / self.max_users) * 100 if self.max_users > 0 else 0,
            'employees': (self.current_employees / self.max_employees) * 100 if self.max_employees > 0 else 0,
            'storage': (float(self.current_storage_gb) / self.max_storage_gb) * 100 if self.max_storage_gb > 0 else 0
        }

    def has_module_access(self, module: str) -> bool:
        """Check if tenant has access to a specific module."""
        return module in self.enabled_modules

    # Settings API expected by tests
    def set_setting(self, key: str, value):
        if not self.custom_fields:
            self.custom_fields = {}
        self.custom_fields[key] = value

    def get_setting(self, key: str, default=None):
        return self.custom_fields.get(key, default)

    def has_feature(self, feature: str) -> bool:
        return self.feature_flags.get(feature, False)

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"

    def __repr__(self) -> str:
        return f"<Tenant(name='{self.name}', slug='{self.slug}')>"

    def can_add_user(self) -> bool:
        """Check if tenant can add more users."""
        return self.current_users < self.max_users

    def can_add_employee(self) -> bool:
        """Check if tenant can add more employees."""
        return self.current_employees < self.max_employees

    def can_use_storage(self, size_gb: float) -> bool:
        """Check if tenant can use additional storage."""
        return float(self.current_storage_gb) + size_gb <= self.max_storage_gb

    def get_module_limit(self, module: str, limit_type: str) -> Any:
        """Get module-specific limits."""
        return self.module_limits.get(module, {}).get(limit_type)

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled."""
        return self.feature_flags.get(feature, False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'domain': self.domain,
            'subdomain': self.subdomain,
            'contact_email': self.contact_email,
            'company_name': self.company_name,
            'plan': self.plan.value,
            'status': self.status.value,
            'billing_cycle': self.billing_cycle.value,
            'subscription_start_date': self.subscription_start_date.isoformat() if self.subscription_start_date else None,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'max_users': self.max_users,
            'max_employees': self.max_employees,
            'max_storage_gb': self.max_storage_gb,
            'current_users': self.current_users,
            'current_employees': self.current_employees,
            'current_storage_gb': float(self.current_storage_gb),
            'enabled_modules': self.enabled_modules,
            'feature_flags': self.feature_flags,
            'usage_percentage': self.usage_percentage,
            'is_active': self.is_active,
            'is_trial': self.is_trial,
            'days_until_trial_end': self.days_until_trial_end,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TenantSubscriptionHistory(BaseIntegerModel):
    """Tenant subscription history model."""
    __tablename__ = "tenant_subscription_history"
    __table_args__ = {
        'schema': 'public',
        'comment': 'History of tenant subscription changes'
    }
    
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    old_plan: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_plan: Mapped[str] = mapped_column(String(50), nullable=False)
    change_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    change_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    initiated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    proration_amount: Mapped[Optional[Numeric(10, 2)]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="subscription_history")


class TenantBillingInvoice(BaseIntegerModel):
    """Tenant billing invoice model."""
    __tablename__ = "tenant_billing_invoices"
    __table_args__ = {
        'schema': 'public',
        'comment': 'Billing invoices for tenants'
    }
    
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    invoice_date: Mapped[date] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[date] = mapped_column(DateTime, nullable=False)
    amount: Mapped[Numeric(10, 2)] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[Numeric(10, 2)] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_amount: Mapped[Numeric(10, 2)] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="billing_invoices")


class TenantUsageLog(BaseIntegerModel):
    """Tenant usage logging model."""
    __tablename__ = "tenant_usage_logs"
    __table_args__ = {
        'schema': 'public',
        'comment': 'Log of tenant resource usage'
    }
    
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.tenants.id"), nullable=False, index=True)
    log_date: Mapped[date] = mapped_column(DateTime, nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Numeric(10, 2)] = mapped_column(Numeric(10, 2), default=1, nullable=False)
    # 'metadata' is a reserved attribute name in SQLAlchemy's Declarative API.
    # Use `meta` as the Python attribute name but keep the database column named 'metadata'.
    meta: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="usage_logs")

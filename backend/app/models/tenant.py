"""
Tenant model for multi-tenant HRMS system.
Represents organizations that use the HRMS platform.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .base import BaseIntegerModel


class TenantStatus(str, enum.Enum):
    """Tenant status enumeration."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PENDING = "pending"
    TRIAL = "trial"


class TenantPlan(str, enum.Enum):
    """Tenant subscription plan enumeration."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class Tenant(BaseIntegerModel):
    """
    Tenant model representing organizations using the HRMS platform.
    
    This model is stored in the public schema and manages tenant-specific
    configurations, subscriptions, and metadata.
    """
    
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
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status and Plan
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus), 
        default=TenantStatus.PENDING, 
        nullable=False
    )
    plan: Mapped[TenantPlan] = mapped_column(
        Enum(TenantPlan), 
        default=TenantPlan.FREE, 
        nullable=False
    )
    
    # Subscription Details
    subscription_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    subscription_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Limits and Quotas
    max_users: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_storage_gb: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_projects: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # Configuration
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en_US", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Features and Settings
    features_enabled: Mapped[dict] = mapped_column(
        JSONB, 
        default=dict, 
        nullable=False
    )
    settings: Mapped[dict] = mapped_column(
        JSONB, 
        default=dict, 
        nullable=False
    )
    
    # Branding
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    secondary_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    # Integration Settings
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Billing Information
    billing_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    billing_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Override base fields for tenant model
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', slug='{self.slug}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if tenant is active."""
        return self.status == TenantStatus.ACTIVE
    
    @property
    def is_trial(self) -> bool:
        """Check if tenant is in trial period."""
        if not self.trial_end_date:
            return False
        return datetime.utcnow() < self.trial_end_date
    
    @property
    def is_subscription_expired(self) -> bool:
        """Check if subscription has expired."""
        if not self.subscription_end_date:
            return False
        return datetime.utcnow() > self.subscription_end_date
    
    def can_add_user(self) -> bool:
        """Check if tenant can add more users."""
        # This would need to be implemented with actual user count
        return True
    
    def can_use_feature(self, feature_name: str) -> bool:
        """Check if tenant can use a specific feature."""
        return self.features_enabled.get(feature_name, False)
    
    def get_setting(self, key: str, default=None):
        """Get a tenant-specific setting."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value):
        """Set a tenant-specific setting."""
        if not self.settings:
            self.settings = {}
        self.settings[key] = value
    
    def enable_feature(self, feature_name: str):
        """Enable a feature for the tenant."""
        if not self.features_enabled:
            self.features_enabled = {}
        self.features_enabled[feature_name] = True
    
    def disable_feature(self, feature_name: str):
        """Disable a feature for the tenant."""
        if not self.features_enabled:
            self.features_enabled = {}
        self.features_enabled[feature_name] = False

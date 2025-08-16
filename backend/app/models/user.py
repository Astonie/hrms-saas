"""
User and Role models for HRMS-SAAS system.
Handles authentication, authorization, and user management.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .base import BaseUUIDModel


class UserStatus(str, enum.Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    LOCKED = "locked"


class UserType(str, enum.Enum):
    """User type enumeration."""
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR_MANAGER = "hr_manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class Role(BaseUUIDModel):
    """
    Role model for role-based access control (RBAC).
    
    Each tenant has their own set of roles with specific permissions.
    """
    
    __tablename__ = "roles"
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Permissions
    permissions: Mapped[dict] = mapped_column(
        JSONB, 
        default=dict, 
        nullable=False
    )
    
    # Role Hierarchy
    parent_role_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("roles.id"), 
        nullable=True
    )
    
    # Role Settings
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    parent_role: Mapped[Optional["Role"]] = relationship(
        "Role", 
        remote_side="Role.id",
        back_populates="child_roles"
    )
    child_roles: Mapped[List["Role"]] = relationship(
        "Role", 
        back_populates="parent_role"
    )
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole", 
        back_populates="role"
    )
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission."""
        return self.permissions.get(permission, False)
    
    def add_permission(self, permission: str):
        """Add a permission to the role."""
        if not self.permissions:
            self.permissions = {}
        self.permissions[permission] = True
    
    def remove_permission(self, permission: str):
        """Remove a permission from the role."""
        if self.permissions and permission in self.permissions:
            del self.permissions[permission]
    
    def get_all_permissions(self) -> List[str]:
        """Get all permissions for this role and its parent roles."""
        permissions = set()
        
        # Add current role permissions
        if self.permissions:
            permissions.update(self.permissions.keys())
        
        # Add parent role permissions
        if self.parent_role:
            permissions.update(self.parent_role.get_all_permissions())
        
        return list(permissions)


class User(BaseUUIDModel):
    """
    User model representing individuals in the HRMS system.
    
    Each user belongs to a specific tenant and has one or more roles.
    """
    
    __tablename__ = "users"
    
    # Basic Information
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Profile Information
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Professional Information
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    hire_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status and Type
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), 
        default=UserStatus.PENDING, 
        nullable=False
    )
    user_type: Mapped[UserType] = mapped_column(
        Enum(UserType), 
        default=UserType.EMPLOYEE, 
        nullable=False
    )
    
    # Security
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en_US", nullable=False)
    preferences: Mapped[dict] = mapped_column(
        JSONB, 
        default=dict, 
        nullable=False
    )
    
    # Avatar and Media
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self) -> str:
        """Get user's display name."""
        return self.full_name
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated and active."""
        return self.is_active and not self.is_locked and self.is_verified
    
    def get_roles(self) -> List[Role]:
        """Get all roles assigned to the user."""
        return [user_role.role for user_role in self.user_roles]
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.get_roles())
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        for role in self.get_roles():
            if role.has_permission(permission):
                return True
        return False
    
    def get_permissions(self) -> List[str]:
        """Get all permissions for the user."""
        permissions = set()
        for role in self.get_roles():
            permissions.update(role.get_all_permissions())
        return list(permissions)
    
    def lock_account(self, duration_minutes: int = 30):
        """Lock the user account for a specified duration."""
        from datetime import timedelta
        self.is_locked = True
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def unlock_account(self):
        """Unlock the user account."""
        self.is_locked = False
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def record_failed_login(self):
        """Record a failed login attempt."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
    
    def record_successful_login(self):
        """Record a successful login."""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        if self.is_locked:
            self.unlock_account()
    
    def get_preference(self, key: str, default=None):
        """Get a user preference."""
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value):
        """Set a user preference."""
        if not self.preferences:
            self.preferences = {}
        self.preferences[key] = value


class UserRole(BaseUUIDModel):
    """
    Junction table for many-to-many relationship between users and roles.
    
    This allows users to have multiple roles within a tenant.
    """
    
    __tablename__ = "user_roles"
    
    # Foreign Keys
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id"), 
        nullable=False
    )
    role_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("roles.id"), 
        nullable=False
    )
    
    # Role Assignment Details
    assigned_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    user: Mapped[User] = relationship("User", back_populates="user_roles")
    role: Mapped[Role] = relationship("Role", back_populates="user_roles")
    
    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the role assignment has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if the role assignment is valid."""
        return self.is_active and not self.is_expired

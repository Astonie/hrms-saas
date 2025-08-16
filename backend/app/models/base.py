"""
Base model classes for HRMS-SAAS database models.
Provides common functionality like timestamps, soft deletes, and audit fields.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, String, Boolean, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..core.database import Base


class TimestampMixin:
    """Mixin to add timestamp fields to models."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin to add soft delete functionality to models."""
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )


class AuditMixin:
    """Mixin to add audit fields to models."""
    
    created_by: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
    deleted_by: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )


class TenantMixin:
    """Mixin to add tenant awareness to models."""
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name based on class name."""
        return cls.__name__.lower()
    
    @declared_attr
    def __table_args__(cls):
        """Add table arguments for multi-tenancy."""
        return {
            'schema': None,  # Will be set dynamically based on tenant
            'comment': f'{cls.__name__} table for multi-tenant HRMS'
        }


class BaseModel(Base, TimestampMixin, SoftDeleteMixin, AuditMixin, TenantMixin):
    """
    Base model class that includes all common functionality.
    
    Features:
    - Timestamps (created_at, updated_at)
    - Soft delete (is_deleted, deleted_at)
    - Audit fields (created_by, updated_by, deleted_by)
    - Multi-tenant support
    """
    
    __abstract__ = True
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def update_from_dict(self, data: dict):
        """Update model attributes from dictionary."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'created_by']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self, deleted_by: Optional[str] = None):
        """Soft delete the record."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None


class BaseUUIDModel(BaseModel):
    """Base model with UUID primary key."""
    
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        index=True
    )


class BaseIntegerModel(BaseModel):
    """Base model with auto-incrementing integer primary key."""
    
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True, 
        index=True
    )


class BaseBigIntegerModel(BaseModel):
    """Base model with auto-incrementing big integer primary key."""
    
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True, 
        index=True
    )


# Utility functions for models
def get_model_table_name(model_class) -> str:
    """Get the table name for a model class."""
    return model_class.__tablename__


def get_model_schema_name(model_class) -> str:
    """Get the schema name for a model class."""
    return getattr(model_class.__table__.args, 'schema', None)


def set_model_schema(model_class, schema_name: str):
    """Set the schema name for a model class."""
    if hasattr(model_class.__table__.args, 'schema'):
        model_class.__table__.args['schema'] = schema_name

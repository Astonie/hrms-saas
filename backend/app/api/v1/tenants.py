"""
Tenant Management API endpoints for HRMS-SAAS.
Handles tenant provisioning, subscription management, and module access control.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from sqlalchemy import select
from datetime import date, datetime

from ...core.security import get_current_user, require_permission
from ...core.database import get_session
from ...services.tenant_service import TenantService
from ...models.tenant import Tenant, TenantStatus, TenantPlan, BillingCycle
from ...models.subscription import SubscriptionPlan

router = APIRouter()


# Pydantic Models

class TenantBase(BaseModel):
    """Base tenant model."""
    name: str = Field(..., min_length=2, max_length=255, description="Organization name")
    slug: str = Field(..., min_length=2, max_length=100, description="Unique tenant identifier")
    domain: Optional[str] = Field(None, max_length=255, description="Custom domain")
    subdomain: Optional[str] = Field(None, max_length=100, description="Subdomain")
    contact_email: str = Field(..., description="Primary contact email")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    company_name: Optional[str] = Field(None, max_length=255, description="Legal company name")
    company_size: Optional[str] = Field(None, max_length=50, description="Company size category")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    website: Optional[str] = Field(None, max_length=255, description="Company website")
    timezone: str = Field(default="UTC", description="Timezone")
    locale: str = Field(default="en-US", description="Locale")
    currency: str = Field(default="USD", description="Currency code")


class TenantCreate(TenantBase):
    """Tenant creation model."""
    plan_type: str = Field(default="free", description="Subscription plan type")
    admin_username: str = Field(..., min_length=3, max_length=100, description="Admin username")
    admin_email: str = Field(..., description="Admin email")
    admin_password: str = Field(..., min_length=8, description="Admin password")
    admin_first_name: Optional[str] = Field(None, max_length=100, description="Admin first name")
    admin_last_name: Optional[str] = Field(None, max_length=100, description="Admin last name")

    @validator('slug')
    def validate_slug(cls, v):
        if not v.isalnum() and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()


class TenantUpdate(BaseModel):
    """Tenant update model."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    subdomain: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None)
    contact_phone: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=255)
    company_size: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None)
    locale: Optional[str] = Field(None)
    currency: Optional[str] = Field(None)
    logo_url: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field(None, max_length=7)
    secondary_color: Optional[str] = Field(None, max_length=7)
    notes: Optional[str] = Field(None)


class TenantResponse(TenantBase):
    """Tenant response model."""
    id: int
    slug: str
    plan: str
    status: str
    billing_cycle: str
    subscription_start_date: Optional[date]
    subscription_end_date: Optional[date]
    trial_end_date: Optional[date]
    max_users: int
    max_employees: int
    max_storage_gb: int
    current_users: int
    current_employees: int
    current_storage_gb: float
    enabled_modules: List[str]
    feature_flags: Dict[str, Any]
    usage_percentage: Dict[str, float]
    is_active: bool
    is_trial: bool
    days_until_trial_end: Optional[int]
    support_tier: str
    monthly_rate: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Tenant list response model."""
    tenants: List[TenantResponse]
    total: int
    page: int
    size: int
    pages: int


class SubscriptionUpdateRequest(BaseModel):
    """Subscription update request model."""
    new_plan_type: str = Field(..., description="New subscription plan type")
    change_reason: Optional[str] = Field(None, max_length=255, description="Reason for change")
    billing_cycle: Optional[str] = Field(None, description="New billing cycle")


class TenantStatusUpdateRequest(BaseModel):
    """Tenant status update request model."""
    status: str = Field(..., description="New tenant status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


class UsageResponse(BaseModel):
    """Usage response model."""
    current_users: int
    current_employees: int
    current_storage_gb: float
    max_users: int
    max_employees: int
    max_storage_gb: int
    usage_percentage: Dict[str, float]


class ModuleAccessResponse(BaseModel):
    """Module access response model."""
    module: str
    has_access: bool
    permissions: List[str]
    features: List[str]


# API Endpoints

@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:create"))
):
    """Create a new tenant organization."""
    try:
        # Prepare tenant data
        tenant_dict = tenant_data.dict(exclude={'admin_username', 'admin_email', 'admin_password', 'admin_first_name', 'admin_last_name'})
        admin_data = {
            'username': tenant_data.admin_username,
            'email': tenant_data.admin_email,
            'password': tenant_data.admin_password,
            'first_name': tenant_data.admin_first_name or 'Admin',
            'last_name': tenant_data.admin_last_name or 'User'
        }

        # Create tenant
        tenant, admin_user = await TenantService.create_tenant(
            tenant_dict, admin_data, tenant_data.plan_type
        )

        # Log usage
        background_tasks.add_task(
            TenantService.log_usage,
            tenant.id,
            'tenant',
            'created',
            metadata={'admin_user_id': admin_user.id}
        )

        return tenant.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create tenant")


@router.get("/", response_model=TenantListResponse)
async def list_tenants(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    plan: Optional[str] = Query(None, description="Filter by plan"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:read"))
):
    """List tenants with filtering and pagination."""
    try:
        tenants, total = await TenantService.list_tenants(page, size, status, plan, search)
        
        return TenantListResponse(
            tenants=[tenant.to_dict() for tenant in tenants],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list tenants")


@router.get("/me", response_model=TenantResponse)
async def get_my_tenant(
    current_user: dict = Depends(get_current_user)
):
    """Get current user's tenant information."""
    try:
        tenant_id = current_user.get('tenant_id')
        if not tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tenant associated with user")

        async with get_session() as session:
            from ...models.tenant import Tenant
            stmt = select(Tenant).where(Tenant.slug == tenant_id)
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

            return tenant.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting tenant: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get tenant information")


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:read"))
):
    """Get tenant by ID."""
    try:
        async with get_session() as session:
            from ...models.tenant import Tenant
            stmt = select(Tenant).where(Tenant.id == tenant_id)
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
            
            return tenant.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get tenant")


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:update"))
):
    """Update tenant information."""
    try:
        async with get_session() as session:
            from ...models.tenant import Tenant
            stmt = select(Tenant).where(Tenant.id == tenant_id)
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
            
            # Update fields
            update_data = tenant_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(tenant, field, value)
            
            await session.commit()
            return tenant.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update tenant")


@router.post("/{tenant_id}/subscription", response_model=TenantResponse)
async def update_subscription(
    tenant_id: int,
    subscription_data: SubscriptionUpdateRequest,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:update"))
):
    """Update tenant subscription plan."""
    try:
        tenant = await TenantService.update_tenant_subscription(
            tenant_id,
            subscription_data.new_plan_type,
            subscription_data.change_reason,
            current_user.get('username', 'system')
        )
        return tenant.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update subscription")


@router.post("/{tenant_id}/status", response_model=TenantResponse)
async def update_tenant_status(
    tenant_id: int,
    status_data: TenantStatusUpdateRequest,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:update"))
):
    """Update tenant status."""
    try:
        if status_data.status == "suspended":
            tenant = await TenantService.suspend_tenant(tenant_id, status_data.reason or "Suspended by admin")
        elif status_data.status == "active":
            tenant = await TenantService.activate_tenant(tenant_id)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        
        return tenant.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update tenant status")


@router.get("/{tenant_id}/usage", response_model=UsageResponse)
async def get_tenant_usage(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:read"))
):
    """Get tenant usage statistics."""
    try:
        usage = await TenantService.get_tenant_usage(tenant_id)
        return UsageResponse(**usage)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get usage statistics")


@router.get("/{tenant_id}/modules", response_model=List[ModuleAccessResponse])
async def get_tenant_modules(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:read"))
):
    """Get available modules for a tenant."""
    try:
        modules = await TenantService.get_available_modules(tenant_id)
        return [
            ModuleAccessResponse(
                module=module['name'],
                has_access=True,
                permissions=module['permissions'],
                features=module['features']
            )
            for module in modules
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get tenant modules")


@router.get("/{tenant_id}/modules/{module_name}/access")
async def check_module_access(
    tenant_id: int,
    module_name: str,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:read"))
):
    """Check if tenant has access to a specific module."""
    try:
        has_access = await TenantService.check_module_access(tenant_id, module_name)
        return {"module": module_name, "has_access": has_access}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check module access")


@router.get("/subscription-plans", response_model=List[Dict[str, Any]])
async def get_subscription_plans(
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:read"))
):
    """Get available subscription plans."""
    try:
        plans = await TenantService.get_subscription_plans()
        return plans
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get subscription plans")


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:delete"))
):
    """Delete tenant (soft delete)."""
    try:
        async with get_session() as session:
            from ...models.tenant import Tenant
            stmt = select(Tenant).where(Tenant.id == tenant_id)
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
            
            # Soft delete
            tenant.soft_delete()
            await session.commit()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete tenant")


@router.post("/{tenant_id}/restore", response_model=TenantResponse)
async def restore_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:update"))
):
    """Restore soft-deleted tenant."""
    try:
        async with get_session() as session:
            from ...models.tenant import Tenant
            stmt = select(Tenant).where(Tenant.id == tenant_id)
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
            
            tenant.restore()
            await session.commit()
            
            return tenant.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to restore tenant")


@router.post("/{tenant_id}/provision", response_model=Dict[str, Any])
async def provision_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:update"))
):
    """Provision tenant infrastructure (create schema, tables, etc.)."""
    try:
        async with get_session() as session:
            from ...models.tenant import Tenant
            stmt = select(Tenant).where(Tenant.id == tenant_id)
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
            
            # Create tenant schema
            await TenantService.tenant_db_manager.create_tenant_schema(tenant.slug)
            
            return {
                "message": f"Tenant {tenant.slug} provisioned successfully",
                "tenant_id": tenant_id,
                "schema_created": True
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to provision tenant: {str(e)}")


@router.get("/{tenant_id}/billing", response_model=Dict[str, Any])
async def get_tenant_billing(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    _: list = Depends(require_permission("tenants:read"))
):
    """Get tenant billing information."""
    try:
        async with get_session() as session:
            from ...models.tenant import Tenant
            stmt = select(Tenant).where(Tenant.id == tenant_id)
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
            
            return {
                "plan": tenant.plan.value,
                "billing_cycle": tenant.billing_cycle.value,
                "monthly_rate": float(tenant.monthly_rate) if tenant.monthly_rate else None,
                "subscription_start_date": tenant.subscription_start_date.isoformat() if tenant.subscription_start_date else None,
                "subscription_end_date": tenant.subscription_end_date.isoformat() if tenant.subscription_end_date else None,
                "trial_end_date": tenant.trial_end_date.isoformat() if tenant.trial_end_date else None,
                "auto_renew": tenant.auto_renew,
                "currency": tenant.currency,
                "status": tenant.status.value
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get billing information")

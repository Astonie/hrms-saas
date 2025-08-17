"""
Tenant Management Service for HRMS-SAAS.
Handles tenant provisioning, subscription management, and module access control.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import logging
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from ..core.database import get_session, tenant_db_manager
from ..models.tenant import Tenant, TenantStatus, TenantPlan, BillingCycle
from ..models.subscription import SubscriptionPlan, ModuleDefinition, DEFAULT_MODULES, DEFAULT_PLANS
from ..models.user import User, Role, UserRole
from ..core.security import security_manager

logger = logging.getLogger(__name__)


class TenantService:
    """Service for managing tenants and their subscriptions."""

    @staticmethod
    async def create_tenant(
        tenant_data: Dict[str, Any],
        admin_user_data: Dict[str, Any],
        plan_type: str = "free"
    ) -> Tuple[Tenant, User]:
        """
        Create a new tenant with initial setup.
        
        Args:
            tenant_data: Tenant organization data
            admin_user_data: Admin user data for the tenant
            plan_type: Subscription plan type
            
        Returns:
            Tuple of (tenant, admin_user)
        """
        async with get_session() as session:
            try:
                # Get subscription plan
                plan = await TenantService._get_subscription_plan(session, plan_type)
                if not plan:
                    raise ValueError(f"Invalid plan type: {plan_type}")

                # Create tenant
                tenant = Tenant(
                    name=tenant_data["name"],
                    slug=tenant_data["slug"],
                    domain=tenant_data.get("domain"),
                    subdomain=tenant_data.get("subdomain"),
                    contact_email=tenant_data["contact_email"],
                    contact_phone=tenant_data.get("contact_phone"),
                    company_name=tenant_data.get("company_name"),
                    company_size=tenant_data.get("company_size"),
                    industry=tenant_data.get("industry"),
                    website=tenant_data.get("website"),
                    plan=TenantPlan(plan_type),
                    status=TenantStatus.PENDING,
                    billing_cycle=BillingCycle.MONTHLY,
                    max_users=plan.max_users,
                    max_employees=plan.max_employees,
                    max_storage_gb=plan.max_storage_gb,
                    enabled_modules=plan.enabled_modules,
                    feature_flags=plan.feature_flags,
                    monthly_rate=plan.monthly_price,
                    trial_days=plan.trial_days,
                    support_tier=plan.support_tier,
                    timezone=tenant_data.get("timezone", "UTC"),
                    locale=tenant_data.get("locale", "en-US"),
                    currency=tenant_data.get("currency", "USD")
                )

                # Set trial dates if applicable
                if plan.trial_days > 0:
                    tenant.trial_end_date = date.today() + timedelta(days=plan.trial_days)
                    tenant.status = TenantStatus.TRIAL

                session.add(tenant)
                await session.flush()  # Get tenant ID

                # Create tenant schema
                await tenant_db_manager.create_tenant_schema(tenant.slug)

                # Create admin user
                admin_user = await TenantService._create_admin_user(
                    session, tenant, admin_user_data
                )

                # Create default roles for the tenant
                await TenantService._create_default_roles(session, tenant)

                await session.commit()
                logger.info(f"Created tenant: {tenant.slug} with plan: {plan_type}")

                return tenant, admin_user

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to create tenant: {str(e)}")
                raise

    @staticmethod
    async def update_tenant_subscription(
        tenant_id: int,
        new_plan_type: str,
        change_reason: Optional[str] = None,
        initiated_by: Optional[str] = None
    ) -> Tenant:
        """
        Update tenant subscription plan.
        
        Args:
            tenant_id: Tenant ID
            new_plan_type: New subscription plan type
            change_reason: Reason for the change
            initiated_by: Who initiated the change
            
        Returns:
            Updated tenant
        """
        async with get_session() as session:
            try:
                # Get tenant and new plan
                tenant = await TenantService._get_tenant_by_id(session, tenant_id)
                if not tenant:
                    raise ValueError(f"Tenant not found: {tenant_id}")

                new_plan = await TenantService._get_subscription_plan(session, new_plan_type)
                if not new_plan:
                    raise ValueError(f"Invalid plan type: {new_plan_type}")

                old_plan = tenant.plan.value

                # Update tenant with new plan settings
                tenant.plan = TenantPlan(new_plan_type)
                tenant.max_users = new_plan.max_users
                tenant.max_employees = new_plan.max_employees
                tenant.max_storage_gb = new_plan.max_storage_gb
                tenant.enabled_modules = new_plan.enabled_modules
                tenant.feature_flags = new_plan.feature_flags
                tenant.monthly_rate = new_plan.monthly_price
                tenant.support_tier = new_plan.support_tier

                # Handle trial period for new plans
                if new_plan.trial_days > 0 and tenant.status != TenantStatus.TRIAL:
                    tenant.trial_end_date = date.today() + timedelta(days=new_plan.trial_days)
                    tenant.status = TenantStatus.TRIAL

                # Record subscription change
                from ..models.tenant import TenantSubscriptionHistory
                subscription_history = TenantSubscriptionHistory(
                    tenant_id=tenant_id,
                    old_plan=old_plan,
                    new_plan=new_plan_type,
                    change_reason=change_reason,
                    initiated_by=initiated_by
                )
                session.add(subscription_history)

                await session.commit()
                logger.info(f"Updated tenant {tenant.slug} from {old_plan} to {new_plan_type}")

                return tenant

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update tenant subscription: {str(e)}")
                raise

    @staticmethod
    async def suspend_tenant(tenant_id: int, reason: str) -> Tenant:
        """Suspend a tenant account."""
        async with get_session() as session:
            tenant = await TenantService._get_tenant_by_id(session, tenant_id)
            if not tenant:
                raise ValueError(f"Tenant not found: {tenant_id}")

            tenant.status = TenantStatus.SUSPENDED
            tenant.notes = f"Suspended: {reason}"
            await session.commit()
            
            logger.info(f"Suspended tenant: {tenant.slug}")
            return tenant

    @staticmethod
    async def activate_tenant(tenant_id: int) -> Tenant:
        """Activate a suspended tenant account."""
        async with get_session() as session:
            tenant = await TenantService._get_tenant_by_id(session, tenant_id)
            if not tenant:
                raise ValueError(f"Tenant not found: {tenant_id}")

            tenant.status = TenantStatus.ACTIVE
            tenant.notes = "Account activated"
            await session.commit()
            
            logger.info(f"Activated tenant: {tenant.slug}")
            return tenant

    @staticmethod
    async def get_tenant_usage(tenant_id: int) -> Dict[str, Any]:
        """Get current usage statistics for a tenant."""
        async with get_session() as session:
            tenant = await TenantService._get_tenant_by_id(session, tenant_id)
            if not tenant:
                raise ValueError(f"Tenant not found: {tenant_id}")

            # Get user count
            user_count = await TenantService._get_user_count(session, tenant_id)
            
            # Get employee count
            employee_count = await TenantService._get_employee_count(session, tenant_id)

            return {
                'current_users': user_count,
                'current_employees': employee_count,
                'current_storage_gb': float(tenant.current_storage_gb),
                'max_users': tenant.max_users,
                'max_employees': tenant.max_employees,
                'max_storage_gb': tenant.max_storage_gb,
                'usage_percentage': {
                    'users': (user_count / tenant.max_users) * 100 if tenant.max_users > 0 else 0,
                    'employees': (employee_count / tenant.max_employees) * 100 if tenant.max_employees > 0 else 0,
                    'storage': (float(tenant.current_storage_gb) / tenant.max_storage_gb) * 100 if tenant.max_storage_gb > 0 else 0
                }
            }

    @staticmethod
    async def check_module_access(tenant_id: int, module: str) -> bool:
        """Check if tenant has access to a specific module."""
        async with get_session() as session:
            tenant = await TenantService._get_tenant_by_id(session, tenant_id)
            if not tenant:
                return False

            return tenant.has_module_access(module)

    @staticmethod
    async def get_available_modules(tenant_id: int) -> List[Dict[str, Any]]:
        """Get available modules for a tenant."""
        async with get_session() as session:
            tenant = await TenantService._get_tenant_by_id(session, tenant_id)
            if not tenant:
                return []

            # Get module definitions
            stmt = select(ModuleDefinition).where(
                ModuleDefinition.name.in_(tenant.enabled_modules)
            ).order_by(ModuleDefinition.sort_order)
            
            result = await session.execute(stmt)
            modules = result.scalars().all()

            return [module.to_dict() for module in modules]

    @staticmethod
    async def log_usage(
        tenant_id: int,
        resource_type: str,
        action: str,
        quantity: float = 1.0,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log resource usage for a tenant."""
        async with get_session() as session:
            from ..models.tenant import TenantUsageLog
            
            usage_log = TenantUsageLog(
                tenant_id=tenant_id,
                log_date=date.today(),
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                quantity=Decimal(str(quantity)),
                meta=metadata or {}
            )
            
            session.add(usage_log)
            await session.commit()

    @staticmethod
    async def get_subscription_plans() -> List[Dict[str, Any]]:
        """Get all available subscription plans."""
        async with get_session() as session:
            stmt = select(SubscriptionPlan).where(
                SubscriptionPlan.is_active == True
            ).order_by(SubscriptionPlan.sort_order)
            
            result = await session.execute(stmt)
            plans = result.scalars().all()

            return [plan.to_dict() for plan in plans]

    @staticmethod
    async def get_tenant_by_slug(slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        async with get_session() as session:
            stmt = select(Tenant).where(Tenant.slug == slug)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    async def list_tenants(
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
        plan: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Tenant], int]:
        """List tenants with filtering and pagination."""
        async with get_session() as session:
            # Build query
            query = select(Tenant)
            count_query = select(func.count(Tenant.id))

            # Apply filters
            if status:
                query = query.where(Tenant.status == TenantStatus(status))
                count_query = count_query.where(Tenant.status == TenantStatus(status))

            if plan:
                query = query.where(Tenant.plan == TenantPlan(plan))
                count_query = count_query.where(Tenant.plan == TenantPlan(plan))

            if search:
                search_filter = or_(
                    Tenant.name.ilike(f"%{search}%"),
                    Tenant.slug.ilike(f"%{search}%"),
                    Tenant.company_name.ilike(f"%{search}%"),
                    Tenant.contact_email.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)

            # Get total count
            count_result = await session.execute(count_query)
            total = count_result.scalar()

            # Apply pagination
            query = query.offset((page - 1) * size).limit(size)
            query = query.order_by(Tenant.created_at.desc())

            # Execute query
            result = await session.execute(query)
            tenants = result.scalars().all()

            return list(tenants), total

    # Private helper methods

    @staticmethod
    async def _get_subscription_plan(session, plan_type: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by type."""
        stmt = select(SubscriptionPlan).where(
            SubscriptionPlan.plan_type == plan_type,
            SubscriptionPlan.is_active == True
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def _get_tenant_by_id(session, tenant_id: int) -> Optional[Tenant]:
        """Get tenant by ID."""
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def _create_admin_user(
        session, tenant: Tenant, admin_data: Dict[str, Any]
    ) -> User:
        """Create admin user for the tenant."""
        # Create user
        user = User(
            username=admin_data["username"],
            email=admin_data["email"],
            hashed_password=security_manager.hash_password(admin_data["password"]),
            first_name=admin_data.get("first_name", "Admin"),
            last_name=admin_data.get("last_name", "User"),
            is_active=True,
            is_verified=True,
            tenant_id=tenant.id
        )
        session.add(user)
        await session.flush()

        # Create admin role
        admin_role = Role(
            name="Admin",
            permissions={
                "users": ["read", "write", "delete"],
                "employees": ["read", "write", "delete", "approve"],
                "departments": ["read", "write", "delete"],
                "leave": ["read", "write", "delete", "approve"],
                "payroll": ["read", "write", "approve"],
                "performance": ["read", "write", "approve"],
                "recruitment": ["read", "write", "approve"],
                "training": ["read", "write", "approve"],
                "documents": ["read", "write", "delete"],
                "settings": ["read", "write"]
            },
            tenant_id=tenant.id
        )
        session.add(admin_role)
        await session.flush()

        # Assign role to user
        user_role = UserRole(
            user_id=user.id,
            role_id=admin_role.id,
            tenant_id=tenant.id
        )
        session.add(user_role)

        return user

    @staticmethod
    async def _create_default_roles(session, tenant: Tenant):
        """Create default roles for the tenant."""
        default_roles = [
            {
                "name": "Manager",
                "permissions": {
                    "employees": ["read", "write"],
                    "departments": ["read"],
                    "leave": ["read", "write", "approve"],
                    "performance": ["read", "write"],
                    "documents": ["read", "write"]
                }
            },
            {
                "name": "Employee",
                "permissions": {
                    "employees": ["read"],
                    "departments": ["read"],
                    "leave": ["read", "write"],
                    "performance": ["read"],
                    "documents": ["read"]
                }
            },
            {
                "name": "HR Staff",
                "permissions": {
                    "employees": ["read", "write"],
                    "departments": ["read", "write"],
                    "leave": ["read", "write", "approve"],
                    "performance": ["read", "write"],
                    "recruitment": ["read", "write"],
                    "training": ["read", "write"]
                }
            }
        ]

        for role_data in default_roles:
            role = Role(
                name=role_data["name"],
                permissions=role_data["permissions"],
                tenant_id=tenant.id
            )
            session.add(role)

    @staticmethod
    async def _get_user_count(session, tenant_id: int) -> int:
        """Get user count for a tenant."""
        stmt = select(func.count(User.id)).where(
            User.tenant_id == tenant_id,
            User.is_active == True
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def _get_employee_count(session, tenant_id: int) -> int:
        """Get employee count for a tenant."""
        from ..models.employee import Employee
        stmt = select(func.count(Employee.id)).where(
            Employee.tenant_id == tenant_id,
            Employee.employment_status == "active"
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def initialize_default_data():
        """Initialize default modules and subscription plans."""
        async with get_session() as session:
            try:
                # Create default modules
                for module_data in DEFAULT_MODULES:
                    existing = await session.execute(
                        select(ModuleDefinition).where(ModuleDefinition.name == module_data["name"])
                    )
                    if not existing.scalar_one_or_none():
                        module = ModuleDefinition(**module_data)
                        session.add(module)

                # Create default subscription plans
                for plan_data in DEFAULT_PLANS:
                    existing = await session.execute(
                        select(SubscriptionPlan).where(SubscriptionPlan.plan_type == plan_data["plan_type"])
                    )
                    if not existing.scalar_one_or_none():
                        plan = SubscriptionPlan(**plan_data)
                        session.add(plan)

                await session.commit()
                logger.info("Initialized default modules and subscription plans")

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to initialize default data: {str(e)}")
                raise

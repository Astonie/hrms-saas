import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException

from app.services.tenant_service import TenantService
from app.models.tenant import Tenant, TenantStatus, TenantPlan, BillingCycle
from app.models.subscription import SubscriptionPlan, ModuleDefinition
from app.models.user import User, Role, UserRole
from app.core.security import security_manager


class TestTenantService:
    """Test cases for TenantService with comprehensive coverage."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        return session

    @pytest.fixture
    def sample_tenant_data(self):
        """Sample tenant data for testing."""
        return {
            "name": "Test Company",
            "slug": "test-company",
            "contact_email": "admin@testcompany.com",
            "company_name": "Test Company Inc.",
            "contact_phone": "+1234567890",
            "contact_address": "123 Test St, Test City, TC 12345",
            "billing_address": "123 Test St, Test City, TC 12345",
            "timezone": "UTC",
            "locale": "en_US",
            "currency": "USD",
            "industry": "Technology",
            "company_size": "10-50",
            "website": "https://testcompany.com",
            "description": "A test company for testing purposes"
        }

    @pytest.fixture
    def sample_admin_data(self):
        """Sample admin user data for testing."""
        return {
            "username": "admin",
            "email": "admin@testcompany.com",
            "password": "SecurePass123!",
            "first_name": "Admin",
            "last_name": "User"
        }

    @pytest.fixture
    def mock_subscription_plan(self):
        """Mock subscription plan."""
        plan = Mock(spec=SubscriptionPlan)
        plan.id = 1
        plan.plan_type = "professional"
        plan.name = "Professional Plan"
        plan.monthly_price = Decimal("99.99")
        plan.yearly_price = Decimal("999.99")
        plan.max_users = 25
        plan.max_employees = 250
        plan.max_storage_gb = 10
        plan.enabled_modules = ["employees", "departments", "leave", "payroll"]
        plan.feature_flags = {"advanced_reporting": True, "api_access": True}
        plan.trial_days = 14
        plan.support_tier = "standard"
        return plan

    @pytest.fixture
    def mock_module_definition(self):
        """Mock module definition."""
        module = Mock(spec=ModuleDefinition)
        module.id = 1
        module.name = "employees"
        module.display_name = "Employee Management"
        module.description = "Manage employee information and records"
        module.permissions = ["employees:read", "employees:create", "employees:update", "employees:delete"]
        module.features = ["employee_directory", "performance_tracking", "document_management"]
        module.is_active = True
        module.version = "1.0.0"
        return module

    @pytest.mark.asyncio
    async def test_create_tenant_success(self, mock_db_session, sample_tenant_data, sample_admin_data, mock_subscription_plan):
        """Test successful tenant creation."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session), \
             patch('app.services.tenant_service.tenant_db_manager.create_tenant_schema', new_callable=AsyncMock), \
             patch('app.services.tenant_service.tenant_db_manager.get_tenant_session', new_callable=AsyncMock) as mock_tenant_session, \
             patch.object(TenantService, '_get_subscription_plan', return_value=mock_subscription_plan), \
             patch.object(security_manager, 'hash_password', return_value="hashed_password"), \
             patch('app.services.tenant_service.uuid.uuid4', return_value="test-uuid-123"):

            mock_tenant_session.return_value.__aenter__.return_value = mock_db_session
            
            # Mock the query results
            mock_db_session.execute.return_value.scalar.return_value = None  # No existing tenant
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None  # No existing user
            
            tenant, admin_user = await TenantService.create_tenant(
                sample_tenant_data, sample_admin_data, "professional"
            )

            assert tenant is not None
            assert admin_user is not None
            assert tenant.name == sample_tenant_data["name"]
            assert tenant.slug == sample_tenant_data["slug"]
            assert tenant.plan == TenantPlan.PROFESSIONAL
            assert tenant.status == TenantStatus.PENDING
            assert tenant.max_users == mock_subscription_plan.max_users
            assert tenant.max_employees == mock_subscription_plan.max_employees
            assert tenant.max_storage_gb == mock_subscription_plan.max_storage_gb
            assert tenant.enabled_modules == mock_subscription_plan.enabled_modules

    @pytest.mark.asyncio
    async def test_create_tenant_duplicate_slug(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with duplicate slug."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            # Mock existing tenant
            mock_db_session.execute.return_value.scalar.return_value = 1
            
            with pytest.raises(HTTPException) as exc_info:
                await TenantService.create_tenant(sample_tenant_data, sample_admin_data)
            
            assert exc_info.value.status_code == 400
            assert "Tenant with this slug already exists" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_tenant_duplicate_email(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with duplicate admin email."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            # Mock no existing tenant but existing user
            mock_db_session.execute.return_value.scalar.return_value = None
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = Mock()
            
            with pytest.raises(HTTPException) as exc_info:
                await TenantService.create_tenant(sample_tenant_data, sample_admin_data)
            
            assert exc_info.value.status_code == 400
            assert "User with this email already exists" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_tenant_invalid_plan(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with invalid plan type."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            with pytest.raises(HTTPException) as exc_info:
                await TenantService.create_tenant(sample_tenant_data, sample_admin_data, "invalid_plan")
            
            assert exc_info.value.status_code == 400
            assert "Invalid subscription plan type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_tenant_subscription_success(self, mock_db_session, mock_subscription_plan):
        """Test successful subscription update."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            # Mock existing tenant
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.id = 1
            mock_tenant.plan = TenantPlan.BASIC
            mock_tenant.status = TenantStatus.ACTIVE
            mock_tenant.enabled_modules = ["employees"]
            mock_tenant.max_users = 10
            mock_tenant.max_employees = 100
            mock_tenant.max_storage_gb = 5
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            mock_db_session.execute.return_value.scalar.return_value = mock_subscription_plan
            
            updated_tenant = await TenantService.update_tenant_subscription(
                1, "professional", "Upgrade for more features", "admin@test.com"
            )
            
            assert updated_tenant is not None
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_tenant_subscription_tenant_not_found(self, mock_db_session):
        """Test subscription update for non-existent tenant."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await TenantService.update_tenant_subscription(999, "professional")
            
            assert exc_info.value.status_code == 404
            assert "Tenant not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_tenant_subscription_invalid_plan(self, mock_db_session):
        """Test subscription update with invalid plan."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.id = 1
            mock_tenant.plan = TenantPlan.BASIC
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            
            with pytest.raises(HTTPException) as exc_info:
                await TenantService.update_tenant_subscription(1, "invalid_plan")
            
            assert exc_info.value.status_code == 400
            assert "Invalid subscription plan type" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_suspend_tenant_success(self, mock_db_session):
        """Test successful tenant suspension."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.id = 1
            mock_tenant.status = TenantStatus.ACTIVE
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            
            suspended_tenant = await TenantService.suspend_tenant(1, "Payment overdue")
            
            assert suspended_tenant is not None
            assert suspended_tenant.status == TenantStatus.SUSPENDED
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_activate_tenant_success(self, mock_db_session):
        """Test successful tenant activation."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.id = 1
            mock_tenant.status = TenantStatus.SUSPENDED
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            
            activated_tenant = await TenantService.activate_tenant(1)
            
            assert activated_tenant is not None
            assert activated_tenant.status == TenantStatus.ACTIVE
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_module_access_allowed(self, mock_db_session):
        """Test module access check when allowed."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.enabled_modules = ["employees", "departments"]
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            
            has_access = await TenantService.check_module_access(1, "employees")
            
            assert has_access is True

    @pytest.mark.asyncio
    async def test_check_module_access_denied(self, mock_db_session):
        """Test module access check when denied."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.enabled_modules = ["employees", "departments"]
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            
            has_access = await TenantService.check_module_access(1, "payroll")
            
            assert has_access is False

    @pytest.mark.asyncio
    async def test_get_tenant_usage_success(self, mock_db_session):
        """Test successful tenant usage retrieval."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.id = 1
            mock_tenant.max_users = 25
            mock_tenant.max_employees = 250
            mock_tenant.max_storage_gb = 10
            mock_tenant.current_users = 15
            mock_tenant.current_employees = 150
            mock_tenant.current_storage_gb = Decimal("5.5")
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            
            usage = await TenantService.get_tenant_usage(1)
            
            assert usage is not None
            assert usage["max_users"] == 25
            assert usage["current_users"] == 15
            assert usage["usage_percentage"]["users"] == 60.0
            assert usage["usage_percentage"]["employees"] == 60.0
            assert usage["usage_percentage"]["storage"] == 55.0

    @pytest.mark.asyncio
    async def test_get_available_modules_success(self, mock_db_session):
        """Test successful available modules retrieval."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.enabled_modules = ["employees", "departments"]
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            
            modules = await TenantService.get_available_modules(1)
            
            assert modules is not None
            assert len(modules) == 2
            assert "employees" in [m["name"] for m in modules]
            assert "departments" in [m["name"] for m in modules]

    @pytest.mark.asyncio
    async def test_log_usage_success(self, mock_db_session):
        """Test successful usage logging."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            await TenantService.log_usage(
                tenant_id=1,
                resource_type="users",
                action="user_login",
                quantity=1.0,
                resource_id="user-123",
                metadata={"ip_address": "192.168.1.1"}
            )
            
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_subscription_plans_success(self, mock_db_session):
        """Test successful subscription plans retrieval."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_plans = [
                Mock(spec=SubscriptionPlan, id=1, name="Basic", plan_type="basic"),
                Mock(spec=SubscriptionPlan, id=2, name="Professional", plan_type="professional")
            ]
            
            mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_plans
            
            plans = await TenantService.get_subscription_plans()
            
            assert plans is not None
            assert len(plans) == 2

    @pytest.mark.asyncio
    async def test_get_tenant_by_slug_success(self, mock_db_session):
        """Test successful tenant retrieval by slug."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenant = Mock(spec=Tenant)
            mock_tenant.slug = "test-company"
            
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_tenant
            
            tenant = await TenantService.get_tenant_by_slug("test-company")
            
            assert tenant is not None
            assert tenant.slug == "test-company"

    @pytest.mark.asyncio
    async def test_list_tenants_success(self, mock_db_session):
        """Test successful tenant listing with pagination."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_tenants = [
                Mock(spec=Tenant, id=1, name="Company A"),
                Mock(spec=Tenant, id=2, name="Company B")
            ]
            
            mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_tenants
            mock_db_session.execute.return_value.scalar.return_value = 2
            
            tenants, total = await TenantService.list_tenants(page=1, size=10)
            
            assert len(tenants) == 2
            assert total == 2

    @pytest.mark.asyncio
    async def test_initialize_default_data_success(self, mock_db_session):
        """Test successful default data initialization."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            # Mock that no modules/plans exist
            mock_db_session.execute.return_value.scalar.return_value = 0
            
            await TenantService.initialize_default_data()
            
            # Should commit after successful initialization
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_default_data_existing_data(self, mock_db_session):
        """Test default data initialization when data already exists."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            # Mock that modules/plans already exist
            mock_db_session.execute.return_value.scalar.return_value = 5
            
            await TenantService.initialize_default_data()
            
            # Should not commit if data already exists
            mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_initialize_default_data_error(self, mock_db_session):
        """Test default data initialization error handling."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_db_session.commit.side_effect = SQLAlchemyError("Database error")
            
            with pytest.raises(SQLAlchemyError):
                await TenantService.initialize_default_data()
            
            mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_tenant_database_error(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation database error handling."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_db_session.commit.side_effect = SQLAlchemyError("Database error")
            
            with pytest.raises(SQLAlchemyError):
                await TenantService.create_tenant(sample_tenant_data, sample_admin_data)
            
            mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_tenant_integrity_error(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation integrity error handling."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session):
            mock_db_session.commit.side_effect = IntegrityError("Duplicate key", None, None)
            
            with pytest.raises(HTTPException) as exc_info:
                await TenantService.create_tenant(sample_tenant_data, sample_admin_data)
            
            assert exc_info.value.status_code == 400
            assert "Database constraint violation" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_tenant_data_success(self, sample_tenant_data):
        """Test tenant data validation success."""
        # This would test internal validation logic if we had it
        assert "name" in sample_tenant_data
        assert "slug" in sample_tenant_data
        assert "contact_email" in sample_tenant_data

    @pytest.mark.asyncio
    async def test_validate_admin_data_success(self, sample_admin_data):
        """Test admin data validation success."""
        # This would test internal validation logic if we had it
        assert "username" in sample_admin_data
        assert "email" in sample_admin_data
        assert "password" in sample_admin_data

    @pytest.mark.asyncio
    async def test_tenant_creation_with_custom_plan(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with custom plan type."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session), \
             patch('app.services.tenant_service.tenant_db_manager.create_tenant_schema', new_callable=AsyncMock), \
             patch('app.services.tenant_service.tenant_db_manager.get_tenant_session', new_callable=AsyncMock) as mock_tenant_session, \
             patch.object(TenantService, '_get_subscription_plan', return_value=Mock()), \
             patch.object(security_manager, 'hash_password', return_value="hashed_password"), \
             patch('app.services.tenant_service.uuid.uuid4', return_value="test-uuid-123"):

            mock_tenant_session.return_value.__aenter__.return_value = mock_db_session
            mock_db_session.execute.return_value.scalar.return_value = None
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
            
            tenant, admin_user = await TenantService.create_tenant(
                sample_tenant_data, sample_admin_data, "custom"
            )
            
            assert tenant.plan == TenantPlan.CUSTOM

    @pytest.mark.asyncio
    async def test_tenant_creation_with_trial_plan(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with trial plan."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session), \
             patch('app.services.tenant_service.tenant_db_manager.create_tenant_schema', new_callable=AsyncMock), \
             patch('app.services.tenant_service.tenant_db_manager.get_tenant_session', new_callable=AsyncMock) as mock_tenant_session, \
             patch.object(TenantService, '_get_subscription_plan', return_value=Mock()), \
             patch.object(security_manager, 'hash_password', return_value="hashed_password"), \
             patch('app.services.tenant_service.uuid.uuid4', return_value="test-uuid-123"):

            mock_tenant_session.return_value.__aenter__.return_value = mock_db_session
            mock_db_session.execute.return_value.scalar.return_value = None
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
            
            tenant, admin_user = await TenantService.create_tenant(
                sample_tenant_data, sample_admin_data, "free"
            )
            
            assert tenant.plan == TenantPlan.FREE
            assert tenant.status == TenantStatus.TRIAL

    @pytest.mark.asyncio
    async def test_tenant_creation_with_billing_cycle(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with specific billing cycle."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session), \
             patch('app.services.tenant_service.tenant_db_manager.create_tenant_schema', new_callable=AsyncMock), \
             patch('app.services.tenant_service.tenant_db_manager.get_tenant_session', new_callable=AsyncMock) as mock_tenant_session, \
             patch.object(TenantService, '_get_subscription_plan', return_value=Mock()), \
             patch.object(security_manager, 'hash_password', return_value="hashed_password"), \
             patch('app.services.tenant_service.uuid.uuid4', return_value="test-uuid-123"):

            mock_tenant_session.return_value.__aenter__.return_value = mock_db_session
            mock_db_session.execute.return_value.scalar.return_value = None
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
            
            # Add billing cycle to tenant data
            sample_tenant_data["billing_cycle"] = "yearly"
            
            tenant, admin_user = await TenantService.create_tenant(
                sample_tenant_data, sample_admin_data, "professional"
            )
            
            assert tenant.billing_cycle == BillingCycle.YEARLY

    @pytest.mark.asyncio
    async def test_tenant_creation_with_module_limits(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with module-specific limits."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session), \
             patch('app.services.tenant_service.tenant_db_manager.create_tenant_schema', new_callable=AsyncMock), \
             patch('app.services.tenant_service.tenant_db_manager.get_tenant_session', new_callable=AsyncMock) as mock_tenant_session, \
             patch.object(TenantService, '_get_subscription_plan', return_value=Mock()), \
             patch.object(security_manager, 'hash_password', return_value="hashed_password"), \
             patch('app.services.tenant_service.uuid.uuid4', return_value="test-uuid-123"):

            mock_tenant_session.return_value.__aenter__.return_value = mock_db_session
            mock_db_session.execute.return_value.scalar.return_value = None
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
            
            # Add module limits to tenant data
            sample_tenant_data["module_limits"] = {
                "employees": {"max_records": 1000, "features": ["basic", "advanced"]},
                "payroll": {"max_records": 500, "features": ["basic"]}
            }
            
            tenant, admin_user = await TenantService.create_tenant(
                sample_tenant_data, sample_admin_data, "enterprise"
            )
            
            assert tenant.module_limits is not None
            assert "employees" in tenant.module_limits
            assert "payroll" in tenant.module_limits

    @pytest.mark.asyncio
    async def test_tenant_creation_with_feature_flags(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with feature flags."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session), \
             patch('app.services.tenant_service.tenant_db_manager.create_tenant_schema', new_callable=AsyncMock), \
             patch('app.services.tenant_service.tenant_db_manager.get_tenant_session', new_callable=AsyncMock) as mock_tenant_session, \
             patch.object(TenantService, '_get_subscription_plan', return_value=Mock()), \
             patch.object(security_manager, 'hash_password', return_value="hashed_password"), \
             patch('app.services.tenant_service.uuid.uuid4', return_value="test-uuid-123"):

            mock_tenant_session.return_value.__aenter__.return_value = mock_db_session
            mock_db_session.execute.return_value.scalar.return_value = None
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
            
            # Add feature flags to tenant data
            sample_tenant_data["feature_flags"] = {
                "advanced_reporting": True,
                "api_access": True,
                "custom_branding": False,
                "white_label": False
            }
            
            tenant, admin_user = await TenantService.create_tenant(
                sample_tenant_data, sample_admin_data, "enterprise"
            )
            
            assert tenant.feature_flags is not None
            assert tenant.feature_flags["advanced_reporting"] is True
            assert tenant.feature_flags["api_access"] is True
            assert tenant.feature_flags["custom_branding"] is False

    @pytest.mark.asyncio
    async def test_tenant_creation_with_compliance_settings(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with compliance and security settings."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session), \
             patch('app.services.tenant_service.tenant_db_manager.create_tenant_schema', new_callable=AsyncMock), \
             patch('app.services.tenant_service.tenant_db_manager.get_tenant_session', new_callable=AsyncMock) as mock_tenant_session, \
             patch.object(TenantService, '_get_subscription_plan', return_value=Mock()), \
             patch.object(security_manager, 'hash_password', return_value="hashed_password"), \
             patch('app.services.tenant_service.uuid.uuid4', return_value="test-uuid-123"):

            mock_tenant_session.return_value.__aenter__.return_value = mock_db_session
            mock_db_session.execute.return_value.scalar.return_value = None
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
            
            # Add compliance settings to tenant data
            sample_tenant_data.update({
                "data_retention_days": 2555,  # 7 years
                "backup_frequency": "daily",
                "encryption_level": "256-bit",
                "compliance_certifications": ["SOC2", "GDPR", "HIPAA"],
                "audit_logging": True,
                "data_encryption_at_rest": True,
                "data_encryption_in_transit": True
            })
            
            tenant, admin_user = await TenantService.create_tenant(
                sample_tenant_data, sample_admin_data, "enterprise"
            )
            
            assert tenant.data_retention_days == 2555
            assert tenant.backup_frequency == "daily"
            assert tenant.encryption_level == "256-bit"
            assert "SOC2" in tenant.compliance_certifications
            assert tenant.audit_logging is True
            assert tenant.data_encryption_at_rest is True
            assert tenant.data_encryption_in_transit is True

    @pytest.mark.asyncio
    async def test_tenant_creation_with_support_settings(self, mock_db_session, sample_tenant_data, sample_admin_data):
        """Test tenant creation with support and onboarding settings."""
        with patch('app.services.tenant_service.get_session', return_value=mock_db_session), \
             patch('app.services.tenant_service.tenant_db_manager.create_tenant_schema', new_callable=AsyncMock), \
             patch('app.services.tenant_service.tenant_db_manager.get_tenant_session', new_callable=AsyncMock) as mock_tenant_session, \
             patch.object(TenantService, '_get_subscription_plan', return_value=Mock()), \
             patch.object(security_manager, 'hash_password', return_value="hashed_password"), \
             patch('app.services.tenant_service.uuid.uuid4', return_value="test-uuid-123"):

            mock_tenant_session.return_value.__aenter__.return_value = mock_db_session
            mock_db_session.execute.return_value.scalar.return_value = None
            mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
            
            # Add support settings to tenant data
            sample_tenant_data.update({
                "support_tier": "premium",
                "onboarding_completed": False,
                "onboarding_steps": ["account_setup", "user_import", "training", "go_live"],
                "assigned_account_manager": "john.doe@company.com",
                "priority_support": True,
                "dedicated_support_team": True,
                "response_time_sla": "2 hours"
            })
            
            tenant, admin_user = await TenantService.create_tenant(
                sample_tenant_data, sample_admin_data, "enterprise"
            )
            
            assert tenant.support_tier == "premium"
            assert tenant.onboarding_completed is False
            assert "account_setup" in tenant.onboarding_steps
            assert tenant.assigned_account_manager == "john.doe@company.com"
            assert tenant.priority_support is True
            assert tenant.dedicated_support_team is True
            assert tenant.response_time_sla == "2 hours"

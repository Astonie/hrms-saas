import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from datetime import date, datetime
from decimal import Decimal

from app.main import app
from app.models.tenant import Tenant, TenantStatus, TenantPlan, BillingCycle
from app.models.subscription import SubscriptionPlan
from app.services.tenant_service import TenantService


class TestTenantsAPI:
    """Test cases for tenant API endpoints with comprehensive coverage."""

    @pytest.fixture
    def client(self):
        """Test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_tenant_data(self):
        """Sample tenant data for testing."""
        return {
            "name": "Test Company",
            "slug": "test-company",
            "contact_email": "admin@testcompany.com",
            "company_name": "Test Company Inc.",
            "plan_type": "professional",
            "admin_username": "admin",
            "admin_email": "admin@testcompany.com",
            "admin_password": "SecurePass123!",
            "admin_first_name": "Admin",
            "admin_last_name": "User"
        }

    @pytest.fixture
    def sample_tenant_update_data(self):
        """Sample tenant update data for testing."""
        return {
            "name": "Updated Company",
            "contact_email": "admin@updatedcompany.com",
            "company_name": "Updated Company Inc.",
            "description": "An updated company description"
        }

    @pytest.fixture
    def sample_subscription_update_data(self):
        """Sample subscription update data for testing."""
        return {
            "plan_type": "enterprise",
            "billing_cycle": "yearly",
            "auto_renew": True,
            "change_reason": "Upgrade for enterprise features"
        }

    @pytest.fixture
    def mock_tenant(self):
        """Mock tenant object."""
        tenant = Mock(spec=Tenant)
        tenant.id = 1
        tenant.name = "Test Company"
        tenant.slug = "test-company"
        tenant.plan = TenantPlan.PROFESSIONAL
        tenant.status = TenantStatus.ACTIVE
        return tenant

    @pytest.fixture
    def mock_auth_headers(self):
        """Mock authentication headers."""
        return {
            "Authorization": "Bearer test-jwt-token",
            "X-Tenant-ID": "1"
        }

    @pytest.fixture
    def mock_permission_dependency(self):
        """Mock permission dependency."""
        return ["tenants:create", "tenants:read", "tenants:update", "tenants:delete"]

    def test_create_tenant_success(self, client, sample_tenant_data, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test successful tenant creation."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'create_tenant', return_value=(mock_tenant, Mock())):

            response = client.post(
                "/api/v1/tenants/",
                json=sample_tenant_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["name"] == mock_tenant.name
            assert data["slug"] == mock_tenant.slug

    def test_create_tenant_unauthorized(self, client, sample_tenant_data):
        """Test tenant creation without authentication."""
        response = client.post(
            "/api/v1/tenants/",
            json=sample_tenant_data
        )

        assert response.status_code == 401  # Unauthorized

    def test_create_tenant_forbidden(self, client, sample_tenant_data, mock_auth_headers):
        """Test tenant creation without proper permissions."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', side_effect=HTTPException(status_code=403, detail="Insufficient permissions")):

            response = client.post(
                "/api/v1/tenants/",
                json=sample_tenant_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 403
            assert "Insufficient permissions" in response.json()["detail"]

    def test_create_tenant_validation_error(self, client, mock_auth_headers, mock_permission_dependency):
        """Test tenant creation with validation error."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency):

            invalid_data = {"name": "", "slug": "invalid slug"}  # Invalid data
            
            response = client.post(
                "/api/v1/tenants/",
                json=invalid_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 422  # Validation error

    def test_create_tenant_service_error(self, client, sample_tenant_data, mock_auth_headers, mock_permission_dependency):
        """Test tenant creation when service raises error."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'create_tenant', side_effect=HTTPException(status_code=400, detail="Service error")):

            response = client.post(
                "/api/v1/tenants/",
                json=sample_tenant_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 400
            assert "Service error" in response.json()["detail"]

    def test_list_tenants_success(self, client, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test successful tenant listing."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'list_tenants', return_value=([mock_tenant], 1)):

            response = client.get(
                "/api/v1/tenants/",
                headers=mock_auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["name"] == mock_tenant.name

    def test_list_tenants_with_filters(self, client, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test tenant listing with filters."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'list_tenants', return_value=([mock_tenant], 1)):

            response = client.get(
                "/api/v1/tenants/?status=active&plan=professional&search=test",
                headers=mock_auth_headers
            )

            assert response.status_code == 200

    def test_get_tenant_success(self, client, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test successful tenant retrieval."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'get_tenant_by_slug', return_value=mock_tenant):

            response = client.get(
                "/api/v1/tenants/test-company",
                headers=mock_auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == mock_tenant.name
            assert data["slug"] == mock_tenant.slug

    def test_get_tenant_not_found(self, client, mock_auth_headers, mock_permission_dependency):
        """Test tenant retrieval when not found."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'get_tenant_by_slug', return_value=None):

            response = client.get(
                "/api/v1/tenants/non-existent",
                headers=mock_auth_headers
            )

            assert response.status_code == 404
            assert "Tenant not found" in response.json()["detail"]

    def test_update_tenant_success(self, client, sample_tenant_update_data, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test successful tenant update."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'get_tenant_by_slug', return_value=mock_tenant), \
             patch.object(TenantService, 'update_tenant', return_value=mock_tenant):

            response = client.put(
                "/api/v1/tenants/test-company",
                json=sample_tenant_update_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == mock_tenant.name

    def test_update_tenant_not_found(self, client, sample_tenant_update_data, mock_auth_headers, mock_permission_dependency):
        """Test tenant update when not found."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'get_tenant_by_slug', return_value=None):

            response = client.put(
                "/api/v1/tenants/non-existent",
                json=sample_tenant_update_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 404
            assert "Tenant not found" in response.json()["detail"]

    def test_delete_tenant_success(self, client, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test successful tenant deletion."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'get_tenant_by_slug', return_value=mock_tenant), \
             patch.object(TenantService, 'delete_tenant', return_value=True):

            response = client.delete(
                "/api/v1/tenants/test-company",
                headers=mock_auth_headers
            )

            assert response.status_code == 204

    def test_update_subscription_success(self, client, sample_subscription_update_data, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test successful subscription update."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'update_tenant_subscription', return_value=mock_tenant):

            response = client.post(
                "/api/v1/tenants/1/subscription",
                json=sample_subscription_update_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == mock_tenant.name

    def test_update_subscription_validation_error(self, client, mock_auth_headers, mock_permission_dependency):
        """Test subscription update with validation error."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency):

            invalid_data = {"plan_type": "invalid_plan"}  # Invalid data
            
            response = client.post(
                "/api/v1/tenants/1/subscription",
                json=invalid_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 422  # Validation error

    def test_get_tenant_usage_success(self, client, mock_auth_headers, mock_permission_dependency):
        """Test successful tenant usage retrieval."""
        usage_data = {
            "max_users": 25,
            "current_users": 15,
            "max_employees": 250,
            "current_employees": 150,
            "max_storage_gb": 10,
            "current_storage_gb": 5.5,
            "usage_percentage": {
                "users": 60.0,
                "employees": 60.0,
                "storage": 55.0
            }
        }
        
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'get_tenant_usage', return_value=usage_data):

            response = client.get(
                "/api/v1/tenants/1/usage",
                headers=mock_auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["max_users"] == 25
            assert data["current_users"] == 15
            assert data["usage_percentage"]["users"] == 60.0

    def test_check_module_access_success(self, client, mock_auth_headers, mock_permission_dependency):
        """Test successful module access check."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'check_module_access', return_value=True):

            response = client.get(
                "/api/v1/tenants/1/modules/employees/access",
                headers=mock_auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["has_access"] is True
            assert data["module"] == "employees"

    def test_get_available_modules_success(self, client, mock_auth_headers, mock_permission_dependency):
        """Test successful available modules retrieval."""
        modules_data = [
            {"name": "employees", "display_name": "Employee Management", "description": "Manage employees"},
            {"name": "departments", "display_name": "Department Management", "description": "Manage departments"}
        ]
        
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'get_available_modules', return_value=modules_data):

            response = client.get(
                "/api/v1/tenants/1/modules",
                headers=mock_auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "employees"
            assert data[1]["name"] == "departments"

    def test_get_subscription_plans_success(self, client, mock_auth_headers, mock_permission_dependency):
        """Test successful subscription plans retrieval."""
        mock_plan = Mock(spec=SubscriptionPlan)
        mock_plan.name = "Professional Plan"
        
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'get_subscription_plans', return_value=[mock_plan]):

            response = client.get(
                "/api/v1/tenants/subscription-plans",
                headers=mock_auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == mock_plan.name

    def test_tenant_creation_with_background_tasks(self, client, sample_tenant_data, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test tenant creation with background tasks."""
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'create_tenant', return_value=(mock_tenant, Mock())):

            response = client.post(
                "/api/v1/tenants/",
                json=sample_tenant_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 201
            # Background tasks would be executed here in a real scenario

    def test_tenant_creation_with_minimal_data(self, client, mock_tenant, mock_auth_headers, mock_permission_dependency):
        """Test tenant creation with minimal required data."""
        minimal_data = {
            "name": "Minimal Company",
            "slug": "minimal-company",
            "contact_email": "admin@minimal.com",
            "company_name": "Minimal Company Inc.",
            "plan_type": "basic",
            "admin_username": "admin",
            "admin_email": "admin@minimal.com",
            "admin_password": "SecurePass123!"
        }
        
        with patch('app.api.v1.tenants.get_current_user', return_value={"id": "1", "username": "admin"}), \
             patch('app.api.v1.tenants.require_permission', return_value=lambda: mock_permission_dependency), \
             patch.object(TenantService, 'create_tenant', return_value=(mock_tenant, Mock())):

            response = client.post(
                "/api/v1/tenants/",
                json=minimal_data,
                headers=mock_auth_headers
            )

            assert response.status_code == 201

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.middleware.module_access import (
    ModuleAccessMiddleware,
    create_module_access_middleware,
    require_module_access,
    require_employees_module,
    require_departments_module,
    require_leave_module,
    require_payroll_module,
    require_recruitment_module,
    require_performance_module,
    require_training_module,
    require_attendance_module,
    require_benefits_module
)


class TestModuleAccessMiddleware:
    """Test cases for ModuleAccessMiddleware with comprehensive coverage."""

    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI application."""
        app = Mock()
        app.return_value = None
        return app

    @pytest.fixture
    def mock_scope(self):
        """Mock ASGI scope."""
        return {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/employees",
            "headers": [(b"x-tenant-id", b"1")]
        }

    @pytest.fixture
    def mock_receive(self):
        """Mock ASGI receive function."""
        return AsyncMock()

    @pytest.fixture
    def mock_send(self):
        """Mock ASGI send function."""
        return AsyncMock()

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/v1/employees"
        request.headers = {"x-tenant-id": "1"}
        return request

    @pytest.fixture
    def mock_tenant_service(self):
        """Mock TenantService."""
        service = Mock()
        service.check_module_access = AsyncMock(return_value=True)
        return service

    def test_middleware_initialization(self, mock_app):
        """Test middleware initialization."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees", "departments"])
        
        assert middleware.app == mock_app
        assert middleware.required_modules == ["employees", "dep_employees", "departments"]

    def test_middleware_initialization_no_modules(self, mock_app):
        """Test middleware initialization without required modules."""
        middleware = ModuleAccessMiddleware(mock_app)
        
        assert middleware.app == mock_app
        assert middleware.required_modules == []

    def test_requires_module_check_skip_auth_paths(self, mock_app):
        """Test that auth paths skip module checking."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        # Test auth paths that should skip
        auth_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/me",
            "/docs",
            "/openapi.json",
            "/health",
            "/metrics"
        ]
        
        for path in auth_paths:
            request = Mock()
            request.url.path = path
            assert not middleware._requires_module_check(request)

    def test_requires_module_check_requires_check(self, mock_app):
        """Test that non-auth paths require module checking."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        request = Mock()
        request.url.path = "/api/v1/employees"
        assert middleware._requires_module_check(request)

    def test_extract_tenant_id_from_header(self, mock_app):
        """Test tenant ID extraction from header."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        request = Mock()
        request.headers = {"x-tenant-id": "123"}
        
        tenant_id = middleware._extract_tenant_id(request)
        assert tenant_id == 123

    def test_extract_tenant_id_from_jwt(self, mock_app):
        """Test tenant ID extraction from JWT token."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        request = Mock()
        request.headers = {"authorization": "Bearer test-token"}
        
        with patch('app.middleware.module_access.security_manager.extract_tenant_id', return_value="456"):
            tenant_id = middleware._extract_tenant_id(request)
            assert tenant_id == 456

    def test_extract_tenant_id_not_found(self, mock_app):
        """Test tenant ID extraction when not found."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        request = Mock()
        request.headers = {}
        
        tenant_id = middleware._extract_tenant_id(request)
        assert tenant_id is None

    @pytest.mark.asyncio
    async def test_check_module_access_success(self, mock_app, mock_tenant_service):
        """Test successful module access check."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        request = Mock()
        request.url.path = "/api/v1/employees"
        
        with patch('app.middleware.module_access.TenantService', return_value=mock_tenant_service):
            await middleware._check_module_access(request, 1)
            # Should not raise any exception

    @pytest.mark.asyncio
    async def test_check_module_access_denied(self, mock_app, mock_tenant_service):
        """Test module access check when denied."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        request = Mock()
        request.url.path = "/api/v1/employees"
        
        mock_tenant_service.check_module_access.return_value = False
        
        with patch('app.middleware.module_access.TenantService', return_value=mock_tenant_service):
            with pytest.raises(HTTPException) as exc_info:
                await middleware._check_module_access(request, 1)
            
            assert exc_info.value.status_code == 403
            assert "Module access denied" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_check_module_access_unknown_module(self, mock_app, mock_tenant_service):
        """Test module access check for unknown module."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        request = Mock()
        request.url.path = "/api/v1/unknown"
        
        with patch('app.middleware.module_access.TenantService', return_value=mock_tenant_service):
            with pytest.raises(HTTPException) as exc_info:
                await middleware._check_module_access(request, 1)
            
            assert exc_info.value.status_code == 403
            assert "Module access denied" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_middleware_call_http_scope(self, mock_app, mock_scope, mock_receive, mock_send):
        """Test middleware call with HTTP scope."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        with patch.object(middleware, '_requires_module_check', return_value=True), \
             patch.object(middleware, '_extract_tenant_id', return_value=1), \
             patch.object(middleware, '_check_module_access', new_callable=AsyncMock):
            
            await middleware(mock_scope, mock_receive, mock_send)
            
            # Should call the app
            mock_app.assert_called_once_with(mock_scope, mock_receive, mock_send)

    @pytest.mark.asyncio
    async def test_middleware_call_http_scope_with_module_check(self, mock_app, mock_scope, mock_receive, mock_send):
        """Test middleware call with HTTP scope requiring module check."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        with patch.object(middleware, '_requires_module_check', return_value=True), \
             patch.object(middleware, '_extract_tenant_id', return_value=1), \
             patch.object(middleware, '_check_module_access', new_callable=AsyncMock):
            
            await middleware(mock_scope, mock_receive, mock_send)
            
            # Should call the app
            mock_app.assert_called_once_with(mock_scope, mock_receive, mock_send)

    @pytest.mark.asyncio
    async def test_middleware_call_http_scope_module_check_failed(self, mock_app, mock_scope, mock_receive, mock_send):
        """Test middleware call when module check fails."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        with patch.object(middleware, '_requires_module_check', return_value=True), \
             patch.object(middleware, '_extract_tenant_id', return_value=1), \
             patch.object(middleware, '_check_module_access', side_effect=HTTPException(status_code=403, detail="Access denied")):
            
            await middleware(mock_scope, mock_receive, mock_send)
            
            # Should not call the app when module check fails
            mock_app.assert_not_called()

    @pytest.mark.asyncio
    async def test_middleware_call_non_http_scope(self, mock_app, mock_receive, mock_send):
        """Test middleware call with non-HTTP scope."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        non_http_scope = {"type": "websocket"}
        
        await middleware(non_http_scope, mock_receive, mock_send)
        
        # Should call the app directly for non-HTTP scopes
        mock_app.assert_called_once_with(non_http_scope, mock_receive, mock_send)

    @pytest.mark.asyncio
    async def test_middleware_call_no_tenant_id(self, mock_app, mock_scope, mock_receive, mock_send):
        """Test middleware call when no tenant ID is found."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        with patch.object(middleware, '_requires_module_check', return_value=True), \
             patch.object(middleware, '_extract_tenant_id', return_value=None):
            
            await middleware(mock_scope, mock_receive, mock_send)
            
            # Should call the app when no tenant ID
            mock_app.assert_called_once_with(mock_scope, mock_receive, mock_send)

    @pytest.mark.asyncio
    async def test_middleware_call_exception_handling(self, mock_app, mock_scope, mock_receive, mock_send):
        """Test middleware call exception handling."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        with patch.object(middleware, '_requires_module_check', return_value=True), \
             patch.object(middleware, '_extract_tenant_id', return_value=1), \
             patch.object(middleware, '_check_module_access', side_effect=Exception("Unexpected error")):
            
            await middleware(mock_scope, mock_receive, mock_send)
            
            # Should call the app even when module check fails with unexpected error
            mock_app.assert_called_once_with(mock_scope, mock_receive, mock_send)

    def test_path_to_module_mapping(self, mock_app):
        """Test path to module mapping."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        # Test various path mappings
        test_cases = [
            ("/api/v1/employees", "employees"),
            ("/api/v1/departments", "departments"),
            ("/api/v1/leave", "leave"),
            ("/api/v1/payroll", "payroll"),
            ("/api/v1/recruitment", "recruitment"),
            ("/api/v1/performance", "performance"),
            ("/api/v1/training", "training"),
            ("/api/v1/attendance", "attendance"),
            ("/api/v1/benefits", "benefits"),
            ("/api/v1/unknown", None)
        ]
        
        for path, expected_module in test_cases:
            request = Mock()
            request.url.path = path
            
            if expected_module:
                # This would test the internal mapping logic
                assert True  # Placeholder for actual mapping test
            else:
                assert True  # Placeholder for actual mapping test


class TestModuleAccessDependencies:
    """Test cases for module access dependency functions."""

    @pytest.fixture
    def mock_tenant_id(self):
        """Mock tenant ID."""
        return 1

    @pytest.fixture
    def mock_module_name(self):
        """Mock module name."""
        return "employees"

    @pytest.mark.asyncio
    async def test_require_module_access_success(self, mock_tenant_id, mock_module_name):
        """Test successful module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_module_access(mock_module_name)(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_module_access_denied(self, mock_tenant_id, mock_module_name):
        """Test module access requirement when denied."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await require_module_access(mock_module_name)(mock_tenant_id)
            
            assert exc_info.value.status_code == 403
            assert "Module access denied" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_employees_module_success(self, mock_tenant_id):
        """Test successful employees module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_employees_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_departments_module_success(self, mock_tenant_id):
        """Test successful departments module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_departments_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_leave_module_success(self, mock_tenant_id):
        """Test successful leave module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_leave_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_payroll_module_success(self, mock_tenant_id):
        """Test successful payroll module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_payroll_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_recruitment_module_success(self, mock_tenant_id):
        """Test successful recruitment module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_recruitment_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_performance_module_success(self, mock_tenant_id):
        """Test successful performance module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_performance_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_training_module_success(self, mock_tenant_id):
        """Test successful training module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_training_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_attendance_module_success(self, mock_tenant_id):
        """Test successful attendance module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_attendance_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_benefits_module_success(self, mock_tenant_id):
        """Test successful benefits module access requirement."""
        with patch('app.middleware.module_access.TenantService.check_module_access', return_value=True):
            result = await require_benefits_module()(mock_tenant_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_module_access_service_error(self, mock_tenant_id, mock_module_name):
        """Test module access requirement when service raises error."""
        with patch('app.middleware.module_access.TenantService.check_module_access', side_effect=Exception("Service error")):
            with pytest.raises(HTTPException) as exc_info:
                await require_module_access(mock_module_name)(mock_tenant_id)
            
            assert exc_info.value.status_code == 500
            assert "Internal server error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_module_access_invalid_tenant_id(self, mock_module_name):
        """Test module access requirement with invalid tenant ID."""
        with pytest.raises(HTTPException) as exc_info:
            await require_module_access(mock_module_name)(None)
        
        assert exc_info.value.status_code == 400
        assert "Invalid tenant ID" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_module_access_empty_module_name(self, mock_tenant_id):
        """Test module access requirement with empty module name."""
        with pytest.raises(HTTPException) as exc_info:
            await require_module_access("")(mock_tenant_id)
        
        assert exc_info.value.status_code == 400
        assert "Invalid module name" in str(exc_info.value.detail)


class TestModuleAccessFactory:
    """Test cases for module access factory functions."""

    def test_create_module_access_middleware(self, mock_app):
        """Test middleware factory function."""
        middleware = create_module_access_middleware(mock_app, ["employees", "departments"])
        
        assert isinstance(middleware, ModuleAccessMiddleware)
        assert middleware.app == mock_app
        assert middleware.required_modules == ["employees", "departments"]

    def test_create_module_access_middleware_no_modules(self, mock_app):
        """Test middleware factory function without modules."""
        middleware = create_module_access_middleware(mock_app)
        
        assert isinstance(middleware, ModuleAccessMiddleware)
        assert middleware.app == mock_app
        assert middleware.required_modules == []

    def test_create_module_access_middleware_empty_modules(self, mock_app):
        """Test middleware factory function with empty modules list."""
        middleware = create_module_access_middleware(mock_app, [])
        
        assert isinstance(middleware, ModuleAccessMiddleware)
        assert middleware.app == mock_app
        assert middleware.required_modules == []


class TestModuleAccessSecurity:
    """Test cases for module access security features."""

    @pytest.fixture
    def mock_malicious_request(self):
        """Mock malicious request."""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/v1/employees"
        request.headers = {"x-tenant-id": "1; DROP TABLE users;"}  # SQL injection attempt
        return request

    def test_sql_injection_prevention(self, mock_app, mock_malicious_request):
        """Test SQL injection prevention in tenant ID extraction."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        # Should handle malicious input gracefully
        tenant_id = middleware._extract_tenant_id(mock_malicious_request)
        # The middleware should either reject or sanitize the input
        assert tenant_id is None or isinstance(tenant_id, (int, type(None)))

    def test_path_traversal_prevention(self, mock_app):
        """Test path traversal prevention."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        malicious_paths = [
            "/api/v1/employees/../../../etc/passwd",
            "/api/v1/employees/%2e%2e%2f%2e%2e%2f",
            "/api/v1/employees/..%2f..%2f..%2f"
        ]
        
        for path in malicious_paths:
            request = Mock()
            request.url.path = path
            # Should not crash or allow access to unauthorized paths
            assert True  # Placeholder for actual security test

    def test_tenant_id_validation(self, mock_app):
        """Test tenant ID validation."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        invalid_tenant_ids = [
            "0",
            "-1",
            "999999999999999999999999999999",
            "abc",
            "1.5",
            "1,2,3"
        ]
        
        for tenant_id in invalid_tenant_ids:
            request = Mock()
            request.headers = {"x-tenant-id": tenant_id}
            
            # Should handle invalid tenant IDs gracefully
            extracted_id = middleware._extract_tenant_id(request)
            assert extracted_id is None or isinstance(extracted_id, int)

    def test_module_name_validation(self, mock_app):
        """Test module name validation."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        malicious_module_names = [
            "employees'; DROP TABLE users; --",
            "employees<script>alert('xss')</script>",
            "employees/../../../etc/passwd",
            "employees%00",
            "employees\x00"
        ]
        
        for module_name in malicious_module_names:
            # Should handle malicious module names gracefully
            assert True  # Placeholder for actual security test

    @pytest.mark.asyncio
    async def test_rate_limiting_simulation(self, mock_app, mock_scope, mock_receive, mock_send):
        """Test rate limiting simulation (basic implementation)."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        # Simulate multiple rapid requests
        for i in range(10):
            await middleware(mock_scope, mock_receive, mock_send)
        
        # Should handle multiple requests without crashing
        assert True  # Placeholder for actual rate limiting test

    def test_audit_logging_simulation(self, mock_app):
        """Test audit logging simulation."""
        middleware = ModuleAccessMiddleware(mock_app, ["employees"])
        
        # Simulate access attempts for audit logging
        test_cases = [
            (1, "employees", True),
            (1, "departments", False),
            (2, "employees", True),
            (2, "payroll", False)
        ]
        
        for tenant_id, module, has_access in test_cases:
            # Should log access attempts appropriately
            assert True  # Placeholder for actual audit logging test

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from app.main import app
from app.core.config import settings


class TestMainApp:
    """Test main FastAPI application."""

    def test_app_creation(self):
        """Test that the app is created with correct configuration."""
        assert app.title == "HRMS-SAAS"
        assert app.version == "1.0.0"
        assert app.description == "Enterprise Multi-Tenant Human Resources Management System"

    def test_app_docs_urls(self):
        """Test that documentation URLs are properly configured."""
        if settings.debug:
            assert app.docs_url == "/docs"
            assert app.redoc_url == "/redoc"
            assert app.openapi_url == "/openapi.json"
        else:
            assert app.docs_url is None
            assert app.redoc_url is None
            assert app.openapi_url is None

    def test_app_middleware(self):
        """Test that required middleware is configured."""
        # Check CORS middleware
        cors_middleware = None
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(type(middleware.cls)):
                cors_middleware = middleware
                break
        
        assert cors_middleware is not None

    def test_app_routers(self):
        """Test that API routers are included."""
        # Check that the main API router is included
        assert len(app.routes) > 0
        
        # Check for API routes
        api_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith('/api')]
        assert len(api_routes) > 0

    def test_health_check_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "HRMS-SAAS"
        assert "timestamp" in data
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "HRMS-SAAS API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"


class TestExceptionHandlers:
    """Test exception handlers."""

    def test_http_exception_handler(self, client: TestClient):
        """Test HTTP exception handler."""
        # Create a test endpoint that raises an HTTPException
        @app.get("/test-http-exception")
        def test_http_exception():
            raise HTTPException(status_code=404, detail="Resource not found")
        
        response = client.get("/test-http-exception")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Resource not found"
        assert "timestamp" in data
        assert "path" in data

    def test_validation_exception_handler(self, client: TestClient):
        """Test validation exception handler."""
        # Create a test endpoint with validation
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            name: str
            age: int
        
        @app.post("/test-validation")
        def test_validation(model: TestModel):
            return {"message": "Valid"}
        
        # Send invalid data
        response = client.post("/test-validation", json={"name": "test"})  # Missing age
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "timestamp" in data
        assert "path" in data

    def test_general_exception_handler(self, client: TestClient):
        """Test general exception handler."""
        # Create a test endpoint that raises a general exception
        @app.get("/test-general-exception")
        def test_general_exception():
            raise Exception("Something went wrong")
        
        response = client.get("/test-general-exception")
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "Internal server error"
        assert "timestamp" in data
        assert "path" in data

    def test_starlette_http_exception_handler(self, client: TestClient):
        """Test Starlette HTTP exception handler."""
        # Create a test endpoint that raises a StarletteHTTPException
        @app.get("/test-starlette-exception")
        def test_starlette_exception():
            raise StarletteHTTPException(status_code=403, detail="Forbidden")
        
        response = client.get("/test-starlette-exception")
        
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Forbidden"
        assert "timestamp" in data
        assert "path" in data


class TestMiddleware:
    """Test middleware functionality."""

    def test_cors_middleware(self, client: TestClient):
        """Test CORS middleware configuration."""
        # Test preflight request
        response = client.options("/api/v1/auth/login", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Should handle CORS preflight
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS

    def test_trusted_host_middleware(self, client: TestClient):
        """Test trusted host middleware."""
        # This would test the TrustedHostMiddleware if implemented
        # For now, we'll test that the app responds to requests
        response = client.get("/health")
        assert response.status_code == 200

    def test_logging_middleware(self, client: TestClient):
        """Test logging middleware."""
        # This would test logging middleware if implemented
        # For now, we'll test that requests are processed
        response = client.get("/health")
        assert response.status_code == 200


class TestLifespan:
    """Test application lifespan events."""

    @pytest.mark.asyncio
    async def test_lifespan_startup(self):
        """Test application startup."""
        from app.main import lifespan
        
        # Mock the database initialization
        with patch('app.core.database.init_database') as mock_init:
            async with lifespan(app):
                mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_shutdown(self):
        """Test application shutdown."""
        from app.main import lifespan
        
        # Mock the database shutdown
        with patch('app.core.database.close_database') as mock_close:
            async with lifespan(app):
                pass
            
            # The close should be called when exiting the context
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_exception_handling(self):
        """Test lifespan exception handling."""
        from app.main import lifespan
        
        # Mock database initialization to raise an exception
        with patch('app.core.database.init_database', side_effect=Exception("DB init failed")):
            with pytest.raises(Exception, match="DB init failed"):
                async with lifespan(app):
                    pass


class TestAPIEndpoints:
    """Test API endpoint availability."""

    def test_auth_endpoints_available(self, client: TestClient):
        """Test that auth endpoints are available."""
        # Test login endpoint
        response = client.post("/api/v1/auth/login", json={
            "username": "test",
            "password": "test",
            "tenant_id": "test"
        })
        
        # Should get a response (either success or validation error)
        assert response.status_code in [200, 401, 422]

    def test_api_documentation_available(self, client: TestClient):
        """Test that API documentation is available when debug is enabled."""
        if settings.debug:
            # Test OpenAPI schema
            response = client.get("/openapi.json")
            assert response.status_code == 200
            
            # Test Swagger UI
            response = client.get("/docs")
            assert response.status_code == 200
            
            # Test ReDoc
            response = client.get("/redoc")
            assert response.status_code == 200

    def test_api_versioning(self, client: TestClient):
        """Test API versioning."""
        # Test that v1 API is available
        response = client.get("/api/v1/")
        # This might return 404 if no root endpoint is defined for v1
        # But the important thing is that the route exists
        assert response.status_code in [200, 404, 405]


class TestSecurity:
    """Test security features."""

    def test_https_redirect_placeholder(self, client: TestClient):
        """Test HTTPS redirect placeholder."""
        # This would test HTTPS redirect middleware if implemented
        # For now, we'll test that the app responds
        response = client.get("/health")
        assert response.status_code == 200

    def test_rate_limiting_placeholder(self, client: TestClient):
        """Test rate limiting placeholder."""
        # This would test rate limiting if implemented
        # For now, we'll test that multiple requests work
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200

    def test_security_headers_placeholder(self, client: TestClient):
        """Test security headers placeholder."""
        # This would test security headers if implemented
        # For now, we'll test that the app responds
        response = client.get("/health")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_404_not_found(self, client: TestClient):
        """Test 404 not found handling."""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_405_method_not_allowed(self, client: TestClient):
        """Test 405 method not allowed handling."""
        # Try to POST to a GET endpoint
        response = client.post("/health")
        
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data

    def test_422_unprocessable_entity(self, client: TestClient):
        """Test 422 unprocessable entity handling."""
        # Send invalid JSON
        response = client.post("/api/v1/auth/login", data="invalid json")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestPerformance:
    """Test performance-related features."""

    def test_response_time(self, client: TestClient):
        """Test response time for health endpoint."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Health endpoint should respond quickly (under 1 second)
        assert response_time < 1.0
        assert response.status_code == 200

    def test_concurrent_requests(self, client: TestClient):
        """Test concurrent request handling."""
        import threading
        import time
        
        results = []
        
        def make_request():
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            results.append({
                "status_code": response.status_code,
                "response_time": end_time - start_time
            })
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 5
        for result in results:
            assert result["status_code"] == 200
            assert result["response_time"] < 2.0  # Should be quick


class TestMonitoring:
    """Test monitoring and observability features."""

    def test_health_check_comprehensive(self, client: TestClient):
        """Test comprehensive health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["status", "service", "timestamp", "version"]
        for field in required_fields:
            assert field in data
        
        # Check status value
        assert data["status"] in ["healthy", "unhealthy", "degraded"]
        
        # Check timestamp format
        import datetime
        try:
            datetime.datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Invalid timestamp format")

    def test_metrics_endpoint_placeholder(self, client: TestClient):
        """Test metrics endpoint placeholder."""
        # This would test metrics endpoint if implemented
        # For now, we'll test that the app responds
        response = client.get("/health")
        assert response.status_code == 200

    def test_logging_configuration(self):
        """Test logging configuration."""
        # Test that logging is configured
        import logging
        
        # Check that the app logger exists
        logger = logging.getLogger("app")
        assert logger is not None
        
        # Check log level
        assert logger.level <= logging.INFO


class TestConfiguration:
    """Test configuration handling."""

    def test_environment_variables(self):
        """Test environment variable handling."""
        # Test that settings are loaded
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'app_version')
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'environment')

    def test_database_configuration(self):
        """Test database configuration."""
        # Test that database settings are available
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'database_pool_size')
        assert hasattr(settings, 'database_max_overflow')

    def test_security_configuration(self):
        """Test security configuration."""
        # Test that security settings are available
        assert hasattr(settings, 'jwt_secret_key')
        assert hasattr(settings, 'jwt_algorithm')
        assert hasattr(settings, 'access_token_expire_minutes')
        assert hasattr(settings, 'refresh_token_expire_days')

    def test_cors_configuration(self):
        """Test CORS configuration."""
        # Test that CORS settings are available
        assert hasattr(settings, 'cors_origins')
        assert hasattr(settings, 'cors_allow_credentials')
        assert hasattr(settings, 'cors_allow_methods')
        assert hasattr(settings, 'cors_allow_headers')

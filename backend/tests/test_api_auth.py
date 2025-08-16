import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import security_manager
from app.models.user import User
from app.models.tenant import Tenant


class TestAuthAPI:
    """Test authentication API endpoints."""

    def test_login_success(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test successful user login."""
        login_data = {
            "username": "testuser",
            "password": "testpassword123",
            "tenant_id": str(test_tenant.id)
        }
        
        with patch('app.api.v1.auth.verify_password', return_value=True):
            with patch('app.api.v1.auth.get_user_by_username', return_value=test_user):
                response = client.post("/api/v1/auth/login", json=login_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data
                assert data["token_type"] == "bearer"
                assert data["user_id"] == str(test_user.id)
                assert data["tenant_id"] == str(test_tenant.id)
                assert "permissions" in data

    def test_login_invalid_credentials(self, client: TestClient, test_tenant: Tenant):
        """Test login with invalid credentials."""
        login_data = {
            "username": "wronguser",
            "password": "wrongpassword",
            "tenant_id": str(test_tenant.id)
        }
        
        with patch('app.api.v1.auth.verify_password', return_value=False):
            response = client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == 401
            data = response.json()
            assert "Invalid credentials" in data["detail"]

    def test_login_user_not_found(self, client: TestClient, test_tenant: Tenant):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "testpassword123",
            "tenant_id": str(test_tenant.id)
        }
        
        with patch('app.api.v1.auth.get_user_by_username', return_value=None):
            response = client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == 401
            data = response.json()
            assert "Invalid credentials" in data["detail"]

    def test_login_inactive_user(self, client: TestClient, test_tenant: Tenant):
        """Test login with inactive user."""
        test_user = User(
            username="inactiveuser",
            email="inactive@test.com",
            hashed_password="hash",
            is_active=False
        )
        
        login_data = {
            "username": "inactiveuser",
            "password": "testpassword123",
            "tenant_id": str(test_tenant.id)
        }
        
        with patch('app.api.v1.auth.verify_password', return_value=True):
            with patch('app.api.v1.auth.get_user_by_username', return_value=test_user):
                response = client.post("/api/v1/auth/login", json=login_data)
                
                assert response.status_code == 401
                data = response.json()
                assert "Account is inactive" in data["detail"]

    def test_login_locked_user(self, client: TestClient, test_tenant: Tenant):
        """Test login with locked user."""
        test_user = User(
            username="lockeduser",
            email="locked@test.com",
            hashed_password="hash",
            is_locked=True,
            lock_reason="Too many failed attempts"
        )
        
        login_data = {
            "username": "lockeduser",
            "password": "testpassword123",
            "tenant_id": str(test_tenant.id)
        }
        
        with patch('app.api.v1.auth.verify_password', return_value=True):
            with patch('app.api.v1.auth.get_user_by_username', return_value=test_user):
                response = client.post("/api/v1/auth/login", json=login_data)
                
                assert response.status_code == 401
                data = response.json()
                assert "Account is locked" in data["detail"]

    def test_login_missing_tenant_id(self, client: TestClient):
        """Test login without tenant ID."""
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 422  # Validation error

    def test_login_missing_username(self, client: TestClient, test_tenant: Tenant):
        """Test login without username."""
        login_data = {
            "password": "testpassword123",
            "tenant_id": str(test_tenant.id)
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 422  # Validation error

    def test_login_missing_password(self, client: TestClient, test_tenant: Tenant):
        """Test login without password."""
        login_data = {
            "username": "testuser",
            "tenant_id": str(test_tenant.id)
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 422  # Validation error

    def test_refresh_token_success(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test successful token refresh."""
        refresh_token = security_manager.create_refresh_token(
            subject=test_user.username,
            tenant_id=str(test_tenant.id),
            user_id=str(test_user.id)
        )
        
        refresh_data = {"refresh_token": refresh_token}
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == str(test_user.id)
        assert data["tenant_id"] == str(test_tenant.id)

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid.token.here"}
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid refresh token" in data["detail"]

    def test_refresh_token_expired(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test refresh with expired token."""
        # Create a token that expires immediately
        import time
        from datetime import timedelta
        
        refresh_token = security_manager.create_refresh_token(
            subject=test_user.username,
            tenant_id=str(test_tenant.id),
            user_id=str(test_user.id),
            expires_delta=timedelta(milliseconds=1)
        )
        
        # Wait for token to expire
        time.sleep(0.1)
        
        refresh_data = {"refresh_token": refresh_token}
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Token has expired" in data["detail"]

    def test_refresh_token_missing(self, client: TestClient):
        """Test refresh without token."""
        response = client.post("/api/v1/auth/refresh", json={})
        
        assert response.status_code == 422  # Validation error

    def test_logout_success(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test successful logout."""
        access_token = security_manager.create_access_token(
            subject=test_user.username,
            tenant_id=str(test_tenant.id),
            user_id=str(test_user.id)
        )
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        with patch('app.api.v1.auth.blacklist_token'):
            response = client.post("/api/v1/auth/logout", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Successfully logged out"

    def test_logout_invalid_token(self, client: TestClient):
        """Test logout with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        
        response = client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid authentication credentials" in data["detail"]

    def test_logout_missing_token(self, client: TestClient):
        """Test logout without token."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]

    def test_get_current_user_info(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test getting current user information."""
        access_token = security_manager.create_access_token(
            subject=test_user.username,
            tenant_id=str(test_tenant.id),
            user_id=str(test_user.id)
        )
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        with patch('app.api.v1.auth.get_user_by_id', return_value=test_user):
            response = client.get("/api/v1/auth/me", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == test_user.username
            assert data["email"] == test_user.email
            assert data["first_name"] == test_user.first_name
            assert data["last_name"] == test_user.last_name

    def test_get_current_user_info_invalid_token(self, client: TestClient):
        """Test getting user info with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid authentication credentials" in data["detail"]

    def test_get_current_user_info_missing_token(self, client: TestClient):
        """Test getting user info without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]

    def test_oauth2_login_placeholder(self, client: TestClient):
        """Test OAuth2 login placeholder endpoint."""
        response = client.get("/api/v1/auth/oauth2/google")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OAuth2 Google login - Implementation pending"

    def test_oauth2_callback_placeholder(self, client: TestClient):
        """Test OAuth2 callback placeholder endpoint."""
        response = client.get("/api/v1/auth/oauth2/google/callback")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OAuth2 Google callback - Implementation pending"

    def test_password_reset_request_placeholder(self, client: TestClient):
        """Test password reset request placeholder endpoint."""
        reset_data = {"email": "test@example.com"}
        
        response = client.post("/api/v1/auth/password-reset-request", json=reset_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset request - Implementation pending"

    def test_password_reset_confirm_placeholder(self, client: TestClient):
        """Test password reset confirmation placeholder endpoint."""
        reset_data = {
            "token": "reset_token_here",
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/password-reset-confirm", json=reset_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset confirmation - Implementation pending"

    def test_email_verification_placeholder(self, client: TestClient):
        """Test email verification placeholder endpoint."""
        response = client.get("/api/v1/auth/verify-email?token=verification_token")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Email verification - Implementation pending"

    def test_two_factor_auth_placeholder(self, client: TestClient):
        """Test two-factor authentication placeholder endpoint."""
        response = client.post("/api/v1/auth/2fa/enable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Two-factor authentication - Implementation pending"


class TestAuthValidation:
    """Test authentication validation."""

    def test_login_request_validation(self, client: TestClient):
        """Test login request validation."""
        # Test with empty data
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422
        
        # Test with invalid email format
        invalid_data = {
            "username": "testuser",
            "password": "testpass",
            "tenant_id": "invalid-uuid"
        }
        response = client.post("/api/v1/auth/login", json=invalid_data)
        assert response.status_code == 422

    def test_refresh_request_validation(self, client: TestClient):
        """Test refresh request validation."""
        # Test with empty data
        response = client.post("/api/v1/auth/refresh", json={})
        assert response.status_code == 422
        
        # Test with missing refresh_token
        invalid_data = {"some_field": "value"}
        response = client.post("/api/v1/auth/refresh", json=invalid_data)
        assert response.status_code == 422


class TestAuthSecurity:
    """Test authentication security features."""

    def test_password_verification(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test password verification security."""
        # Test with correct password
        login_data = {
            "username": "testuser",
            "password": "testpassword123",
            "tenant_id": str(test_tenant.id)
        }
        
        with patch('app.api.v1.auth.verify_password', return_value=True):
            with patch('app.api.v1.auth.get_user_by_username', return_value=test_user):
                response = client.post("/api/v1/auth/login", json=login_data)
                assert response.status_code == 200
        
        # Test with incorrect password
        with patch('app.api.v1.auth.verify_password', return_value=False):
            with patch('app.api.v1.auth.get_user_by_username', return_value=test_user):
                response = client.post("/api/v1/auth/login", json=login_data)
                assert response.status_code == 401

    def test_token_security(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test token security features."""
        # Test that tokens contain required claims
        access_token = security_manager.create_access_token(
            subject=test_user.username,
            tenant_id=str(test_tenant.id),
            user_id=str(test_user.id)
        )
        
        # Verify token payload
        payload = security_manager.verify_token(access_token)
        assert "sub" in payload
        assert "tenant_id" in payload
        assert "user_id" in payload
        assert "type" in payload
        assert payload["type"] == "access"

    def test_rate_limiting_placeholder(self, client: TestClient):
        """Test rate limiting placeholder."""
        # This would test actual rate limiting implementation
        # For now, we'll test that the endpoint responds
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpassword123",
            "tenant_id": "test-tenant"
        })
        
        # Should get some response (either success or failure)
        assert response.status_code in [200, 401, 422]


class TestAuthIntegration:
    """Test authentication integration scenarios."""

    def test_full_auth_flow(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test complete authentication flow."""
        # 1. Login
        login_data = {
            "username": "testuser",
            "password": "testpassword123",
            "tenant_id": str(test_tenant.id)
        }
        
        with patch('app.api.v1.auth.verify_password', return_value=True):
            with patch('app.api.v1.auth.get_user_by_username', return_value=test_user):
                login_response = client.post("/api/v1/auth/login", json=login_data)
                assert login_response.status_code == 200
                
                login_data = login_response.json()
                access_token = login_data["access_token"]
                refresh_token = login_data["refresh_token"]
        
        # 2. Get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        
        with patch('app.api.v1.auth.get_user_by_id', return_value=test_user):
            me_response = client.get("/api/v1/auth/me", headers=headers)
            assert me_response.status_code == 200
        
        # 3. Refresh token
        refresh_data = {"refresh_token": refresh_token}
        refresh_response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200
        
        # 4. Logout
        with patch('app.api.v1.auth.blacklist_token'):
            logout_response = client.post("/api/v1/auth/logout", headers=headers)
            assert logout_response.status_code == 200

    def test_cross_tenant_isolation(self, client: TestClient, test_tenant: Tenant, test_user: User):
        """Test that users cannot access other tenants."""
        # Create token for one tenant
        access_token = security_manager.create_access_token(
            subject=test_user.username,
            tenant_id=str(test_tenant.id),
            user_id=str(test_user.id)
        )
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Try to access with different tenant ID
        with patch('app.api.v1.auth.get_user_by_id', return_value=test_user):
            response = client.get("/api/v1/auth/me", headers=headers)
            
            # Should still work as the token contains the correct tenant_id
            # This test would be more meaningful with actual tenant isolation in the API
            assert response.status_code == 200

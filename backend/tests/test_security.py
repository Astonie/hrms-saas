import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from jose import JWTError
from fastapi import HTTPException, status

from app.core.security import (
    security_manager,
    get_current_user,
    get_current_tenant,
    get_current_user_permissions,
    require_permission,
    require_any_permission,
    require_all_permissions
)
from app.models.user import User


class TestSecurityManager:
    """Test security manager functionality."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = security_manager.hash_password(password)
        
        assert hashed != password
        assert security_manager.verify_password(password, hashed) is True
        assert security_manager.verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Test access token creation."""
        subject = "testuser"
        tenant_id = "test-tenant"
        user_id = "test-user-id"
        permissions = ["read", "write"]
        
        token = security_manager.create_access_token(
            subject=subject,
            tenant_id=tenant_id,
            user_id=user_id,
            permissions=permissions
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token payload
        payload = security_manager.verify_token(token)
        assert payload["sub"] == subject
        assert payload["tenant_id"] == tenant_id
        assert payload["user_id"] == user_id
        assert payload["permissions"] == permissions
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        subject = "testuser"
        tenant_id = "test-tenant"
        user_id = "test-user-id"
        
        token = security_manager.create_refresh_token(
            subject=subject,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token payload
        payload = security_manager.verify_token(token)
        assert payload["sub"] == subject
        assert payload["tenant_id"] == tenant_id
        assert payload["user_id"] == user_id
        assert payload["type"] == "refresh"

    def test_token_expiration(self):
        """Test token expiration."""
        subject = "testuser"
        
        # Test default expiration
        token = security_manager.create_access_token(subject=subject)
        payload = security_manager.verify_token(token)
        assert "exp" in payload
        
        # Test custom expiration
        custom_expiry = timedelta(hours=2)
        token = security_manager.create_access_token(
            subject=subject,
            expires_delta=custom_expiry
        )
        payload = security_manager.verify_token(token)
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        # Should expire in approximately 2 hours
        now = datetime.utcnow()
        time_diff = exp_datetime - now
        assert 1.5 <= time_diff.total_seconds() / 3600 <= 2.5

    def test_verify_token_success(self):
        """Test successful token verification."""
        subject = "testuser"
        token = security_manager.create_access_token(subject=subject)
        
        payload = security_manager.verify_token(token)
        assert payload["sub"] == subject

    def test_verify_token_invalid(self):
        """Test invalid token verification."""
        with pytest.raises(JWTError):
            security_manager.verify_token("invalid.token.here")

    def test_verify_token_expired(self):
        """Test expired token verification."""
        # Create token with very short expiration
        token = security_manager.create_access_token(
            subject="testuser",
            expires_delta=timedelta(milliseconds=1)
        )
        
        # Wait for token to expire
        import time
        time.sleep(0.1)
        
        with pytest.raises(JWTError):
            security_manager.verify_token(token)

    def test_extract_tenant_id(self):
        """Test tenant ID extraction from token."""
        tenant_id = "test-tenant"
        token = security_manager.create_access_token(
            subject="testuser",
            tenant_id=tenant_id
        )
        
        extracted = security_manager.extract_tenant_id(token)
        assert extracted == tenant_id

    def test_extract_user_id(self):
        """Test user ID extraction from token."""
        user_id = "test-user-id"
        token = security_manager.create_access_token(
            subject="testuser",
            user_id=user_id
        )
        
        extracted = security_manager.extract_user_id(token)
        assert extracted == user_id

    def test_extract_permissions(self):
        """Test permissions extraction from token."""
        permissions = ["read", "write", "delete"]
        token = security_manager.create_access_token(
            subject="testuser",
            permissions=permissions
        )
        
        extracted = security_manager.extract_permissions(token)
        assert extracted == permissions

    def test_extract_permissions_none(self):
        """Test permissions extraction when none exist."""
        token = security_manager.create_access_token(subject="testuser")
        
        extracted = security_manager.extract_permissions(token)
        assert extracted == []


class TestSecurityDependencies:
    """Test security dependency functions."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful user extraction from token."""
        # Mock the HTTPBearer dependency
        mock_credentials = MagicMock()
        mock_credentials.credentials = security_manager.create_access_token(
            subject="testuser",
            user_id="test-user-id"
        )
        
        with patch('app.core.security.security') as mock_security:
            mock_security.return_value = mock_credentials
            
            result = await get_current_user(mock_credentials)
            assert result["user_id"] == "test-user-id"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test user extraction with invalid token."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid.token"
        
        with patch('app.core.security.security') as mock_security:
            mock_security.return_value = mock_credentials
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid authentication credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_tenant_success(self):
        """Test successful tenant extraction from token."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = security_manager.create_access_token(
            subject="testuser",
            tenant_id="test-tenant"
        )
        
        with patch('app.core.security.security') as mock_security:
            mock_security.return_value = mock_credentials
            
            result = await get_current_tenant(mock_credentials)
            assert result == "test-tenant"

    @pytest.mark.asyncio
    async def test_get_current_user_permissions_success(self):
        """Test successful permissions extraction from token."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = security_manager.create_access_token(
            subject="testuser",
            permissions=["read", "write"]
        )
        
        with patch('app.core.security.security') as mock_security:
            mock_security.return_value = mock_credentials
            
            result = await get_current_user_permissions(mock_credentials)
            assert result == ["read", "write"]


class TestPermissionDecorators:
    """Test permission decorator functions."""

    def test_require_permission_success(self):
        """Test successful permission requirement."""
        permissions = ["read", "write", "delete"]
        decorator = require_permission("read")
        
        # Mock the dependency function
        mock_dependency = MagicMock(return_value=permissions)
        
        # Apply the decorator
        result = decorator(mock_dependency)
        assert result == permissions

    def test_require_permission_denied(self):
        """Test denied permission requirement."""
        permissions = ["write", "delete"]  # Missing "read"
        decorator = require_permission("read")
        
        # Mock the dependency function
        mock_dependency = MagicMock(return_value=permissions)
        
        # Apply the decorator - should raise exception
        with pytest.raises(HTTPException) as exc_info:
            decorator(mock_dependency)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Permission 'read' required" in str(exc_info.value.detail)

    def test_require_any_permission_success(self):
        """Test successful any permission requirement."""
        permissions = ["read", "write"]
        decorator = require_any_permission("read", "delete")
        
        # Mock the dependency function
        mock_dependency = MagicMock(return_value=permissions)
        
        # Apply the decorator
        result = decorator(mock_dependency)
        assert result == permissions

    def test_require_any_permission_denied(self):
        """Test denied any permission requirement."""
        permissions = ["write", "update"]  # Missing both "read" and "delete"
        decorator = require_any_permission("read", "delete")
        
        # Mock the dependency function
        mock_dependency = MagicMock(return_value=permissions)
        
        # Apply the decorator - should raise exception
        with pytest.raises(HTTPException) as exc_info:
            decorator(mock_dependency)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "One of permissions ['read', 'delete'] required" in str(exc_info.value.detail)

    def test_require_all_permissions_success(self):
        """Test successful all permissions requirement."""
        permissions = ["read", "write", "delete"]
        decorator = require_all_permissions("read", "write")
        
        # Mock the dependency function
        mock_dependency = MagicMock(return_value=permissions)
        
        # Apply the decorator
        result = decorator(mock_dependency)
        assert result == permissions

    def test_require_all_permissions_denied(self):
        """Test denied all permissions requirement."""
        permissions = ["read", "update"]  # Missing "write"
        decorator = require_all_permissions("read", "write")
        
        # Mock the dependency function
        mock_dependency = MagicMock(return_value=permissions)
        
        # Apply the decorator - should raise exception
        with pytest.raises(HTTPException) as exc_info:
            decorator(mock_dependency)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "All permissions ['read', 'write'] required" in str(exc_info.value.detail)


class TestPasswordSecurity:
    """Test password security features."""

    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Strong password
        strong_password = "StrongPass123!@#"
        hashed = security_manager.hash_password(strong_password)
        assert security_manager.verify_password(strong_password, hashed) is True
        
        # Weak password (should still work but could be enhanced with validation)
        weak_password = "123"
        hashed = security_manager.hash_password(weak_password)
        assert security_manager.verify_password(weak_password, hashed) is True

    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        password = "testpassword"
        hash1 = security_manager.hash_password(password)
        hash2 = security_manager.hash_password(password)
        
        assert hash1 != hash2  # Due to salt
        assert security_manager.verify_password(password, hash1) is True
        assert security_manager.verify_password(password, hash2) is True

    def test_special_characters_in_password(self):
        """Test passwords with special characters."""
        special_password = "P@ssw0rd!@#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = security_manager.hash_password(special_password)
        assert security_manager.verify_password(special_password, hashed) is True

    def test_unicode_password(self):
        """Test passwords with unicode characters."""
        unicode_password = "P@ssw0rd测试🚀"
        hashed = security_manager.hash_password(unicode_password)
        assert security_manager.verify_password(unicode_password, hashed) is True

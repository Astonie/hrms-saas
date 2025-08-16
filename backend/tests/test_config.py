import pytest
from unittest.mock import patch
from app.core.config import Settings, settings


class TestSettings:
    """Test configuration settings."""

    def test_default_values(self):
        """Test default configuration values."""
        with patch.dict('os.environ', {}, clear=True):
            test_settings = Settings()
            assert test_settings.app_name == "HRMS-SAAS"
            assert test_settings.debug is True
            assert test_settings.environment == "development"

    def test_environment_override(self):
        """Test environment variable override."""
        with patch.dict('os.env', {'DEBUG': 'false', 'ENVIRONMENT': 'production'}, clear=True):
            test_settings = Settings()
            assert test_settings.debug is False
            assert test_settings.environment == "production"

    def test_database_url_validation(self):
        """Test database URL validation."""
        with patch.dict('os.environ', {'DATABASE_URL': ''}, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL is required"):
                Settings()

    def test_jwt_secret_validation(self):
        """Test JWT secret validation."""
        with patch.dict('os.environ', {'JWT_SECRET_KEY': ''}, clear=True):
            with pytest.raises(ValueError, match="JWT_SECRET_KEY is required"):
                Settings()

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing."""
        with patch.dict('os.environ', {'CORS_ORIGINS': '["http://localhost:3000", "https://example.com"]'}, clear=True):
            test_settings = Settings()
            assert test_settings.cors_origins == ["http://localhost:3000", "https://example.com"]

    def test_cors_origins_string(self):
        """Test CORS origins as string."""
        with patch.dict('os.environ', {'CORS_ORIGINS': 'http://localhost:3000,https://example.com'}, clear=True):
            test_settings = Settings()
            assert test_settings.cors_origins == ["http://localhost:3000", "https://example.com"]

    def test_is_development(self):
        """Test development environment check."""
        with patch.dict('os.environ', {'ENVIRONMENT': 'development'}, clear=True):
            test_settings = Settings()
            assert test_settings.is_development() is True
            assert test_settings.is_production() is False

    def test_is_production(self):
        """Test production environment check."""
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}, clear=True):
            test_settings = Settings()
            assert test_settings.is_production() is True
            assert test_settings.is_development() is False

    def test_redis_url_default(self):
        """Test Redis URL default value."""
        with patch.dict('os.environ', {}, clear=True):
            test_settings = Settings()
            assert test_settings.redis_url == "redis://localhost:6379/0"

    def test_redis_url_override(self):
        """Test Redis URL override."""
        with patch.dict('os.environ', {'REDIS_URL': 'redis://custom:6379/1'}, clear=True):
            test_settings = Settings()
            assert test_settings.redis_url == "redis://custom:6379/1"

    def test_tenant_configuration(self):
        """Test tenant configuration settings."""
        with patch.dict('os.environ', {}, clear=True):
            test_settings = Settings()
            assert test_settings.tenant_header == "X-Tenant-ID"
            assert test_settings.tenant_subdomain_enabled is True
            assert test_settings.tenant_domain_enabled is True

    def test_security_settings(self):
        """Test security configuration."""
        with patch.dict('os.environ', {}, clear=True):
            test_settings = Settings()
            assert test_settings.cors_allow_credentials is True
            assert test_settings.rate_limit_enabled is True
            assert test_settings.max_requests_per_minute == 100

    def test_logging_configuration(self):
        """Test logging configuration."""
        with patch.dict('os.environ', {}, clear=True):
            test_settings = Settings()
            assert test_settings.log_level == "INFO"
            assert test_settings.log_format == "json"

    def test_feature_flags(self):
        """Test feature flag configuration."""
        with patch.dict('os.environ', {}, clear=True):
            test_settings = Settings()
            assert test_settings.oauth2_enabled is False
            assert test_settings.file_upload_enabled is True
            assert test_settings.notification_enabled is True

    def test_settings_instance(self):
        """Test that the global settings instance is created."""
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'jwt_secret_key')

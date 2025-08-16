"""
Configuration settings for HRMS-SAAS.
Loads environment variables and provides application configuration.
"""

import os
from typing import List, Optional, Union
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    app_name: str = Field(default="HRMS-SAAS", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Database Configuration
    database_url: str = Field(env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # JWT Configuration
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # OAuth2 Configuration
    oauth2_secret_key: str = Field(env="OAUTH2_SECRET_KEY")
    google_client_id: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    github_client_id: Optional[str] = Field(default=None, env="GITHUB_CLIENT_ID")
    github_client_secret: Optional[str] = Field(default=None, env="GITHUB_CLIENT_SECRET")
    
    # Email Configuration
    smtp_host: str = Field(default="localhost", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_tls: bool = Field(default=True, env="SMTP_TLS")
    smtp_from_email: str = Field(default="noreply@hrms-saas.com", env="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="HRMS System", env="SMTP_FROM_NAME")
    
    # File Storage Configuration
    storage_type: str = Field(default="local", env="STORAGE_TYPE")
    storage_bucket: str = Field(default="hrms-documents", env="STORAGE_BUCKET")
    storage_region: str = Field(default="us-east-1", env="STORAGE_REGION")
    storage_access_key: Optional[str] = Field(default=None, env="STORAGE_ACCESS_KEY")
    storage_secret_key: Optional[str] = Field(default=None, env="STORAGE_SECRET_KEY")
    storage_endpoint_url: Optional[str] = Field(default=None, env="STORAGE_ENDPOINT_URL")
    
    # Security Configuration
    secret_key: str = Field(env="SECRET_KEY")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Monitoring Configuration
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    
    # Multi-Tenant Configuration
    tenant_header: str = Field(default="X-Tenant-ID", env="TENANT_HEADER")
    tenant_subdomain_enabled: bool = Field(default=True, env="TENANT_SUBDOMAIN_ENABLED")
    tenant_domain_enabled: bool = Field(default=True, env="TENANT_DOMAIN_ENABLED")
    
    # Feature Flags
    feature_billing_enabled: bool = Field(default=False, env="FEATURE_BILLING_ENABLED")
    feature_analytics_enabled: bool = Field(default=True, env="FEATURE_ANALYTICS_ENABLED")
    feature_webhooks_enabled: bool = Field(default=False, env="FEATURE_WEBHOOKS_ENABLED")
    feature_localization_enabled: bool = Field(default=False, env="FEATURE_LOCALIZATION_ENABLED")
    
    # Development Settings
    create_demo_data: bool = Field(default=False, env="CREATE_DEMO_DATA")
    auto_create_tenants: bool = Field(default=False, env="AUTO_CREATE_TENANTS")
    skip_email_verification: bool = Field(default=False, env="SKIP_EMAIL_VERIFICATION")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.strip("[]").split(",")]
        return v
    
    @validator("database_url", pre=True)
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    @validator("jwt_secret_key", pre=True)
    def validate_jwt_secret_key(cls, v):
        """Validate JWT secret key."""
        if not v or len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("secret_key", pre=True)
    def validate_secret_key(cls, v):
        """Validate application secret key."""
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Environment-specific settings
def is_development() -> bool:
    """Check if running in development mode."""
    return settings.environment.lower() in ["development", "dev", "local"]

def is_production() -> bool:
    """Check if running in production mode."""
    return settings.environment.lower() in ["production", "prod"]

def is_testing() -> bool:
    """Check if running in testing mode."""
    return settings.environment.lower() in ["testing", "test"]

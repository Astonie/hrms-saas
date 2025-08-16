"""
Security module for HRMS-SAAS application.
Handles JWT authentication, password hashing, and security utilities.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


class SecurityManager:
    """Manages security operations for the HRMS system."""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate a password hash."""
        return pwd_context.hash(password)
    
    def create_access_token(
        self, 
        subject: Union[str, Any], 
        expires_delta: Optional[timedelta] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        permissions: Optional[list] = None
    ) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "access"
        }
        
        # Add tenant context if provided
        if tenant_id:
            to_encode["tenant_id"] = tenant_id
        
        # Add user context if provided
        if user_id:
            to_encode["user_id"] = user_id
        
        # Add permissions if provided
        if permissions:
            to_encode["permissions"] = permissions
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        subject: Union[str, Any], 
        expires_delta: Optional[timedelta] = None,
        tenant_id: Optional[str] = None
    ) -> str:
        """Create a JWT refresh token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh"
        }
        
        # Add tenant context if provided
        if tenant_id:
            to_encode["tenant_id"] = tenant_id
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def verify_access_token(self, token: str) -> dict:
        """Verify and decode an access token specifically."""
        payload = self.verify_token(token)
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    
    def verify_refresh_token(self, token: str) -> dict:
        """Verify and decode a refresh token specifically."""
        payload = self.verify_token(token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    
    def extract_tenant_id(self, token: str) -> Optional[str]:
        """Extract tenant ID from a token."""
        payload = self.verify_token(token)
        return payload.get("tenant_id")
    
    def extract_user_id(self, token: str) -> Optional[str]:
        """Extract user ID from a token."""
        payload = self.verify_token(token)
        return payload.get("user_id")
    
    def extract_permissions(self, token: str) -> list:
        """Extract permissions from a token."""
        payload = self.verify_token(token)
        return payload.get("permissions", [])
    
    def generate_random_string(self, length: int = 32) -> str:
        """Generate a random string for secrets."""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self) -> str:
        """Generate a secure API key."""
        return f"hrms_{secrets.token_urlsafe(32)}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage."""
        return pwd_context.hash(api_key)
    
    def verify_api_key(self, plain_api_key: str, hashed_api_key: str) -> bool:
        """Verify an API key against its hash."""
        return pwd_context.verify(plain_api_key, hashed_api_key)


# Global security manager instance
security_manager = SecurityManager()


# Dependency functions for FastAPI
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get the current user from the JWT token."""
    token = credentials.credentials
    payload = security_manager.verify_access_token(token)
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_tenant(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Get the current tenant ID from the JWT token."""
    token = credentials.credentials
    tenant_id = security_manager.extract_tenant_id(token)
    
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return tenant_id


async def get_current_user_permissions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> list:
    """Get the current user's permissions from the JWT token."""
    token = credentials.credentials
    return security_manager.extract_permissions(token)


def require_permission(permission: str):
    """Decorator to require a specific permission."""
    def permission_dependency(
        current_permissions: list = Depends(get_current_user_permissions)
    ):
        if permission not in current_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_permissions
    
    return permission_dependency


def require_any_permission(permissions: list):
    """Decorator to require any of the specified permissions."""
    def permission_dependency(
        current_permissions: list = Depends(get_current_user_permissions)
    ):
        if not any(perm in current_permissions for perm in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of permissions {permissions} required"
            )
        return current_permissions
    
    return permission_dependency


def require_all_permissions(permissions: list):
    """Decorator to require all of the specified permissions."""
    def permission_dependency(
        current_permissions: list = Depends(get_current_user_permissions)
    ):
        if not all(perm in current_permissions for perm in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All permissions {permissions} required"
            )
        return current_permissions
    
    return permission_dependency


# Utility functions
def hash_password(password: str) -> str:
    """Hash a password."""
    return security_manager.get_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return security_manager.verify_password(plain_password, hashed_password)


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    permissions: Optional[list] = None
) -> str:
    """Create an access token."""
    return security_manager.create_access_token(
        subject, expires_delta, tenant_id, user_id, permissions
    )


def create_refresh_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    tenant_id: Optional[str] = None
) -> str:
    """Create a refresh token."""
    return security_manager.create_refresh_token(subject, expires_delta, tenant_id)


def generate_random_string(length: int = 32) -> str:
    """Generate a random string."""
    return security_manager.generate_random_string(length)


def generate_api_key() -> str:
    """Generate an API key."""
    return security_manager.generate_api_key()

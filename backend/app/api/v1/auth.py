"""
Authentication API endpoints for HRMS-SAAS.
Handles login, logout, token refresh, and OAuth2 authentication.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from ...core.security import (
    security_manager, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    get_current_user
)
from ...core.database import get_session
from ...models.user import User, UserRole
from ...models.tenant import Tenant
from ...core.database import tenant_db_manager

router = APIRouter()


# Request/Response Models
class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str
    tenant_id: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    tenant_id: str
    permissions: list


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request model."""
    refresh_token: str


class OAuth2LoginRequest(BaseModel):
    """OAuth2 login request model."""
    provider: str  # google, github, etc.
    code: str
    redirect_uri: str
    tenant_id: Optional[str] = None


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db_session = Depends(get_session)
):
    """
    Authenticate user and return access/refresh tokens.
    
    This endpoint handles both username/password and OAuth2 authentication.
    """
    try:
        # Get user from database
        user = await get_user_by_username(db_session, request.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Verify password
        if not verify_password(request.password, user.hashed_password):
            # Record failed login attempt
            user.record_failed_login()
            await db_session.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Check if user is active
        if not user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active or verified"
            )
        
        # Get tenant information
        tenant = await get_tenant_for_user(db_session, user.id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any tenant"
            )
        
        # Check if tenant is active
        if not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant account is not active"
            )
        
        # Get user permissions
        permissions = user.get_permissions()
        
        # Create tokens
        access_token = create_access_token(
            subject=user.username,
            tenant_id=tenant.slug,
            user_id=user.id,
            permissions=permissions
        )
        
        refresh_token = create_refresh_token(
            subject=user.username,
            tenant_id=tenant.slug
        )
        
        # Record successful login
        user.record_successful_login()
        await db_session.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=security_manager.access_token_expire_minutes * 60,
            user_id=user.id,
            tenant_id=tenant.slug,
            permissions=permissions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db_session = Depends(get_session)
):
    """
    Refresh access token using refresh token.
    """
    try:
        # Verify refresh token
        payload = security_manager.verify_refresh_token(request.refresh_token)
        username = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        
        if not username or not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        user = await get_user_by_username(db_session, username)
        if not user or not user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Verify tenant
        tenant = await get_tenant_by_slug(db_session, tenant_id)
        if not tenant or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant not found or inactive"
            )
        
        # Get user permissions
        permissions = user.get_permissions()
        
        # Create new tokens
        access_token = create_access_token(
            subject=user.username,
            tenant_id=tenant.slug,
            user_id=user.id,
            permissions=permissions
        )
        
        new_refresh_token = create_refresh_token(
            subject=user.username,
            tenant_id=tenant.slug
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=security_manager.access_token_expire_minutes * 60,
            user_id=user.id,
            tenant_id=tenant.slug,
            permissions=permissions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Logout user and invalidate refresh token.
    
    Note: In a production system, you would typically blacklist the refresh token
    in Redis or database for better security.
    """
    # For now, we just return success
    # In production, implement token blacklisting
    return {"message": "Successfully logged out"}


@router.post("/oauth2/login")
async def oauth2_login(
    request: OAuth2LoginRequest,
    db_session = Depends(get_session)
):
    """
    OAuth2 authentication endpoint.
    
    This is a placeholder for OAuth2 implementation.
    In production, you would integrate with specific OAuth2 providers.
    """
    # TODO: Implement OAuth2 authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth2 authentication not yet implemented"
    )


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_session)
):
    """
    Get current user information.
    """
    try:
        user_id = current_user.get("user_id")
        user = await get_user_by_id(db_session, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "user_type": user.user_type,
            "permissions": current_user.get("permissions", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


# Helper functions
async def get_user_by_username(db_session, username: str) -> Optional[User]:
    """Get user by username."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = select(User).options(selectinload(User.user_roles).selectinload(UserRole.role)).where(User.username == username)
    result = await db_session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db_session, user_id: str) -> Optional[User]:
    """Get user by ID."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = select(User).options(selectinload(User.user_roles).selectinload(UserRole.role)).where(User.id == user_id)
    result = await db_session.execute(stmt)
    return result.scalar_one_or_none()


async def get_tenant_for_user(db_session, user_id: str) -> Optional[Tenant]:
    """Get tenant for a user."""
    from sqlalchemy import select
    
    stmt = select(Tenant).where(Tenant.id == User.tenant_id).join(User, User.tenant_id == Tenant.id).where(User.id == user_id)
    result = await db_session.execute(stmt)
    return result.scalar_one_or_none()


async def get_tenant_by_slug(db_session, slug: str) -> Optional[Tenant]:
    """Get tenant by slug."""
    from sqlalchemy import select
    
    stmt = select(Tenant).where(Tenant.slug == slug)
    result = await db_session.execute(stmt)
    return result.scalar_one_or_none()

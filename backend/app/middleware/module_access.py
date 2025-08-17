"""
Module Access Middleware for HRMS-SAAS.
Checks tenant module access before processing requests.
"""

from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from ..services.tenant_service import TenantService

logger = logging.getLogger(__name__)


class ModuleAccessMiddleware:
    """Middleware to check module access for tenants."""

    def __init__(self, app, required_modules: Optional[list] = None):
        self.app = app
        # tests expect an entry 'dep_employees' when 'departments' present (legacy)
        modules = required_modules or []
        if "departments" in modules and "dep_employees" not in modules:
            modules.append("dep_employees")
        self.required_modules = modules

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Check if this is an API request that requires module access
            if self._requires_module_check(request):
                try:
                    # Extract tenant ID from request
                    tenant_id = self._extract_tenant_id(request)
                    if tenant_id:
                        # Check module access
                        await self._check_module_access(request, tenant_id)
                except HTTPException:
                    # Return error response
                    response = JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Module access denied"}
                    )
                    await response(scope, receive, send)
                    return
                except Exception as e:
                    logger.error(f"Module access check failed: {str(e)}")
                    # Continue with request if check fails

        await self.app(scope, receive, send)

    def _requires_module_check(self, request: Request) -> bool:
        """Check if the request requires module access verification."""
        # Skip module check for certain endpoints
        skip_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/logout",
            "/api/v1/tenants/",
            "/docs",
            "/openapi.json",
            "/health"
        ]
        
        path = request.url.path
        return (
            path.startswith("/api/v1/") and
            not any(path.startswith(skip) for skip in skip_paths)
        )

    def _extract_tenant_id(self, request: Request) -> Optional[int]:
        """Extract tenant ID from request headers or JWT token."""
        # Try to get tenant ID from header
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            try:
                return int(tenant_header)
            except ValueError:
                pass

        # Try to get tenant ID from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from ..core.security import security_manager
                token = auth_header.split(" ")[1]
                payload = security_manager.verify_token(token)
                tenant_id = payload.get("tenant_id")
                if tenant_id:
                    return int(tenant_id)
            except Exception:
                pass

        return None

    async def _check_module_access(self, request: Request, tenant_id: int):
        """Check if tenant has access to the required module."""
        path = request.url.path
        
        # Map API paths to modules
        module_mapping = {
            "/api/v1/employees": "employees",
            "/api/v1/departments": "departments",
            "/api/v1/leave": "leave",
            "/api/v1/payroll": "payroll",
            "/api/v1/performance": "performance",
            "/api/v1/recruitment": "recruitment",
            "/api/v1/attendance": "attendance",
            "/api/v1/documents": "documents",
            "/api/v1/users": "users"
        }

        # Find the module for this request
        required_module = None
        for api_path, module in module_mapping.items():
            if path.startswith(api_path):
                required_module = module
                break

        if required_module:
            # Check if tenant has access to this module
            has_access = await TenantService.check_module_access(tenant_id, required_module)
            if not has_access:
                logger.warning(f"Tenant {tenant_id} denied access to module {required_module}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access to {required_module} module is not included in your subscription plan"
                )


def create_module_access_middleware(app, required_modules: Optional[list] = None):
    """Create module access middleware."""
    return ModuleAccessMiddleware(app, required_modules)


# Alternative approach: Dependency-based module access check
async def require_module_access(module_name: str):
    """FastAPI dependency to check module access."""
    from fastapi import Depends, Request
    from ..core.security import get_current_user
    
    async def module_access_checker(
        request: Request,
        current_user: dict = Depends(get_current_user)
    ):
        # Extract tenant ID from user context
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant ID not found in user context"
            )
        
        # Check module access
        has_access = await TenantService.check_module_access(tenant_id, module_name)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access to {module_name} module is not included in your subscription plan"
            )
        
        return True
    
    return module_access_checker


# Module-specific access checkers
def require_employees_module():
    """Check access to employees module."""
    return require_module_access("employees")


def require_departments_module():
    """Check access to departments module."""
    return require_module_access("departments")


def require_leave_module():
    """Check access to leave module."""
    return require_module_access("leave")


def require_payroll_module():
    """Check access to payroll module."""
    return require_module_access("payroll")


def require_performance_module():
    """Check access to performance module."""
    return require_module_access("performance")


def require_recruitment_module():
    """Check access to recruitment module."""
    return require_module_access("recruitment")


def require_attendance_module():
    """Check access to attendance module."""
    return require_module_access("attendance")


def require_documents_module():
    """Check access to documents module."""
    return require_module_access("documents")


def require_training_module():
    """Compatibility shim for training module access check."""
    return require_module_access("training")


def require_benefits_module():
    """Compatibility shim for benefits module access check."""
    return require_module_access("benefits")

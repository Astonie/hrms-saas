"""
Main API router for HRMS-SAAS v1.
Includes all sub-routers for different HR modules.
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .employees import router as employees_router
from .departments import router as departments_router
from .leave import router as leave_router

# TODO: Add other HR modules as they are implemented
# from .payroll import router as payroll_router
# from .performance import router as performance_router
# from .recruitment import router as recruitment_router
# from .attendance import router as attendance_router
# from .documents import router as documents_router
# from .users import router as users_router
# from .tenants import router as tenants_router

api_router = APIRouter()

# Authentication and User Management
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

# Core HR Management
api_router.include_router(
    employees_router,
    prefix="/employees",
    tags=["Employee Management"]
)

api_router.include_router(
    departments_router,
    prefix="/departments",
    tags=["Department Management"]
)

api_router.include_router(
    leave_router,
    prefix="/leave",
    tags=["Leave Management"]
)

# TODO: Include other HR modules as they are implemented
# api_router.include_router(
#     payroll_router,
#     prefix="/payroll",
#     tags=["Payroll Management"]
# )

# api_router.include_router(
#     performance_router,
#     prefix="/performance",
#     tags=["Performance Management"]
# )

# api_router.include_router(
#     recruitment_router,
#     prefix="/recruitment",
#     tags=["Recruitment Management"]
# )

# api_router.include_router(
#     attendance_router,
#     prefix="/attendance",
#     tags=["Attendance Management"]
# )

# api_router.include_router(
#     documents_router,
#     prefix="/documents",
#     tags=["Document Management"]
# )

# api_router.include_router(
#     users_router,
#     prefix="/users",
#     tags=["User Management"]
# )

# api_router.include_router(
#     tenants_router,
#     prefix="/tenants",
#     tags=["Tenant Management"]
# )

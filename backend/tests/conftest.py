import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_session
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User, Role, UserRole
from app.models.employee import Employee, Department
from app.core.security import security_manager


# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """Set up test database and create tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Company",
        slug="test-company",
        contact_email="admin@testcompany.com",
        company_name="Test Company Inc.",
        status="active",
        plan="professional",
        max_users=100,
        max_employees=500
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.fixture
async def test_role(db_session: AsyncSession, test_tenant: Tenant) -> Role:
    """Create a test role."""
    role = Role(
        name="HR Manager",
        permissions={
            "employees": ["read", "write", "delete"],
            "departments": ["read", "write"],
            "leave": ["read", "approve"],
            "payroll": ["read"]
        },
        tenant_id=test_tenant.id
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def test_user(db_session: AsyncSession, test_tenant: Tenant, test_role: Role) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@testcompany.com",
        hashed_password=security_manager.hash_password("testpassword123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        tenant_id=test_tenant.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Assign role
    user_role = UserRole(
        user_id=user.id,
        role_id=test_role.id,
        tenant_id=test_tenant.id
    )
    db_session.add(user_role)
    await db_session.commit()
    
    return user


@pytest.fixture
async def test_department(db_session: AsyncSession, test_tenant: Tenant) -> Department:
    """Create a test department."""
    dept = Department(
        name="Human Resources",
        description="HR Department",
        tenant_id=test_tenant.id
    )
    db_session.add(dept)
    await db_session.commit()
    await db_session.refresh(dept)
    return dept


@pytest.fixture
async def test_employee(db_session: AsyncSession, test_tenant: Tenant, test_user: User, test_department: Department) -> Employee:
    """Create a test employee."""
    employee = Employee(
        user_id=test_user.id,
        employee_id="EMP001",
        employment_status="active",
        employment_type="full-time",
        hire_date="2023-01-15",
        department_id=test_department.id,
        job_title="HR Specialist",
        salary=50000,
        tenant_id=test_tenant.id
    )
    db_session.add(employee)
    await db_session.commit()
    await db_session.refresh(employee)
    return employee


@pytest.fixture
def mock_auth_headers(test_user: User, test_tenant: Tenant) -> dict:
    """Create mock authentication headers."""
    token = security_manager.create_access_token(
        subject=test_user.username,
        tenant_id=str(test_tenant.id),
        user_id=str(test_user.id),
        permissions=["employees:read", "employees:write"]
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_tenant_headers(test_tenant: Tenant) -> dict:
    """Create mock tenant headers."""
    return {"X-Tenant-ID": str(test_tenant.id)}


# Override the get_session dependency for testing
async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

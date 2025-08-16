import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.tenant import Tenant, TenantStatus, TenantPlan
from app.models.user import User, Role, UserRole
from app.models.employee import Employee, Department, EmploymentStatus, EmploymentType
from app.models.base import BaseModel


class TestTenantModel:
    """Test Tenant model functionality."""

    def test_tenant_creation(self):
        """Test basic tenant creation."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            company_name="Test Company Inc.",
            status=TenantStatus.ACTIVE,
            plan=TenantPlan.PROFESSIONAL
        )
        
        assert tenant.name == "Test Company"
        assert tenant.slug == "test-company"
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.plan == TenantPlan.PROFESSIONAL
        assert tenant.is_active is True

    def test_tenant_defaults(self):
        """Test tenant default values."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com"
        )
        
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.plan == TenantPlan.FREE
        assert tenant.max_users == 10
        assert tenant.max_employees == 50
        assert tenant.is_active is True

    def test_tenant_properties(self):
        """Test tenant computed properties."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            plan=TenantPlan.PROFESSIONAL,
            trial_ends_at=datetime.utcnow(),
            subscription_ends_at=datetime.utcnow()
        )
        
        # Test trial status
        assert tenant.is_trial is False  # trial_ends_at is in the past
        
        # Test subscription status
        assert tenant.is_subscription_expired is True  # subscription_ends_at is in the past

    def test_tenant_active_trial(self):
        """Test tenant with active trial."""
        future_date = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            trial_ends_at=future_date
        )
        
        assert tenant.is_trial is True

    def test_tenant_active_subscription(self):
        """Test tenant with active subscription."""
        future_date = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            subscription_ends_at=future_date
        )
        
        assert tenant.is_subscription_expired is False

    def test_tenant_feature_access(self):
        """Test tenant feature access methods."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            plan=TenantPlan.ENTERPRISE
        )
        
        # Test feature access
        assert tenant.has_feature("advanced_analytics") is True
        assert tenant.has_feature("nonexistent_feature") is False

    def test_tenant_setting_management(self):
        """Test tenant setting management methods."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com"
        )
        
        # Test setting management
        tenant.set_setting("theme", "dark")
        assert tenant.get_setting("theme") == "dark"
        assert tenant.get_setting("nonexistent", "default") == "default"

    def test_tenant_validation(self):
        """Test tenant validation rules."""
        # Test required fields
        with pytest.raises(IntegrityError):
            tenant = Tenant()
            # This would fail in actual database due to NOT NULL constraints

    def test_tenant_string_representation(self):
        """Test tenant string representation."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com"
        )
        
        assert str(tenant) == "Test Company (test-company)"
        assert repr(tenant) == "<Tenant(name='Test Company', slug='test-company')>"


class TestRoleModel:
    """Test Role model functionality."""

    def test_role_creation(self):
        """Test basic role creation."""
        role = Role(
            name="HR Manager",
            description="Human Resources Manager role",
            permissions={
                "employees": ["read", "write", "delete"],
                "departments": ["read", "write"]
            }
        )
        
        assert role.name == "HR Manager"
        assert role.description == "Human Resources Manager role"
        assert "employees" in role.permissions
        assert "read" in role.permissions["employees"]

    def test_role_defaults(self):
        """Test role default values."""
        role = Role(name="Test Role")
        
        assert role.permissions == {}
        assert role.is_active is True
        assert role.is_system is False

    def test_role_hierarchy(self):
        """Test role hierarchy functionality."""
        parent_role = Role(name="Parent Role")
        child_role = Role(
            name="Child Role",
            parent_role_id=parent_role.id
        )
        
        assert child_role.parent_role_id == parent_role.id

    def test_role_permission_management(self):
        """Test role permission management methods."""
        role = Role(name="Test Role")
        
        # Test adding permissions
        role.add_permission("employees", "read")
        role.add_permission("employees", "write")
        
        assert "employees" in role.permissions
        assert "read" in role.permissions["employees"]
        assert "write" in role.permissions["employees"]
        
        # Test removing permissions
        role.remove_permission("employees", "read")
        assert "read" not in role.permissions["employees"]
        assert "write" in role.permissions["employees"]
        
        # Test checking permissions
        assert role.has_permission("employees", "write") is True
        assert role.has_permission("employees", "read") is False

    def test_role_validation(self):
        """Test role validation rules."""
        # Test required fields
        with pytest.raises(IntegrityError):
            role = Role()
            # This would fail in actual database due to NOT NULL constraints

    def test_role_string_representation(self):
        """Test role string representation."""
        role = Role(name="Test Role")
        
        assert str(role) == "Test Role"
        assert repr(role) == "<Role(name='Test Role')>"


class TestUserModel:
    """Test User model functionality."""

    def test_user_creation(self):
        """Test basic user creation."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            first_name="Test",
            last_name="User"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True

    def test_user_defaults(self):
        """Test user default values."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_locked is False
        assert user.failed_login_attempts == 0

    def test_user_properties(self):
        """Test user computed properties."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            first_name="Test",
            last_name="User"
        )
        
        assert user.full_name == "Test User"
        assert user.display_name == "Test User"

    def test_user_with_middle_name(self):
        """Test user with middle name."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            first_name="Test",
            middle_name="Middle",
            last_name="User"
        )
        
        assert user.full_name == "Test Middle User"
        assert user.display_name == "Test Middle User"

    def test_user_display_name_fallback(self):
        """Test user display name fallback."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        
        assert user.display_name == "testuser"  # Falls back to username

    def test_user_account_management(self):
        """Test user account management methods."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        
        # Test account locking
        user.lock_account("Test lock reason")
        assert user.is_locked is True
        assert user.lock_reason == "Test lock reason"
        
        # Test account unlocking
        user.unlock_account()
        assert user.is_locked is False
        assert user.lock_reason is None

    def test_user_login_attempts(self):
        """Test user login attempt tracking."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        
        # Test failed login attempts
        user.record_failed_login()
        assert user.failed_login_attempts == 1
        
        user.record_failed_login()
        assert user.failed_login_attempts == 2
        
        # Test resetting failed attempts
        user.reset_failed_login_attempts()
        assert user.failed_login_attempts == 0

    def test_user_role_management(self):
        """Test user role management methods."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        
        # Test role assignment
        role = Role(name="Test Role")
        user.assign_role(role)
        
        assert len(user.user_roles) == 1
        assert user.user_roles[0].role == role
        
        # Test role removal
        user.remove_role(role)
        assert len(user.user_roles) == 0

    def test_user_permission_checking(self):
        """Test user permission checking methods."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        
        # Create role with permissions
        role = Role(
            name="Test Role",
            permissions={
                "employees": ["read", "write"],
                "departments": ["read"]
            }
        )
        
        user.assign_role(role)
        
        # Test permission checking
        assert user.has_permission("employees", "read") is True
        assert user.has_permission("employees", "write") is True
        assert user.has_permission("employees", "delete") is False
        assert user.has_permission("departments", "read") is True
        assert user.has_permission("departments", "write") is False

    def test_user_validation(self):
        """Test user validation rules."""
        # Test required fields
        with pytest.raises(IntegrityError):
            user = User()
            # This would fail in actual database due to NOT NULL constraints

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            first_name="Test",
            last_name="User"
        )
        
        assert str(user) == "Test User (testuser)"
        assert repr(user) == "<User(username='testuser', email='test@example.com')>"


class TestUserRoleModel:
    """Test UserRole model functionality."""

    def test_user_role_creation(self):
        """Test basic user role creation."""
        user_role = UserRole(
            user_id="user-uuid",
            role_id="role-uuid"
        )
        
        assert user_role.user_id == "user-uuid"
        assert user_role.role_id == "role-uuid"

    def test_user_role_relationships(self):
        """Test user role relationships."""
        user_role = UserRole(
            user_id="user-uuid",
            role_id="role-uuid"
        )
        
        # Test that relationships can be set
        user_role.user = User(username="testuser", email="test@example.com", hashed_password="hash")
        user_role.role = Role(name="Test Role")
        
        assert user_role.user.username == "testuser"
        assert user_role.role.name == "Test Role"

    def test_user_role_string_representation(self):
        """Test user role string representation."""
        user_role = UserRole(
            user_id="user-uuid",
            role_id="role-uuid"
        )
        
        assert str(user_role) == "UserRole(user_id='user-uuid', role_id='role-uuid')"
        assert repr(user_role) == "<UserRole(user_id='user-uuid', role_id='role-uuid')>"


class TestDepartmentModel:
    """Test Department model functionality."""

    def test_department_creation(self):
        """Test basic department creation."""
        dept = Department(
            name="Human Resources",
            description="HR Department",
            code="HR"
        )
        
        assert dept.name == "Human Resources"
        assert dept.description == "HR Department"
        assert dept.code == "HR"

    def test_department_defaults(self):
        """Test department default values."""
        dept = Department(name="Test Department")
        
        assert dept.is_active is True
        assert dept.description is None
        assert dept.code is None

    def test_department_hierarchy(self):
        """Test department hierarchy functionality."""
        parent_dept = Department(name="Parent Department")
        child_dept = Department(
            name="Child Department",
            parent_department_id=parent_dept.id
        )
        
        assert child_dept.parent_department_id == parent_dept.id

    def test_department_employee_management(self):
        """Test department employee management."""
        dept = Department(name="Test Department")
        
        # Test adding department head
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.ACTIVE
        )
        
        dept.department_head_id = employee.id
        assert dept.department_head_id == employee.id

    def test_department_validation(self):
        """Test department validation rules."""
        # Test required fields
        with pytest.raises(IntegrityError):
            dept = Department()
            # This would fail in actual database due to NOT NULL constraints

    def test_department_string_representation(self):
        """Test department string representation."""
        dept = Department(name="Test Department")
        
        assert str(dept) == "Test Department"
        assert repr(dept) == "<Department(name='Test Department')>"


class TestEmployeeModel:
    """Test Employee model functionality."""

    def test_employee_creation(self):
        """Test basic employee creation."""
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
            hire_date="2023-01-15",
            job_title="Software Engineer",
            salary=75000
        )
        
        assert employee.employee_id == "EMP001"
        assert employee.employment_status == EmploymentStatus.ACTIVE
        assert employee.employment_type == EmploymentType.FULL_TIME
        assert employee.job_title == "Software Engineer"
        assert employee.salary == 75000

    def test_employee_defaults(self):
        """Test employee default values."""
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.ACTIVE
        )
        
        assert employee.is_active is True
        assert employee.employment_type == EmploymentStatus.ACTIVE
        assert employee.salary is None

    def test_employee_dates(self):
        """Test employee date handling."""
        hire_date = date(2023, 1, 15)
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.ACTIVE,
            hire_date=hire_date
        )
        
        assert employee.hire_date == hire_date
        assert employee.employment_length_days is None  # No termination date

    def test_employee_employment_length(self):
        """Test employee employment length calculation."""
        hire_date = date(2023, 1, 15)
        termination_date = date(2024, 1, 15)
        
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.TERMINATED,
            hire_date=hire_date,
            termination_date=termination_date
        )
        
        # Should be approximately 365 days
        assert employee.employment_length_days == 365

    def test_employee_salary_management(self):
        """Test employee salary management."""
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.ACTIVE,
            salary=50000
        )
        
        # Test salary increase
        employee.salary = 55000
        assert employee.salary == 55000
        
        # Test salary decrease
        employee.salary = 52000
        assert employee.salary == 52000

    def test_employee_benefits(self):
        """Test employee benefits management."""
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.ACTIVE
        )
        
        # Test benefits
        employee.benefits = {
            "health_insurance": True,
            "dental_insurance": True,
            "retirement_plan": "401k"
        }
        
        assert employee.benefits["health_insurance"] is True
        assert employee.benefits["retirement_plan"] == "401k"

    def test_employee_skills(self):
        """Test employee skills management."""
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.ACTIVE
        )
        
        # Test skills
        employee.skills = ["Python", "JavaScript", "SQL"]
        assert "Python" in employee.skills
        assert len(employee.skills) == 3

    def test_employee_validation(self):
        """Test employee validation rules."""
        # Test required fields
        with pytest.raises(IntegrityError):
            employee = Employee()
            # This would fail in actual database due to NOT NULL constraints

    def test_employee_string_representation(self):
        """Test employee string representation."""
        employee = Employee(
            user_id="user-uuid",
            employee_id="EMP001",
            employment_status=EmploymentStatus.ACTIVE,
            job_title="Software Engineer"
        )
        
        assert str(employee) == "EMP001 - Software Engineer"
        assert repr(employee) == "<Employee(employee_id='EMP001', job_title='Software Engineer')>"


class TestBaseModel:
    """Test BaseModel functionality."""

    def test_base_model_creation(self):
        """Test base model creation."""
        # Create a concrete model instance
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash"
        )
        
        # Test base model functionality
        assert hasattr(user, 'id')
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')
        assert hasattr(user, 'is_deleted') is False

    def test_base_model_to_dict(self):
        """Test base model to_dict method."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash"
        )
        
        user_dict = user.to_dict()
        assert isinstance(user_dict, dict)
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"

    def test_base_model_update_from_dict(self):
        """Test base model update_from_dict method."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash"
        )
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        user.update_from_dict(update_data)
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'

    def test_base_model_soft_delete(self):
        """Test base model soft delete functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash"
        )
        
        user.soft_delete()
        assert user.is_deleted is True
        assert user.deleted_at is not None

    def test_base_model_restore(self):
        """Test base model restore functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash"
        )
        
        user.soft_delete()
        user.restore()
        assert user.is_deleted is False
        assert user.deleted_at is None

    def test_base_model_audit_trail(self):
        """Test base model audit trail functionality."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hash"
        )
        
        # Test audit trail
        assert user.created_by is None
        assert user.updated_by is None
        
        # Simulate audit trail
        user.created_by = "system"
        user.updated_by = "admin"
        
        assert user.created_by == "system"
        assert user.updated_by == "admin"

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app.models.subscription import (
    SubscriptionPlan,
    PlanFeature,
    ModuleDefinition,
    DEFAULT_MODULES,
    DEFAULT_PLANS
)


class TestSubscriptionPlan:
    """Test cases for SubscriptionPlan model with comprehensive coverage."""

    @pytest.fixture
    def sample_plan_data(self):
        """Sample subscription plan data for testing."""
        return {
            "name": "Professional Plan",
            "plan_type": "professional",
            "description": "Professional plan for growing companies",
            "monthly_price": Decimal("99.99"),
            "yearly_price": Decimal("999.99"),
            "max_users": 25,
            "max_employees": 250,
            "max_storage_gb": 10,
            "enabled_modules": ["employees", "departments", "leave", "payroll"],
            "feature_flags": {
                "advanced_reporting": True,
                "api_access": True,
                "custom_branding": False
            },
            "trial_days": 14,
            "support_tier": "standard",
            "is_active": True
        }

    @pytest.fixture
    def sample_plan(self, sample_plan_data):
        """Create a sample subscription plan instance."""
        plan = SubscriptionPlan(**sample_plan_data)
        plan.id = 1
        plan.created_at = datetime(2024, 1, 1, 9, 0, 0)
        plan.updated_at = datetime(2024, 1, 1, 9, 0, 0)
        return plan

    def test_subscription_plan_creation(self, sample_plan_data):
        """Test subscription plan creation with valid data."""
        plan = SubscriptionPlan(**sample_plan_data)
        
        assert plan.name == "Professional Plan"
        assert plan.plan_type == "professional"
        assert plan.description == "Professional plan for growing companies"
        assert plan.monthly_price == Decimal("99.99")
        assert plan.yearly_price == Decimal("999.99")
        assert plan.max_users == 25
        assert plan.max_employees == 250
        assert plan.max_storage_gb == 10
        assert plan.enabled_modules == ["employees", "departments", "leave", "payroll"]
        assert plan.feature_flags["advanced_reporting"] is True
        assert plan.feature_flags["api_access"] is True
        assert plan.feature_flags["custom_branding"] is False
        assert plan.trial_days == 14
        assert plan.support_tier == "standard"
        assert plan.is_active is True

    def test_subscription_plan_default_values(self):
        """Test subscription plan creation with default values."""
        plan = SubscriptionPlan(
            name="Basic Plan",
            plan_type="basic"
        )
        
        assert plan.description == ""
        assert plan.monthly_price is None
        assert plan.yearly_price is None
        assert plan.max_users == 5
        assert plan.max_employees == 50
        assert plan.max_storage_gb == 1
        assert plan.enabled_modules == []
        assert plan.feature_flags == {}
        assert plan.trial_days == 0
        assert plan.support_tier == "basic"
        assert plan.is_active is True

    def test_subscription_plan_validation(self):
        """Test subscription plan validation."""
        # Test with invalid plan type
        with pytest.raises(ValueError):
            SubscriptionPlan(
                name="Invalid Plan",
                plan_type="invalid_type"
            )

    def test_subscription_plan_to_dict(self, sample_plan):
        """Test subscription plan to_dict method."""
        plan_dict = sample_plan.to_dict()
        
        assert isinstance(plan_dict, dict)
        assert plan_dict["id"] == 1
        assert plan_dict["name"] == "Professional Plan"
        assert plan_dict["plan_type"] == "professional"
        assert plan_dict["monthly_price"] == "99.99"
        assert plan_dict["yearly_price"] == "999.99"
        assert plan_dict["max_users"] == 25
        assert plan_dict["max_employees"] == 250
        assert plan_dict["max_storage_gb"] == 10
        assert plan_dict["enabled_modules"] == ["employees", "departments", "leave", "payroll"]
        assert plan_dict["feature_flags"]["advanced_reporting"] is True
        assert plan_dict["trial_days"] == 14
        assert plan_dict["support_tier"] == "standard"
        assert plan_dict["is_active"] is True
        assert "created_at" in plan_dict
        assert "updated_at" in plan_dict

    def test_subscription_plan_update_from_dict(self, sample_plan):
        """Test subscription plan update_from_dict method."""
        update_data = {
            "name": "Updated Professional Plan",
            "monthly_price": Decimal("129.99"),
            "max_users": 50,
            "feature_flags": {
                "advanced_reporting": True,
                "api_access": True,
                "custom_branding": True,
                "white_label": True
            }
        }
        
        sample_plan.update_from_dict(update_data)
        
        assert sample_plan.name == "Updated Professional Plan"
        assert sample_plan.monthly_price == Decimal("129.99")
        assert sample_plan.max_users == 50
        assert sample_plan.feature_flags["custom_branding"] is True
        assert sample_plan.feature_flags["white_label"] is True

    def test_subscription_plan_relationships(self, sample_plan):
        """Test subscription plan relationships."""
        # Mock relationships
        sample_plan.features = [Mock(), Mock()]
        sample_plan.tenants = [Mock(), Mock(), Mock()]
        
        assert len(sample_plan.features) == 2
        assert len(sample_plan.tenants) == 3

    def test_subscription_plan_str_representation(self, sample_plan):
        """Test subscription plan string representation."""
        str_repr = str(sample_plan)
        assert "Professional Plan" in str_repr
        assert "professional" in str_repr

    def test_subscription_plan_repr_representation(self, sample_plan):
        """Test subscription plan repr representation."""
        repr_str = repr(sample_plan)
        assert "SubscriptionPlan" in repr_str
        assert "Professional Plan" in repr_str
        assert "professional" in repr_str

    def test_subscription_plan_equality(self, sample_plan_data):
        """Test subscription plan equality."""
        plan1 = SubscriptionPlan(**sample_plan_data)
        plan2 = SubscriptionPlan(**sample_plan_data)
        plan1.id = 1
        plan2.id = 1
        
        assert plan1 == plan2
        
        plan2.id = 2
        assert plan1 != plan2

    def test_subscription_plan_hash(self, sample_plan):
        """Test subscription plan hash."""
        plan_hash = hash(sample_plan)
        assert isinstance(plan_hash, int)

    def test_subscription_plan_with_extreme_values(self):
        """Test subscription plan with extreme values."""
        extreme_data = {
            "name": "Extreme Plan",
            "plan_type": "enterprise",
            "max_users": 999999,
            "max_employees": 9999999,
            "max_storage_gb": 999999,
            "monthly_price": Decimal("999999.99"),
            "yearly_price": Decimal("9999999.99"),
            "trial_days": 365,
            "enabled_modules": ["module1", "module2", "module3"] * 100,  # Large list
            "feature_flags": {f"feature_{i}": True for i in range(1000)}  # Large dict
        }
        
        plan = SubscriptionPlan(**extreme_data)
        
        assert plan.max_users == 999999
        assert plan.max_employees == 9999999
        assert plan.max_storage_gb == 999999
        assert plan.monthly_price == Decimal("999999.99")
        assert plan.yearly_price == Decimal("9999999.99")
        assert plan.trial_days == 365
        assert len(plan.enabled_modules) == 300
        assert len(plan.feature_flags) == 1000

    def test_subscription_plan_with_special_characters(self):
        """Test subscription plan with special characters."""
        special_data = {
            "name": "Special & Characters Plan (v2.0)",
            "plan_type": "custom",
            "description": "Plan with special chars: &, ., (, ), -, +, @, #, $, %, ^, *, ~, `, |, \\, /, ?, <, >, [, ], {, }, ;, :, ', \", ,",
            "support_tier": "premium+",
            "enabled_modules": ["module-1", "module_2", "module.3", "module@4"],
            "feature_flags": {
                "feature-1": True,
                "feature_2": False,
                "feature.3": True,
                "feature@4": False
            }
        }
        
        plan = SubscriptionPlan(**special_data)
        
        assert plan.name == "Special & Characters Plan (v2.0)"
        assert "special chars: &, ., (, ), -, +, @, #, $, %, ^, *, ~, `, |, \\, /, ?, <, >, [, ], {, }, ;, :, ', \", ," in plan.description
        assert plan.support_tier == "premium+"
        assert "module-1" in plan.enabled_modules
        assert "module_2" in plan.enabled_modules
        assert "module.3" in plan.enabled_modules
        assert "module@4" in plan.enabled_modules
        assert plan.feature_flags["feature-1"] is True
        assert plan.feature_flags["feature_2"] is False
        assert plan.feature_flags["feature.3"] is True
        assert plan.feature_flags["feature@4"] is False


class TestPlanFeature:
    """Test cases for PlanFeature model with comprehensive coverage."""

    @pytest.fixture
    def sample_feature_data(self):
        """Sample plan feature data for testing."""
        return {
            "name": "Advanced Reporting",
            "description": "Advanced reporting and analytics features",
            "feature_type": "analytics",
            "is_active": True,
            "config": {
                "max_reports": 100,
                "export_formats": ["PDF", "Excel", "CSV"],
                "scheduling": True
            }
        }

    @pytest.fixture
    def sample_feature(self, sample_feature_data):
        """Create a sample plan feature instance."""
        feature = PlanFeature(**sample_feature_data)
        feature.id = 1
        feature.plan_id = 1
        feature.created_at = datetime(2024, 1, 1, 9, 0, 0)
        feature.updated_at = datetime(2024, 1, 1, 9, 0, 0)
        return feature

    def test_plan_feature_creation(self, sample_feature_data):
        """Test plan feature creation with valid data."""
        feature = PlanFeature(**sample_feature_data)
        
        assert feature.name == "Advanced Reporting"
        assert feature.description == "Advanced reporting and analytics features"
        assert feature.feature_type == "analytics"
        assert feature.is_active is True
        assert feature.config["max_reports"] == 100
        assert feature.config["export_formats"] == ["PDF", "Excel", "CSV"]
        assert feature.config["scheduling"] is True

    def test_plan_feature_default_values(self):
        """Test plan feature creation with default values."""
        feature = PlanFeature(
            name="Basic Feature",
            feature_type="basic"
        )
        
        assert feature.description == ""
        assert feature.is_active is True
        assert feature.config == {}

    def test_plan_feature_to_dict(self, sample_feature):
        """Test plan feature to_dict method."""
        feature_dict = sample_feature.to_dict()
        
        assert isinstance(feature_dict, dict)
        assert feature_dict["id"] == 1
        assert feature_dict["plan_id"] == 1
        assert feature_dict["name"] == "Advanced Reporting"
        assert feature_dict["feature_type"] == "analytics"
        assert feature_dict["config"]["max_reports"] == 100
        assert feature_dict["is_active"] is True

    def test_plan_feature_update_from_dict(self, sample_feature):
        """Test plan feature update_from_dict method."""
        update_data = {
            "name": "Updated Advanced Reporting",
            "config": {
                "max_reports": 200,
                "export_formats": ["PDF", "Excel", "CSV", "JSON"],
                "scheduling": True,
                "real_time": True
            }
        }
        
        sample_feature.update_from_dict(update_data)
        
        assert sample_feature.name == "Updated Advanced Reporting"
        assert sample_feature.config["max_reports"] == 200
        assert "JSON" in sample_feature.config["export_formats"]
        assert sample_feature.config["real_time"] is True

    def test_plan_feature_relationships(self, sample_feature):
        """Test plan feature relationships."""
        # Mock relationships
        sample_feature.plan = Mock()
        
        assert sample_feature.plan is not None

    def test_plan_feature_str_representation(self, sample_feature):
        """Test plan feature string representation."""
        str_repr = str(sample_feature)
        assert "Advanced Reporting" in str_repr
        assert "analytics" in str_repr


class TestModuleDefinition:
    """Test cases for ModuleDefinition model with comprehensive coverage."""

    @pytest.fixture
    def sample_module_data(self):
        """Sample module definition data for testing."""
        return {
            "name": "employees",
            "display_name": "Employee Management",
            "description": "Manage employee information and records",
            "version": "1.0.0",
            "is_active": True,
            "permissions": [
                "employees:read",
                "employees:create",
                "employees:update",
                "employees:delete"
            ],
            "features": [
                "employee_directory",
                "performance_tracking",
                "document_management"
            ],
            "dependencies": ["departments"],
            "config": {
                "max_employees": 1000,
                "file_upload_limit": "10MB",
                "audit_logging": True
            }
        }

    @pytest.fixture
    def sample_module(self, sample_module_data):
        """Create a sample module definition instance."""
        module = ModuleDefinition(**sample_module_data)
        module.id = 1
        module.created_at = datetime(2024, 1, 1, 9, 0, 0)
        module.updated_at = datetime(2024, 1, 1, 9, 0, 0)
        return module

    def test_module_definition_creation(self, sample_module_data):
        """Test module definition creation with valid data."""
        module = ModuleDefinition(**sample_module_data)
        
        assert module.name == "employees"
        assert module.display_name == "Employee Management"
        assert module.description == "Manage employee information and records"
        assert module.version == "1.0.0"
        assert module.is_active is True
        assert "employees:read" in module.permissions
        assert "employees:create" in module.permissions
        assert "employees:update" in module.permissions
        assert "employees:delete" in module.permissions
        assert "employee_directory" in module.features
        assert "performance_tracking" in module.features
        assert "document_management" in module.features
        assert "departments" in module.dependencies
        assert module.config["max_employees"] == 1000
        assert module.config["file_upload_limit"] == "10MB"
        assert module.config["audit_logging"] is True

    def test_module_definition_default_values(self):
        """Test module definition creation with default values."""
        module = ModuleDefinition(
            name="basic_module",
            display_name="Basic Module"
        )
        
        assert module.description == ""
        assert module.version == "1.0.0"
        assert module.is_active is True
        assert module.permissions == []
        assert module.features == []
        assert module.dependencies == []
        assert module.config == {}

    def test_module_definition_to_dict(self, sample_module):
        """Test module definition to_dict method."""
        module_dict = sample_module.to_dict()
        
        assert isinstance(module_dict, dict)
        assert module_dict["id"] == 1
        assert module_dict["name"] == "employees"
        assert module_dict["display_name"] == "Employee Management"
        assert module_dict["version"] == "1.0.0"
        assert module_dict["is_active"] is True
        assert "employees:read" in module_dict["permissions"]
        assert "employee_directory" in module_dict["features"]
        assert "departments" in module_dict["dependencies"]
        assert module_dict["config"]["max_employees"] == 1000

    def test_module_definition_update_from_dict(self, sample_module):
        """Test module definition update_from_dict method."""
        update_data = {
            "display_name": "Updated Employee Management",
            "version": "2.0.0",
            "permissions": [
                "employees:read",
                "employees:create",
                "employees:update",
                "employees:delete",
                "employees:export"
            ],
            "features": [
                "employee_directory",
                "performance_tracking",
                "document_management",
                "advanced_search"
            ],
            "config": {
                "max_employees": 2000,
                "file_upload_limit": "20MB",
                "audit_logging": True,
                "real_time_sync": True
            }
        }
        
        sample_module.update_from_dict(update_data)
        
        assert sample_module.display_name == "Updated Employee Management"
        assert sample_module.version == "2.0.0"
        assert "employees:export" in sample_module.permissions
        assert "advanced_search" in sample_module.features
        assert sample_module.config["max_employees"] == 2000
        assert sample_module.config["file_upload_limit"] == "20MB"
        assert sample_module.config["real_time_sync"] is True

    def test_module_definition_relationships(self, sample_module):
        """Test module definition relationships."""
        # Mock relationships
        sample_module.plans = [Mock(), Mock()]
        
        assert len(sample_module.plans) == 2

    def test_module_definition_str_representation(self, sample_module):
        """Test module definition string representation."""
        str_repr = str(sample_module)
        assert "employees" in str_repr
        assert "Employee Management" in str_repr

    def test_module_definition_repr_representation(self, sample_module):
        """Test module definition repr representation."""
        repr_str = repr(sample_module)
        assert "ModuleDefinition" in repr_str
        assert "employees" in repr_str

    def test_module_definition_equality(self, sample_module_data):
        """Test module definition equality."""
        module1 = ModuleDefinition(**sample_module_data)
        module2 = ModuleDefinition(**sample_module_data)
        module1.id = 1
        module2.id = 1
        
        assert module1 == module2
        
        module2.id = 2
        assert module1 != module2

    def test_module_definition_hash(self, sample_module):
        """Test module definition hash."""
        module_hash = hash(sample_module)
        assert isinstance(module_hash, int)

    def test_module_definition_with_extreme_values(self):
        """Test module definition with extreme values."""
        extreme_data = {
            "name": "extreme_module",
            "display_name": "Extreme Module",
            "permissions": [f"permission_{i}" for i in range(1000)],  # Large permissions list
            "features": [f"feature_{i}" for i in range(1000)],  # Large features list
            "dependencies": [f"dependency_{i}" for i in range(100)],  # Large dependencies list
            "config": {f"config_key_{i}": f"config_value_{i}" for i in range(500)}  # Large config dict
        }
        
        module = ModuleDefinition(**extreme_data)
        
        assert len(module.permissions) == 1000
        assert len(module.features) == 1000
        assert len(module.dependencies) == 100
        assert len(module.config) == 500

    def test_module_definition_with_special_characters(self):
        """Test module definition with special characters."""
        special_data = {
            "name": "special-module_1.0",
            "display_name": "Special & Characters Module (v2.0)",
            "description": "Module with special chars: &, ., (, ), -, +, @, #, $, %, ^, *, ~, `, |, \\, /, ?, <, >, [, ], {, }, ;, :, ', \", ,",
            "permissions": [
                "module:read",
                "module:create",
                "module:update",
                "module:delete",
                "module:export",
                "module:import"
            ],
            "features": [
                "feature-1",
                "feature_2",
                "feature.3",
                "feature@4"
            ],
            "dependencies": [
                "dependency-1",
                "dependency_2",
                "dependency.3"
            ],
            "config": {
                "config-key-1": "config-value-1",
                "config_key_2": "config-value-2",
                "config.3": "config-value-3",
                "config@4": "config-value-4"
            }
        }
        
        module = ModuleDefinition(**special_data)
        
        assert module.name == "special-module_1.0"
        assert module.display_name == "Special & Characters Module (v2.0)"
        assert "special chars: &, ., (, ), -, +, @, #, $, %, ^, *, ~, `, |, \\, /, ?, <, >, [, ], {, }, ;, :, ', \", ," in module.description
        assert "module:export" in module.permissions
        assert "module:import" in module.permissions
        assert "feature-1" in module.features
        assert "feature_2" in module.features
        assert "feature.3" in module.features
        assert "feature@4" in module.features
        assert "dependency-1" in module.dependencies
        assert "dependency_2" in module.dependencies
        assert "dependency.3" in module.dependencies
        assert module.config["config-key-1"] == "config-value-1"
        assert module.config["config_key_2"] == "config-value-2"
        assert module.config["config.3"] == "config-value-3"
        assert module.config["config@4"] == "config-value-4"


class TestDefaultData:
    """Test cases for default modules and plans data."""

    def test_default_modules_structure(self):
        """Test that default modules have correct structure."""
        for module in DEFAULT_MODULES:
            assert "name" in module
            assert "display_name" in module
            assert "description" in module
            assert "version" in module
            assert "is_active" in module
            assert "permissions" in module
            assert "features" in module
            assert "dependencies" in module
            assert "config" in module
            
            # Validate data types
            assert isinstance(module["name"], str)
            assert isinstance(module["display_name"], str)
            assert isinstance(module["description"], str)
            assert isinstance(module["version"], str)
            assert isinstance(module["is_active"], bool)
            assert isinstance(module["permissions"], list)
            assert isinstance(module["features"], list)
            assert isinstance(module["dependencies"], list)
            assert isinstance(module["config"], dict)

    def test_default_plans_structure(self):
        """Test that default plans have correct structure."""
        for plan in DEFAULT_PLANS:
            assert "name" in plan
            assert "plan_type" in plan
            assert "description" in plan
            assert "monthly_price" in plan
            assert "yearly_price" in plan
            assert "max_users" in plan
            assert "max_employees" in plan
            assert "max_storage_gb" in plan
            assert "enabled_modules" in plan
            assert "feature_flags" in plan
            assert "trial_days" in plan
            assert "support_tier" in plan
            assert "is_active" in plan
            
            # Validate data types
            assert isinstance(plan["name"], str)
            assert isinstance(plan["plan_type"], str)
            assert isinstance(plan["description"], str)
            assert isinstance(plan["monthly_price"], (int, type(None)))
            assert isinstance(plan["yearly_price"], (int, type(None)))
            assert isinstance(plan["max_users"], int)
            assert isinstance(plan["max_employees"], int)
            assert isinstance(plan["max_storage_gb"], int)
            assert isinstance(plan["enabled_modules"], list)
            assert isinstance(plan["feature_flags"], dict)
            assert isinstance(plan["trial_days"], int)
            assert isinstance(plan["support_tier"], str)
            assert isinstance(plan["is_active"], bool)

    def test_default_modules_unique_names(self):
        """Test that default modules have unique names."""
        module_names = [module["name"] for module in DEFAULT_MODULES]
        assert len(module_names) == len(set(module_names))

    def test_default_plans_unique_names(self):
        """Test that default plans have unique names."""
        plan_names = [plan["name"] for plan in DEFAULT_PLANS]
        assert len(plan_names) == len(set(plan_names))

    def test_default_modules_valid_permissions(self):
        """Test that default modules have valid permission formats."""
        for module in DEFAULT_MODULES:
            for permission in module["permissions"]:
                assert ":" in permission  # Should have format "module:action"
                parts = permission.split(":")
                assert len(parts) == 2
                assert parts[0] == module["name"]  # Permission should match module name

    def test_default_plans_valid_module_references(self):
        """Test that default plans reference valid modules."""
        valid_modules = {module["name"] for module in DEFAULT_MODULES}
        
        for plan in DEFAULT_PLANS:
            for module_name in plan["enabled_modules"]:
                assert module_name in valid_modules, f"Plan {plan['name']} references unknown module {module_name}"

    def test_default_plans_price_consistency(self):
        """Test that default plans have consistent pricing."""
        for plan in DEFAULT_PLANS:
            if plan["monthly_price"] is not None and plan["yearly_price"] is not None:
                # Yearly price should be approximately 10x monthly price (with some flexibility)
                monthly = plan["monthly_price"]
                yearly = plan["yearly_price"]
                ratio = yearly / monthly
                assert 9 <= ratio <= 12, f"Plan {plan['name']} has unusual yearly/monthly ratio: {ratio}"

    def test_default_plans_limits_consistency(self):
        """Test that default plans have consistent limits."""
        for plan in DEFAULT_PLANS:
            # Higher tier plans should have higher limits
            if plan["plan_type"] == "basic":
                assert plan["max_users"] <= 10
                assert plan["max_employees"] <= 100
                assert plan["max_storage_gb"] <= 5
            elif plan["plan_type"] == "professional":
                assert plan["max_users"] <= 50
                assert plan["max_employees"] <= 500
                assert plan["max_storage_gb"] <= 20
            elif plan["plan_type"] == "enterprise":
                assert plan["max_users"] >= 100
                assert plan["max_employees"] >= 1000
                assert plan["max_storage_gb"] >= 50

    def test_default_data_security(self):
        """Test that default data doesn't contain security vulnerabilities."""
        # Check for potential SQL injection patterns
        sql_patterns = ["DROP", "DELETE", "INSERT", "UPDATE", "SELECT", "UNION", "EXEC", "EXECUTE"]
        
        for module in DEFAULT_MODULES:
            for pattern in sql_patterns:
                assert pattern not in str(module).upper()
        
        for plan in DEFAULT_PLANS:
            for pattern in sql_patterns:
                assert pattern not in str(plan).upper()

    def test_default_data_xss_prevention(self):
        """Test that default data doesn't contain XSS vulnerabilities."""
        xss_patterns = ["<script>", "javascript:", "onload=", "onerror=", "onclick="]
        
        for module in DEFAULT_MODULES:
            for pattern in xss_patterns:
                assert pattern not in str(module).lower()
        
        for plan in DEFAULT_PLANS:
            for pattern in xss_patterns:
                assert pattern not in str(plan).lower()

    def test_default_data_integrity(self):
        """Test that default data maintains referential integrity."""
        # All modules referenced in plans should exist
        valid_modules = {module["name"] for module in DEFAULT_MODULES}
        
        for plan in DEFAULT_PLANS:
            for module_name in plan["enabled_modules"]:
                assert module_name in valid_modules, f"Plan {plan['name']} references non-existent module {module_name}"
        
        # All module dependencies should exist
        for module in DEFAULT_MODULES:
            for dependency in module["dependencies"]:
                assert dependency in valid_modules, f"Module {module['name']} depends on non-existent module {dependency}"

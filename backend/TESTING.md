# HRMS-SAAS Backend Testing Guide

This document provides comprehensive information about testing the HRMS-SAAS backend, including unit tests, integration tests, security scanning, and coverage requirements.

## 🎯 Testing Goals

- **100% Code Coverage**: Ensure all code paths are tested
- **Security First**: Comprehensive security scanning and vulnerability testing
- **Quality Assurance**: Maintain high code quality through linting and formatting
- **Performance**: Ensure tests run efficiently and provide quick feedback

## 🏗️ Testing Architecture

### Test Structure
```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_config.py      # Configuration tests
│   ├── test_security.py    # Security component tests
│   ├── test_database.py    # Database layer tests
│   ├── test_models.py      # Data model tests
│   ├── test_tenant_service.py  # Tenant service tests
│   └── test_subscription_models.py  # Subscription model tests
├── api/                     # API endpoint tests
│   └── v1/
│       ├── test_api_auth.py    # Authentication API tests
│       ├── test_tenants_api.py # Tenant API tests
│       └── test_employees_api.py # Employee API tests
├── integration/             # Integration tests
└── conftest.py             # Test configuration and fixtures
```

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and methods
   - Mock external dependencies
   - Fast execution (< 1 second per test)
   - High isolation

2. **API Tests** (`tests/api/`)
   - Test HTTP endpoints
   - Validate request/response formats
   - Test authentication and authorization
   - Test error handling

3. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use test database
   - Test real workflows
   - Slower execution

## 🚀 Getting Started

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Verify installation
python -c "import pytest, bandit, safety, black, isort, flake8, mypy; print('All tools installed!')"
```

### Running Tests

#### Quick Test Run
```bash
# Run all tests with coverage
python run_tests.py

# Run specific test types
python run_tests.py --test-type unit
python run_tests.py --test-type api
python run_tests.py --test-type integration
```

#### Manual Test Execution
```bash
# Run all tests
pytest tests/ -v --cov=app --cov-report=html

# Run specific test files
pytest tests/unit/test_tenant_service.py -v

# Run tests with specific markers
pytest tests/ -m "tenant" -v
pytest tests/ -m "security" -v

# Run tests in parallel
pytest tests/ -n auto
```

#### Code Quality Checks
```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy app/

# Security scan
bandit -r app/
safety check
```

## 📊 Coverage Requirements

### Minimum Coverage: 95%

- **Line Coverage**: 95% of all code lines must be executed
- **Branch Coverage**: 95% of all code branches must be tested
- **Function Coverage**: 95% of all functions must be called

### Coverage Reports

After running tests, coverage reports are generated in:
- `coverage.xml` - XML format for CI/CD integration
- `coverage_html/` - HTML report for browser viewing
- Terminal output - Summary in console

### Coverage Exclusions

The following are excluded from coverage:
- Test files themselves
- Migration files
- Configuration files
- Debug/development code

## 🔒 Security Testing

### Security Tools

1. **Bandit** - Python security linter
   - Detects common security issues
   - Configurable rule sets
   - JSON output for CI/CD

2. **Safety** - Dependency vulnerability scanner
   - Checks known vulnerabilities
   - Monitors package updates
   - Generates security reports

3. **Custom Security Tests**
   - SQL injection prevention
   - XSS protection
   - Authentication bypass testing
   - Authorization testing

### Security Test Categories

- **Input Validation**: Test malicious input handling
- **Authentication**: Test login/logout flows
- **Authorization**: Test permission enforcement
- **Data Protection**: Test encryption and privacy
- **API Security**: Test endpoint security

## 🧪 Test Writing Guidelines

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestComponentName:
    """Test cases for ComponentName with comprehensive coverage."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {"key": "value"}
    
    def test_success_case(self, sample_data):
        """Test successful operation."""
        # Arrange
        component = Component()
        
        # Act
        result = component.process(sample_data)
        
        # Assert
        assert result is not None
        assert result["key"] == "value"
    
    def test_error_case(self):
        """Test error handling."""
        # Arrange
        component = Component()
        
        # Act & Assert
        with pytest.raises(ValueError):
            component.process(None)
```

### Test Naming Conventions

- **Test Classes**: `Test{ComponentName}`
- **Test Methods**: `test_{scenario}_{expected_result}`
- **Fixtures**: Descriptive names like `sample_tenant_data`

### Test Data Management

- Use fixtures for reusable test data
- Create realistic but minimal test data
- Use factories for complex object creation
- Clean up test data after each test

### Mocking Guidelines

- Mock external dependencies (databases, APIs)
- Mock time-dependent operations
- Mock random operations for deterministic tests
- Use `unittest.mock.patch` for dependency injection

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = --strict-markers --strict-config --verbose --cov=app
markers = unit, integration, api, security, tenant, subscription
```

### Coverage Configuration

```ini
[coverage:run]
source = app
omit = */tests/*, */migrations/*, */__pycache__/*

[coverage:report]
exclude_lines = pragma: no cover, def __repr__, if settings.DEBUG
```

## 📈 Performance Testing

### Test Execution Time

- **Unit Tests**: < 1 second per test
- **API Tests**: < 5 seconds per test
- **Integration Tests**: < 30 seconds per test
- **Full Test Suite**: < 5 minutes

### Performance Monitoring

- Use `pytest-benchmark` for performance tests
- Monitor test execution time trends
- Set performance regression thresholds
- Profile slow tests for optimization

## 🚨 Common Issues and Solutions

### Import Errors
```bash
# Solution: Install test dependencies
pip install -r requirements-test.txt

# Or install specific packages
pip install pytest pytest-asyncio pytest-cov
```

### Database Connection Issues
```bash
# Solution: Check test database configuration
# Ensure test database is running
# Check connection strings in test config
```

### Coverage Issues
```bash
# Solution: Check coverage exclusions
# Ensure all code paths are reachable
# Add missing test cases
```

### Security Scan Failures
```bash
# Solution: Review security warnings
# Fix identified vulnerabilities
# Update dependencies if needed
# Add security test cases
```

## 🔄 Continuous Integration

### GitHub Actions Integration

Tests are automatically run on:
- Pull requests
- Push to main branch
- Scheduled security scans

### CI Pipeline Steps

1. **Code Quality**
   - Format checking (Black)
   - Import sorting (isort)
   - Linting (Flake8)
   - Type checking (MyPy)

2. **Security Scanning**
   - Bandit security scan
   - Safety vulnerability check
   - Dependency audit

3. **Testing**
   - Unit tests with coverage
   - API tests
   - Integration tests

4. **Reporting**
   - Coverage reports
   - Security reports
   - Test results

## 📚 Additional Resources

### Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Bandit Security Tool](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)

### Best Practices
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

### Tools and Extensions
- **VS Code**: Python Test Explorer extension
- **PyCharm**: Built-in test runner
- **Jupyter**: Test notebooks for data science components

## 🤝 Contributing to Tests

### Adding New Tests

1. **Identify Component**: Determine what needs testing
2. **Create Test File**: Follow naming conventions
3. **Write Test Cases**: Cover all scenarios
4. **Add Markers**: Use appropriate test markers
5. **Update Coverage**: Ensure new code is covered

### Test Review Checklist

- [ ] Tests cover all code paths
- [ ] Error cases are tested
- [ ] Edge cases are handled
- [ ] Tests are readable and maintainable
- [ ] Performance requirements are met
- [ ] Security considerations are addressed

### Reporting Issues

When reporting test issues, include:
- Test file and method name
- Error message and stack trace
- Environment details (Python version, OS)
- Steps to reproduce
- Expected vs actual behavior

## 🎉 Success Metrics

### Quality Indicators

- **Coverage**: Maintain 95%+ coverage
- **Security**: Zero high-severity vulnerabilities
- **Performance**: Tests complete within time limits
- **Reliability**: Tests pass consistently

### Continuous Improvement

- Regular test maintenance
- Performance optimization
- Security rule updates
- Coverage gap analysis
- Test automation improvements

---

**Remember**: Good tests are the foundation of reliable software. Write tests that are comprehensive, maintainable, and provide confidence in your code quality.

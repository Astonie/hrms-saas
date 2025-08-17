#!/usr/bin/env python3
"""
Comprehensive Test Runner for HRMS-SAAS Backend
Runs unit tests, integration tests, security scans, and generates coverage reports.
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """Comprehensive test runner for the HRMS-SAAS backend."""
    
    def __init__(self, verbose: bool = False, coverage: bool = True, security: bool = True):
        self.verbose = verbose
        self.coverage = coverage
        self.security = security
        self.project_root = Path(__file__).parent
        self.test_results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command: List[str], description: str, cwd: Path = None) -> bool:
        """Run a shell command and return success status."""
        self.log(f"Running: {description}")
        if self.verbose:
            self.log(f"Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=not self.verbose,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                self.log(f"✓ {description} completed successfully", "SUCCESS")
                if not self.verbose and result.stdout:
                    print(result.stdout)
                return True
            else:
                self.log(f"✗ {description} failed with exit code {result.returncode}", "ERROR")
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"✗ {description} failed with exception: {e}", "ERROR")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed."""
        self.log("Checking dependencies...")
        
        required_packages = [
            "pytest", "pytest-asyncio", "pytest-cov", "coverage",
            "bandit", "safety", "black", "isort", "flake8", "mypy"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
            self.log("Please install missing packages: pip install -r requirements-test.txt", "ERROR")
            return False
        
        self.log("✓ All dependencies are available", "SUCCESS")
        return True
    
    def run_code_formatting(self) -> bool:
        """Run code formatting checks and fixes."""
        self.log("Running code formatting checks...")
        
        # Check if code is properly formatted
        if not self.run_command(
            ["black", "--check", "--diff", "."],
            "Black formatting check"
        ):
            self.log("Code formatting issues found. Running auto-format...", "WARNING")
            if not self.run_command(["black", "."], "Black auto-format"):
                return False
        
        # Check import sorting
        if not self.run_command(
            ["isort", "--check-only", "--diff", "."],
            "Import sorting check"
        ):
            self.log("Import sorting issues found. Running auto-sort...", "WARNING")
            if not self.run_command(["isort", "."], "Import auto-sort"):
                return False
        
        self.log("✓ Code formatting completed", "SUCCESS")
        return True
    
    def run_linting(self) -> bool:
        """Run code linting checks."""
        self.log("Running code linting...")
        
        # Flake8 linting
        if not self.run_command(
            ["flake8", ".", "--max-line-length=100", "--extend-ignore=E203,W503"],
            "Flake8 linting"
        ):
            return False
        
        # MyPy type checking
        if not self.run_command(
            ["mypy", "app/", "--ignore-missing-imports", "--no-strict-optional"],
            "MyPy type checking"
        ):
            return False
        
        self.log("✓ Code linting completed", "SUCCESS")
        return True
    
    def run_security_scanning(self) -> bool:
        """Run security scanning tools."""
        if not self.security:
            self.log("Security scanning disabled", "INFO")
            return True
        
        self.log("Running security scanning...")
        
        # Bandit security scanning
        if not self.run_command(
            ["bandit", "-r", "app/", "-f", "json", "-o", "bandit-report.json"],
            "Bandit security scan"
        ):
            return False
        
        # Safety dependency vulnerability check
        if not self.run_command(
            ["safety", "check", "--json", "--output", "safety-report.json"],
            "Safety vulnerability check"
        ):
            return False
        
        self.log("✓ Security scanning completed", "SUCCESS")
        return True
    
    def run_unit_tests(self) -> bool:
        """Run unit tests with coverage."""
        self.log("Running unit tests...")
        
        pytest_args = [
            "python", "-m", "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            "--maxfail=5"
        ]
        
        if self.coverage:
            pytest_args.extend([
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-report=xml",
                "--cov-branch",
                "--cov-fail-under=95"
            ])
        
        if not self.run_command(pytest_args, "Unit tests"):
            return False
        
        self.log("✓ Unit tests completed", "SUCCESS")
        return True
    
    def run_integration_tests(self) -> bool:
        """Run integration tests."""
        self.log("Running integration tests...")
        
        if not self.run_command(
            ["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"],
            "Integration tests"
        ):
            return False
        
        self.log("✓ Integration tests completed", "SUCCESS")
        return True
    
    def run_api_tests(self) -> bool:
        """Run API tests."""
        self.log("Running API tests...")
        
        if not self.run_command(
            ["python", "-m", "pytest", "tests/api/", "-v", "--tb=short"],
            "API tests"
        ):
            return False
        
        self.log("✓ API tests completed", "SUCCESS")
        return True
    
    def run_all_tests(self) -> bool:
        """Run all tests."""
        self.log("Running all tests...")
        
        pytest_args = [
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--maxfail=10"
        ]
        
        if self.coverage:
            pytest_args.extend([
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-report=xml",
                "--cov-branch",
                "--cov-fail-under=95"
            ])
        
        if not self.run_command(pytest_args, "All tests"):
            return False
        
        self.log("✓ All tests completed", "SUCCESS")
        return True
    
    def generate_test_report(self) -> None:
        """Generate a comprehensive test report."""
        self.log("Generating test report...")
        
        report_file = self.project_root / "test-report.md"
        
        with open(report_file, "w") as f:
            f.write("# HRMS-SAAS Backend Test Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Test Summary\n\n")
            f.write("| Component | Status | Details |\n")
            f.write("|-----------|--------|---------|\n")
            
            for component, result in self.test_results.items():
                status = "✓ PASS" if result else "✗ FAIL"
                f.write(f"| {component} | {status} | |\n")
            
            f.write("\n## Coverage Report\n\n")
            if self.coverage and (self.project_root / "coverage.xml").exists():
                f.write("Coverage report generated in `coverage.xml`\n")
                f.write("HTML coverage report available in `coverage_html/`\n")
            
            f.write("\n## Security Report\n\n")
            if self.security:
                if (self.project_root / "bandit-report.json").exists():
                    f.write("Security scan report available in `bandit-report.json`\n")
                if (self.project_root / "safety-report.json").exists():
                    f.write("Vulnerability report available in `safety-report.json`\n")
            
            f.write("\n## Next Steps\n\n")
            f.write("1. Review any failed tests and fix issues\n")
            f.write("2. Check coverage reports for untested code\n")
            f.write("3. Review security scan results\n")
            f.write("4. Run tests again to ensure all issues are resolved\n")
        
        self.log(f"✓ Test report generated: {report_file}", "SUCCESS")
    
    def run(self, test_type: str = "all") -> bool:
        """Run the specified test suite."""
        self.log(f"Starting {test_type} test suite...")
        
        # Check dependencies first
        if not self.check_dependencies():
            return False
        
        # Run code quality checks
        if not self.run_code_formatting():
            return False
        
        if not self.run_linting():
            return False
        
        # Run security scanning
        if not self.run_security_scanning():
            return False
        
        # Run tests based on type
        if test_type == "unit":
            success = self.run_unit_tests()
        elif test_type == "integration":
            success = self.run_integration_tests()
        elif test_type == "api":
            success = self.run_api_tests()
        elif test_type == "all":
            success = self.run_all_tests()
        else:
            self.log(f"Unknown test type: {test_type}", "ERROR")
            return False
        
        # Generate report
        self.generate_test_report()
        
        if success:
            self.log("🎉 All tests completed successfully!", "SUCCESS")
        else:
            self.log("💥 Some tests failed. Please review the report.", "ERROR")
        
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="HRMS-SAAS Backend Test Runner")
    parser.add_argument(
        "--test-type",
        choices=["unit", "integration", "api", "all"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--no-security",
        action="store_true",
        help="Disable security scanning"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(
        verbose=args.verbose,
        coverage=not args.no_coverage,
        security=not args.no_security
    )
    
    success = runner.run(args.test_type)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

"""
HRMS-SAAS Implementation Summary

This script creates sample data for testing the HRMS system features.
Run this after the main setup to populate the database with realistic data.
"""

import asyncio
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_session
from app.models.user import User, UserType
from app.models.tenant import Tenant
from app.models.employee import Employee, Department, EmploymentStatus, EmploymentType, MaritalStatus
from app.models.leave import LeaveRequest, LeaveBalance, LeaveType, LeaveStatus
from app.core.security import hash_password
from sqlalchemy import select
import uuid


async def create_sample_data():
    """Create comprehensive sample data for HRMS testing."""
    
    async for db in get_session():
        try:
            print("Creating sample HRMS data...")
            
            # Get existing demo tenant
            tenant_result = await db.execute(select(Tenant).where(Tenant.name == "Demo Tenant"))
            tenant = tenant_result.scalar_one_or_none()
            
            if not tenant:
                print("Demo tenant not found. Please run setup_db.py first.")
                return
            
            # Create departments
            departments_data = [
                {"name": "Human Resources", "code": "HR", "description": "Human Resources Department"},
                {"name": "Information Technology", "code": "IT", "description": "Technology and Development"},
                {"name": "Finance", "code": "FIN", "description": "Finance and Accounting"},
                {"name": "Marketing", "code": "MKT", "description": "Marketing and Communications"},
                {"name": "Operations", "code": "OPS", "description": "Operations and Logistics"},
                {"name": "Sales", "code": "SALES", "description": "Sales and Business Development"}
            ]
            
            departments = []
            for dept_data in departments_data:
                # Check if department exists
                existing = await db.execute(
                    select(Department).where(
                        Department.tenant_id == tenant.id,
                        Department.code == dept_data["code"]
                    )
                )
                if not existing.scalar_one_or_none():
                    department = Department(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant.id,
                        **dept_data,
                        is_active=True,
                        budget=Decimal("50000.00"),
                        location="Main Office"
                    )
                    db.add(department)
                    departments.append(department)
                    print(f"Created department: {dept_data['name']}")
            
            await db.commit()
            
            # Create sample employees
            sample_employees = [
                {
                    "username": "john.smith", "email": "john.smith@demo.com", "first_name": "John", "last_name": "Smith",
                    "employee_id": "EMP001", "job_title": "HR Manager", "department_code": "HR",
                    "employment_status": EmploymentStatus.ACTIVE, "employment_type": EmploymentType.FULL_TIME,
                    "hire_date": date(2023, 1, 15), "base_salary": Decimal("75000.00"),
                    "date_of_birth": date(1985, 6, 12), "phone": "+1-555-0101"
                },
                {
                    "username": "sarah.johnson", "email": "sarah.johnson@demo.com", "first_name": "Sarah", "last_name": "Johnson",
                    "employee_id": "EMP002", "job_title": "Software Developer", "department_code": "IT",
                    "employment_status": EmploymentStatus.ACTIVE, "employment_type": EmploymentType.FULL_TIME,
                    "hire_date": date(2023, 2, 1), "base_salary": Decimal("85000.00"),
                    "date_of_birth": date(1990, 3, 22), "phone": "+1-555-0102"
                },
                {
                    "username": "mike.davis", "email": "mike.davis@demo.com", "first_name": "Mike", "last_name": "Davis",
                    "employee_id": "EMP003", "job_title": "Financial Analyst", "department_code": "FIN",
                    "employment_status": EmploymentStatus.ACTIVE, "employment_type": EmploymentType.FULL_TIME,
                    "hire_date": date(2023, 3, 10), "base_salary": Decimal("70000.00"),
                    "date_of_birth": date(1988, 9, 5), "phone": "+1-555-0103"
                },
                {
                    "username": "lisa.wilson", "email": "lisa.wilson@demo.com", "first_name": "Lisa", "last_name": "Wilson",
                    "employee_id": "EMP004", "job_title": "Marketing Specialist", "department_code": "MKT",
                    "employment_status": EmploymentStatus.ACTIVE, "employment_type": EmploymentType.FULL_TIME,
                    "hire_date": date(2023, 4, 5), "base_salary": Decimal("65000.00"),
                    "date_of_birth": date(1992, 11, 18), "phone": "+1-555-0104"
                },
                {
                    "username": "robert.brown", "email": "robert.brown@demo.com", "first_name": "Robert", "last_name": "Brown",
                    "employee_id": "EMP005", "job_title": "Operations Manager", "department_code": "OPS",
                    "employment_status": EmploymentStatus.ACTIVE, "employment_type": EmploymentType.FULL_TIME,
                    "hire_date": date(2023, 5, 20), "base_salary": Decimal("80000.00"),
                    "date_of_birth": date(1980, 7, 30), "phone": "+1-555-0105"
                },
                {
                    "username": "emily.garcia", "email": "emily.garcia@demo.com", "first_name": "Emily", "last_name": "Garcia",
                    "employee_id": "EMP006", "job_title": "Sales Representative", "department_code": "SALES",
                    "employment_status": EmploymentStatus.ACTIVE, "employment_type": EmploymentType.FULL_TIME,
                    "hire_date": date(2023, 6, 1), "base_salary": Decimal("60000.00"),
                    "date_of_birth": date(1995, 4, 14), "phone": "+1-555-0106"
                }
            ]
            
            employees = []
            for emp_data in sample_employees:
                # Check if user exists
                existing_user = await db.execute(
                    select(User).where(User.username == emp_data["username"])
                )
                if existing_user.scalar_one_or_none():
                    continue
                
                # Find department
                dept_result = await db.execute(
                    select(Department).where(
                        Department.tenant_id == tenant.id,
                        Department.code == emp_data["department_code"]
                    )
                )
                department = dept_result.scalar_one_or_none()
                
                # Create user
                user = User(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    username=emp_data["username"],
                    email=emp_data["email"],
                    first_name=emp_data["first_name"],
                    last_name=emp_data["last_name"],
                    hashed_password=hash_password("password123"),
                    user_type=UserType.EMPLOYEE,
                    is_active=True
                )
                db.add(user)
                await db.flush()  # Get the user ID
                
                # Create employee
                employee = Employee(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    user_id=user.id,
                    employee_id=emp_data["employee_id"],
                    employment_status=emp_data["employment_status"],
                    employment_type=emp_data["employment_type"],
                    hire_date=emp_data["hire_date"],
                    job_title=emp_data["job_title"],
                    department_id=department.id if department else None,
                    base_salary=emp_data["base_salary"],
                    currency="USD",
                    pay_frequency="monthly",
                    date_of_birth=emp_data["date_of_birth"],
                    phone=emp_data["phone"],
                    marital_status=MaritalStatus.SINGLE,
                    gender="Not specified",
                    address="123 Main St",
                    city="Anytown",
                    state="State",
                    postal_code="12345",
                    country="USA",
                    is_active=True
                )
                db.add(employee)
                employees.append(employee)
                print(f"Created employee: {emp_data['first_name']} {emp_data['last_name']}")
            
            await db.commit()
            
            # Create leave balances for all employees
            leave_types = [LeaveType.ANNUAL, LeaveType.SICK, LeaveType.PERSONAL]
            current_year = datetime.now().year
            
            for employee in employees:
                for leave_type in leave_types:
                    # Set different balance amounts based on leave type
                    if leave_type == LeaveType.ANNUAL:
                        total_days = 21.0
                    elif leave_type == LeaveType.SICK:
                        total_days = 10.0
                    else:  # PERSONAL
                        total_days = 5.0
                    
                    balance = LeaveBalance(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant.id,
                        employee_id=employee.id,
                        leave_type=leave_type,
                        year=current_year,
                        total_days=total_days,
                        used_days=0.0,
                        pending_days=0.0,
                        carried_over_days=0.0,
                        max_carry_over=5.0
                    )
                    db.add(balance)
            
            await db.commit()
            
            # Create sample leave requests
            if employees:
                sample_requests = [
                    {
                        "employee": employees[0],
                        "leave_type": LeaveType.ANNUAL,
                        "start_date": date.today() + timedelta(days=10),
                        "end_date": date.today() + timedelta(days=12),
                        "reason": "Family vacation",
                        "status": LeaveStatus.PENDING
                    },
                    {
                        "employee": employees[1],
                        "leave_type": LeaveType.SICK,
                        "start_date": date.today() - timedelta(days=2),
                        "end_date": date.today() - timedelta(days=1),
                        "reason": "Medical appointment",
                        "status": LeaveStatus.APPROVED
                    },
                    {
                        "employee": employees[2],
                        "leave_type": LeaveType.PERSONAL,
                        "start_date": date.today() + timedelta(days=5),
                        "end_date": date.today() + timedelta(days=5),
                        "reason": "Personal matters",
                        "status": LeaveStatus.PENDING
                    }
                ]
                
                for req_data in sample_requests:
                    leave_request = LeaveRequest(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant.id,
                        employee_id=req_data["employee"].id,
                        leave_type=req_data["leave_type"],
                        start_date=req_data["start_date"],
                        end_date=req_data["end_date"],
                        reason=req_data["reason"],
                        status=req_data["status"],
                        requested_days=(req_data["end_date"] - req_data["start_date"]).days + 1,
                        is_half_day=False
                    )
                    db.add(leave_request)
                    print(f"Created leave request for {req_data['employee'].user.first_name}")
            
            await db.commit()
            print("\n✅ Sample data created successfully!")
            print("\nSample Login Credentials:")
            print("- admin / admin123 / demo (Admin user)")
            print("- john.smith / password123 / demo (HR Manager)")
            print("- sarah.johnson / password123 / demo (Software Developer)")
            print("- mike.davis / password123 / demo (Financial Analyst)")
            print("\nThe system now has:")
            print(f"- {len(departments_data)} departments")
            print(f"- {len(sample_employees)} employees")
            print(f"- Leave balances for all employees")
            print(f"- Sample leave requests")
            
        except Exception as e:
            await db.rollback()
            print(f"Error creating sample data: {e}")
            raise
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(create_sample_data())

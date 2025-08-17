#!/usr/bin/env python3
"""
Simple data seeder using ORM models for HRMS-SAAS.
"""

import asyncio
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import select, func

from app.core.database import get_async_session
from app.models.tenant import Tenant
from app.models.employee import Employee, Department
from app.models.user import User, UserType

async def create_enterprise_test_data():
    """Create basic data using ORM models."""
    try:
        print("🌱 Creating enterprise test data with ORM models...")
        
        async for db in get_async_session():
            # Get demo tenant
            result = await db.execute(select(Tenant).where(Tenant.slug == "demo"))
            tenant = result.scalar_one_or_none()
            if not tenant:
                print("❌ Demo tenant not found")
                return
            
            print(f"✅ Using tenant: {tenant.name} (ID: {tenant.id})")
            
            # Check existing data
            dept_count = await db.scalar(select(func.count(Department.id)))
            print(f"📁 Existing departments: {dept_count}")
            
            user_count = await db.scalar(select(func.count(User.id)))
            print(f"👥 Existing users: {user_count}")
            
            employee_count = await db.scalar(select(func.count(Employee.id)))
            print(f"💼 Existing employees: {employee_count}")
            
            # Create departments if needed
            if dept_count == 0:
                print("📁 Creating departments...")
                departments_data = [
                    {"name": "Human Resources", "code": "HR", "description": "Human Resources Department"},
                    {"name": "Information Technology", "code": "IT", "description": "Technology Department"},
                    {"name": "Finance", "code": "FIN", "description": "Finance Department"},
                    {"name": "Engineering", "code": "ENG", "description": "Engineering Department"},
                    {"name": "Sales", "code": "SALES", "description": "Sales Department"}
                ]
                
                for dept_info in departments_data:
                    department = Department(
                        id=str(uuid.uuid4()),
                        name=dept_info["name"],
                        code=dept_info["code"], 
                        description=dept_info["description"],
                        is_active=True
                    )
                    db.add(department)
                    print(f"   📁 Added department: {dept_info['name']}")
                
                await db.commit()
                print("✅ Departments created")
            
            # Get departments for employee assignment
            departments = await db.execute(select(Department))
            dept_list = departments.scalars().all()
            
            if len(dept_list) == 0:
                print("❌ No departments available")
                return
                
            print(f"✅ Found {len(dept_list)} departments")
            
            # Create sample users and employees if needed
            if employee_count < 5:
                print("👥 Creating sample users and employees...")
                
                user_employee_data = [
                    {
                        "user": {
                            "username": "john.smith",
                            "email": "john.smith@demo.com",
                            "first_name": "John", 
                            "last_name": "Smith",
                            "role": UserType.EMPLOYEE
                        },
                        "employee": {
                            "employee_id": "EMP001",
                            "job_title": "Software Engineer",
                            "hire_date": date(2023, 1, 15),
                            "base_salary": Decimal("75000.00"),
                            "department_code": "IT"
                        }
                    },
                    {
                        "user": {
                            "username": "sarah.johnson",
                            "email": "sarah.johnson@demo.com", 
                            "first_name": "Sarah",
                            "last_name": "Johnson",
                            "role": UserType.HR_MANAGER
                        },
                        "employee": {
                            "employee_id": "EMP002",
                            "job_title": "HR Manager", 
                            "hire_date": date(2022, 3, 10),
                            "base_salary": Decimal("65000.00"),
                            "department_code": "HR"
                        }
                    },
                    {
                        "user": {
                            "username": "mike.davis",
                            "email": "mike.davis@demo.com",
                            "first_name": "Mike",
                            "last_name": "Davis", 
                            "role": UserType.EMPLOYEE
                        },
                        "employee": {
                            "employee_id": "EMP003",
                            "job_title": "Financial Analyst",
                            "hire_date": date(2023, 6, 20),
                            "base_salary": Decimal("70000.00"),
                            "department_code": "FIN"
                        }
                    },
                    {
                        "user": {
                            "username": "lisa.wilson",
                            "email": "lisa.wilson@demo.com",
                            "first_name": "Lisa",
                            "last_name": "Wilson",
                            "role": UserType.MANAGER
                        },
                        "employee": {
                            "employee_id": "EMP004", 
                            "job_title": "Senior Developer",
                            "hire_date": date(2021, 11, 5),
                            "base_salary": Decimal("85000.00"),
                            "department_code": "ENG"
                        }
                    },
                    {
                        "user": {
                            "username": "robert.brown",
                            "email": "robert.brown@demo.com",
                            "first_name": "Robert",
                            "last_name": "Brown", 
                            "role": UserType.MANAGER
                        },
                        "employee": {
                            "employee_id": "EMP005",
                            "job_title": "Sales Manager",
                            "hire_date": date(2022, 8, 12),
                            "base_salary": Decimal("80000.00"),
                            "department_code": "SALES"
                        }
                    }
                ]
                
                for item in user_employee_data:
                    user_data = item["user"]
                    emp_data = item["employee"]
                    
                    # Check if user exists
                    existing_user = await db.execute(
                        select(User).where(User.email == user_data["email"])
                    )
                    user = existing_user.scalar_one_or_none()
                    
                    if not user:
                        # Create user
                        user = User(
                            id=str(uuid.uuid4()),
                            username=user_data["username"],
                            email=user_data["email"],
                            first_name=user_data["first_name"],
                            last_name=user_data["last_name"],
                            hashed_password="$2b$12$dummy.hash.for.testing",  # Dummy hash
                            tenant_id=int(tenant.id),  # Convert to int
                            user_type=user_data["role"],  # Already enum
                            is_active=True
                        )
                        db.add(user)
                        await db.flush()  # To get the user ID
                        print(f"   👤 Created user: {user_data['first_name']} {user_data['last_name']}")
                    
                    # Check if employee exists
                    existing_emp = await db.execute(
                        select(Employee).where(Employee.employee_id == emp_data["employee_id"])
                    )
                    employee = existing_emp.scalar_one_or_none()
                    
                    if not employee:
                        # Find department
                        dept = next((d for d in dept_list if d.code == emp_data["department_code"]), dept_list[0])
                        
                        # Create employee
                        employee = Employee(
                            id=str(uuid.uuid4()),
                            user_id=user.id,
                            employee_id=emp_data["employee_id"],
                            job_title=emp_data["job_title"],
                            department_id=dept.id,
                            hire_date=emp_data["hire_date"],
                            base_salary=emp_data["base_salary"],
                            employment_status="active",
                            employment_type="full_time",
                            currency="USD",
                            overtime_eligible=True,
                            benefits_enrolled=True,
                            skills=[],  # Empty list
                            certifications=[],  # Empty list
                            custom_fields={}  # Empty dict
                        )
                        db.add(employee)
                        print(f"   💼 Created employee: {emp_data['employee_id']} - {emp_data['job_title']}")
                
                await db.commit()
                print("✅ Users and employees created")
                
            # Final count
            final_emp_count = await db.scalar(select(func.count(Employee.id)))
            final_dept_count = await db.scalar(select(func.count(Department.id)))
            
            print(f"""
🎉 Enterprise test data ready!
   📁 {final_dept_count} departments
   💼 {final_emp_count} employees
   
✅ You can now run: python seed_enterprise_data.py
""")
            
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_enterprise_test_data())

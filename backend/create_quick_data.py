"""
Quick HRMS test data creation script.
Creates basic data for testing without complex relationships.
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
from app.models.employee import Employee, Department, EmploymentStatus, EmploymentType
from app.models.leave import LeaveRequest, LeaveBalance, LeaveType, LeaveStatus
from app.core.security import hash_password
from sqlalchemy import select, text
import uuid


async def create_quick_test_data():
    """Create basic test data without complex relationships."""
    
    async for db in get_session():
        try:
            print("Creating quick test data...")
            
            # Get the demo tenant ID from existing setup
            result = await db.execute(text("SELECT id FROM tenants WHERE name = 'Demo Company' LIMIT 1"))
            tenant_row = result.fetchone()
            
            if not tenant_row:
                print("Demo Company tenant not found. Please run setup_db.py first.")
                return
            
            tenant_id = str(tenant_row[0])
            print(f"Using tenant ID: {tenant_id}")
            
            # Create a few departments directly
            departments = [
                {"id": str(uuid.uuid4()), "name": "Information Technology", "code": "IT"},
                {"id": str(uuid.uuid4()), "name": "Human Resources", "code": "HR"},
                {"id": str(uuid.uuid4()), "name": "Finance", "code": "FIN"}
            ]
            
            for dept in departments:
                # Check if exists
                check_result = await db.execute(
                    text("SELECT id FROM departments WHERE tenant_id = :tid AND code = :code"),
                    {"tid": tenant_id, "code": dept["code"]}
                )
                if not check_result.fetchone():
                    await db.execute(
                        text("""
                            INSERT INTO departments (id, tenant_id, name, code, description, is_active, created_at, updated_at)
                            VALUES (:id, :tid, :name, :code, :desc, true, now(), now())
                        """),
                        {
                            "id": dept["id"],
                            "tid": tenant_id,
                            "name": dept["name"], 
                            "code": dept["code"],
                            "desc": f"{dept['name']} Department"
                        }
                    )
                    print(f"Created department: {dept['name']}")
            
            await db.commit()
            
            # Create a few employees
            employees = [
                {
                    "user_id": str(uuid.uuid4()),
                    "emp_id": str(uuid.uuid4()),
                    "username": "jane.doe",
                    "email": "jane.doe@demo.com",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "employee_id": "EMP100",
                    "job_title": "Software Engineer",
                    "dept_code": "IT"
                },
                {
                    "user_id": str(uuid.uuid4()),
                    "emp_id": str(uuid.uuid4()),
                    "username": "bob.smith",
                    "email": "bob.smith@demo.com", 
                    "first_name": "Bob",
                    "last_name": "Smith",
                    "employee_id": "EMP101",
                    "job_title": "HR Specialist",
                    "dept_code": "HR"
                }
            ]
            
            for emp in employees:
                # Check if user exists
                check_result = await db.execute(
                    text("SELECT id FROM users WHERE username = :username"),
                    {"username": emp["username"]}
                )
                if check_result.fetchone():
                    continue
                
                # Get department ID
                dept_result = await db.execute(
                    text("SELECT id FROM departments WHERE tenant_id = :tid AND code = :code"),
                    {"tid": tenant_id, "code": emp["dept_code"]}
                )
                dept_row = dept_result.fetchone()
                dept_id = str(dept_row[0]) if dept_row else None
                
                # Create user
                await db.execute(
                    text("""
                        INSERT INTO users (id, tenant_id, username, email, first_name, last_name, hashed_password, user_type, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :username, :email, :fname, :lname, :pwd, :utype, true, now(), now())
                    """),
                    {
                        "id": emp["user_id"],
                        "tid": tenant_id,
                        "username": emp["username"],
                        "email": emp["email"],
                        "fname": emp["first_name"],
                        "lname": emp["last_name"],
                        "pwd": hash_password("password123"),
                        "utype": "EMPLOYEE"
                    }
                )
                
                # Create employee
                await db.execute(
                    text("""
                        INSERT INTO employees (id, tenant_id, user_id, employee_id, employment_status, employment_type, 
                                             hire_date, job_title, department_id, base_salary, currency, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :uid, :empid, :status, :type, :hire, :title, :deptid, :salary, 'USD', true, now(), now())
                    """),
                    {
                        "id": emp["emp_id"],
                        "tid": tenant_id,
                        "uid": emp["user_id"],
                        "empid": emp["employee_id"],
                        "status": "ACTIVE",
                        "type": "FULL_TIME",
                        "hire": date(2023, 1, 15),
                        "title": emp["job_title"],
                        "deptid": dept_id,
                        "salary": Decimal("75000.00")
                    }
                )
                print(f"Created employee: {emp['first_name']} {emp['last_name']}")
            
            await db.commit()
            
            # Create leave balances for the year
            current_year = datetime.now().year
            leave_types = ['ANNUAL', 'SICK', 'PERSONAL']
            
            for emp in employees:
                for leave_type in leave_types:
                    balance_id = str(uuid.uuid4())
                    total_days = {"ANNUAL": 21, "SICK": 10, "PERSONAL": 5}[leave_type]
                    
                    await db.execute(
                        text("""
                            INSERT INTO leave_balances (id, tenant_id, employee_id, leave_type, year, total_days, used_days, pending_days, carried_over_days, max_carry_over, created_at, updated_at)
                            VALUES (:id, :tid, :empid, :ltype, :year, :total, 0, 0, 0, 5, now(), now())
                        """),
                        {
                            "id": balance_id,
                            "tid": tenant_id,
                            "empid": emp["emp_id"],
                            "ltype": leave_type,
                            "year": current_year,
                            "total": total_days
                        }
                    )
            
            await db.commit()
            
            # Create a sample leave request
            if employees:
                leave_id = str(uuid.uuid4())
                await db.execute(
                    text("""
                        INSERT INTO leave_requests (id, tenant_id, employee_id, leave_type, start_date, end_date, reason, status, requested_days, is_half_day, created_at, updated_at)
                        VALUES (:id, :tid, :empid, 'ANNUAL', :start, :end, 'Team building event', 'PENDING', 1, false, now(), now())
                    """),
                    {
                        "id": leave_id,
                        "tid": tenant_id,
                        "empid": employees[0]["emp_id"],
                        "start": date.today() + timedelta(days=7),
                        "end": date.today() + timedelta(days=7)
                    }
                )
                print("Created sample leave request")
            
            await db.commit()
            
            print("\n✅ Quick test data created successfully!")
            print("\nTest Login Credentials:")
            print("- admin / admin123 / demo (Admin)")
            print("- jane.doe / password123 / demo (Software Engineer)")
            print("- bob.smith / password123 / demo (HR Specialist)")
            print("\nData created:")
            print("- 3 departments")
            print("- 2 employees")
            print("- Leave balances")
            print("- 1 sample leave request")
            
        except Exception as e:
            await db.rollback()
            print(f"Error creating test data: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(create_quick_test_data())

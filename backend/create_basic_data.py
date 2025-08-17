#!/usr/bin/env python3
"""
Basic data seeder for HRMS-SAAS.
Creates minimal employee data to test enterprise features.
"""

import asyncio
import sys
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.employee import Employee, Department
from app.models.user import User

async def create_basic_data():
    """Create basic employee data for enterprise feature testing."""
    async for db in get_session():
        try:
            print("🌱 Creating basic enterprise test data...")
            
            # Get tenant ID
            tenant_result = await db.execute(text("SELECT id FROM tenants WHERE slug = 'demo' LIMIT 1"))
            tenant_row = tenant_result.fetchone()
            
            if not tenant_row:
                print("❌ Demo tenant not found. Please run setup_db.py first.")
                return
                
            tenant_id = tenant_row[0]
            print(f"✅ Using tenant ID: {tenant_id}")
            
            # Check if departments exist (without tenant_id filter to work with current schema)
            dept_result = await db.execute(text("SELECT id, name FROM departments LIMIT 5"))
            departments = dept_result.fetchall()
            
            # Create basic departments if none exist
            if not departments:
                print("📁 Creating departments...")
                dept_data = [
                    ("Human Resources", "HR"),
                    ("Information Technology", "IT"), 
                    ("Finance", "FIN"),
                    ("Engineering", "ENG"),
                    ("Sales", "SALES")
                ]
                
                for dept_name, dept_code in dept_data:
                    # Check if department exists
                    check_result = await db.execute(
                        text("SELECT id FROM departments WHERE code = :code"),
                        {"code": dept_code}
                    )
                    existing = check_result.fetchone()
                    
                    if not existing:
                        await db.execute(
                            text("INSERT INTO departments (name, code, description, is_active) VALUES (:name, :code, :description, :is_active)"),
                            {
                                "name": dept_name,
                                "code": dept_code,
                                "description": f"{dept_name} Department",
                                "is_active": True
                            }
                        )
                        print(f"   📁 Created department: {dept_name}")
                
                await db.commit()
                
                # Get departments again
                dept_result = await db.execute(text("SELECT id, name FROM departments LIMIT 5"))
                departments = dept_result.fetchall()
            
            print(f"✅ Found {len(departments)} departments")
            
            # Check existing employees
            emp_result = await db.execute(text("SELECT COUNT(*) FROM employees"))
            emp_count = emp_result.scalar()
            
            if emp_count < 5:
                print("👥 Creating sample users and employees...")
                
                # First, create users
                user_data = [
                    {
                        "username": "john.smith",
                        "email": "john.smith@demo.com",
                        "first_name": "John",
                        "last_name": "Smith",
                        "tenant_id": tenant_id,
                        "role": "employee"
                    },
                    {
                        "username": "sarah.johnson", 
                        "email": "sarah.johnson@demo.com",
                        "first_name": "Sarah",
                        "last_name": "Johnson",
                        "tenant_id": tenant_id,
                        "role": "hr_manager"
                    },
                    {
                        "username": "mike.davis",
                        "email": "mike.davis@demo.com", 
                        "first_name": "Mike",
                        "last_name": "Davis",
                        "tenant_id": tenant_id,
                        "role": "employee"
                    },
                    {
                        "username": "lisa.wilson",
                        "email": "lisa.wilson@demo.com",
                        "first_name": "Lisa",
                        "last_name": "Wilson", 
                        "tenant_id": tenant_id,
                        "role": "manager"
                    },
                    {
                        "username": "robert.brown",
                        "email": "robert.brown@demo.com",
                        "first_name": "Robert", 
                        "last_name": "Brown",
                        "tenant_id": tenant_id,
                        "role": "manager"
                    }
                ]
                
                # Create users and collect their IDs
                user_ids = []
                for user_info in user_data:
                    # Check if user exists
                    check_result = await db.execute(
                        text("SELECT id FROM users WHERE email = :email"),
                        {"email": user_info["email"]}
                    )
                    existing = check_result.fetchone()
                    
                    if existing:
                        user_ids.append(existing[0])
                        print(f"   ✅ User exists: {user_info['first_name']} {user_info['last_name']}")
                    else:
                        # Insert user (using simple password hash)
                        user_result = await db.execute(
                            text("""
                                INSERT INTO users (username, email, first_name, last_name, password_hash, tenant_id, role, is_active) 
                                VALUES (:username, :email, :first_name, :last_name, :password, :tenant_id, :role, :is_active)
                                RETURNING id
                            """),
                            {
                                "username": user_info["username"],
                                "email": user_info["email"], 
                                "first_name": user_info["first_name"],
                                "last_name": user_info["last_name"],
                                "password": "$2b$12$dummy.hash.for.testing",  # Dummy password hash
                                "tenant_id": tenant_id,
                                "role": user_info["role"],
                                "is_active": True
                            }
                        )
                        user_id = user_result.fetchone()[0]
                        user_ids.append(user_id)
                        print(f"   👤 Created user: {user_info['first_name']} {user_info['last_name']}")
                
                await db.commit()
                
                # Now create employees linked to users
                employee_data = [
                    {
                        "user_id": user_ids[0],
                        "employee_id": "EMP001",
                        "job_title": "Software Engineer",
                        "department_id": departments[1][0] if len(departments) > 1 else departments[0][0],  # IT
                        "hire_date": date(2023, 1, 15),
                        "base_salary": Decimal("75000.00"),
                        "employment_status": "active",
                        "employment_type": "full_time"
                    },
                    {
                        "user_id": user_ids[1],
                        "employee_id": "EMP002", 
                        "job_title": "HR Manager",
                        "department_id": departments[0][0],  # HR
                        "hire_date": date(2022, 3, 10),
                        "base_salary": Decimal("65000.00"),
                        "employment_status": "active", 
                        "employment_type": "full_time"
                    },
                    {
                        "user_id": user_ids[2],
                        "employee_id": "EMP003",
                        "job_title": "Financial Analyst",
                        "department_id": departments[2][0] if len(departments) > 2 else departments[0][0],  # Finance
                        "hire_date": date(2023, 6, 20),
                        "base_salary": Decimal("70000.00"),
                        "employment_status": "active",
                        "employment_type": "full_time"
                    },
                    {
                        "user_id": user_ids[3],
                        "employee_id": "EMP004",
                        "job_title": "Senior Developer", 
                        "department_id": departments[3][0] if len(departments) > 3 else departments[1][0],  # Engineering
                        "hire_date": date(2021, 11, 5),
                        "base_salary": Decimal("85000.00"),
                        "employment_status": "active",
                        "employment_type": "full_time"
                    },
                    {
                        "user_id": user_ids[4],
                        "employee_id": "EMP005",
                        "job_title": "Sales Manager",
                        "department_id": departments[4][0] if len(departments) > 4 else departments[0][0],  # Sales
                        "hire_date": date(2022, 8, 12),
                        "base_salary": Decimal("80000.00"),
                        "employment_status": "active",
                        "employment_type": "full_time"
                    }
                ]
                
                for emp_data in employee_data:
                    # Check if employee exists
                    check_result = await db.execute(
                        text("SELECT id FROM employees WHERE employee_id = :emp_id"),
                        {"emp_id": emp_data["employee_id"]}
                    )
                    existing = check_result.fetchone()
                    
                    if not existing:
                        # Insert employee with required fields
                        await db.execute(
                            text("""
                                INSERT INTO employees (
                                    user_id, employee_id, job_title, department_id, hire_date, 
                                    base_salary, employment_status, employment_type, currency,
                                    overtime_eligible, benefits_enrolled, skills, certifications, custom_fields
                                ) VALUES (
                                    :user_id, :employee_id, :job_title, :department_id, :hire_date,
                                    :base_salary, :employment_status, :employment_type, :currency,
                                    :overtime_eligible, :benefits_enrolled, :skills, :certifications, :custom_fields
                                )
                            """),
                            {
                                **emp_data,
                                "currency": "USD",
                                "overtime_eligible": True,
                                "benefits_enrolled": True, 
                                "skills": '[]',  # Empty JSON array
                                "certifications": '[]',  # Empty JSON array
                                "custom_fields": '{}'  # Empty JSON object
                            }
                        )
                        print(f"   👤 Created employee: {user_data[employee_data.index(emp_data)]['first_name']} {user_data[employee_data.index(emp_data)]['last_name']}")
                
                await db.commit()
                
            print("✅ Basic employee data created successfully!")
            
            # Show summary
            emp_result = await db.execute(text("SELECT COUNT(*) FROM employees"))
            emp_count = emp_result.scalar()
            
            dept_result = await db.execute(text("SELECT COUNT(*) FROM departments"))
            dept_count = dept_result.scalar()
            
            print(f"""
🎉 Basic data summary:
   👥 {emp_count} employees
   📁 {dept_count} departments
   
✅ Database is now ready for enterprise feature testing!
You can now run: python seed_enterprise_data.py
""")
            
        except Exception as e:
            print(f"❌ Error creating basic data: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(create_basic_data())

"""
Enterprise data seeders for HRMS-SAAS.
Seeds performance reviews, goals, payroll data, and enhanced employee information.
"""

import asyncio
import random
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.models.user import User
from app.models.employee import Employee, Department
from app.models.performance import (
    PerformanceReview, PerformanceGoal, PerformanceFeedback, PerformanceMetric,
    ReviewStatus, ReviewType, GoalStatus, GoalPriority
)
from app.models.payroll import (
    PayrollEntry, PayrollRun, SalaryStructure,
    PayrollStatus, PaymentMethod, PayrollFrequency
)

# Sample data for realistic seeding
PERFORMANCE_STRENGTHS = [
    "Exceptional technical skills and problem-solving abilities",
    "Strong leadership qualities and team management skills",
    "Excellent communication and interpersonal skills",
    "Proactive approach to identifying and solving problems",
    "Consistent delivery of high-quality work",
    "Strong analytical and strategic thinking capabilities",
    "Excellent client relationship management",
    "Outstanding attention to detail and accuracy",
    "Innovative thinking and creative problem solving",
    "Strong mentoring and coaching abilities"
]

PERFORMANCE_IMPROVEMENTS = [
    "Could improve time management for multiple concurrent projects",
    "Would benefit from additional training in advanced technical skills",
    "Could enhance presentation and public speaking skills",
    "Needs to work on delegating tasks more effectively",
    "Could improve documentation and knowledge sharing practices",
    "Would benefit from developing more strategic thinking skills",
    "Needs to work on conflict resolution and negotiation skills",
    "Could improve project planning and estimation accuracy",
    "Would benefit from enhancing cross-functional collaboration",
    "Needs to focus more on professional development activities"
]

GOAL_TITLES = [
    "Complete AWS Solutions Architect certification",
    "Lead platform migration project to cloud infrastructure",
    "Implement new customer onboarding process",
    "Increase team productivity by 25%",
    "Develop and launch new product feature",
    "Mentor 3 junior team members",
    "Reduce customer response time by 40%",
    "Complete advanced leadership training program",
    "Establish new department KPIs and metrics",
    "Build strategic partnership with key vendor"
]

FEEDBACK_CONTENT = [
    "Excellent work on the quarterly project delivery. Your attention to detail and leadership really showed.",
    "Great job collaborating with the cross-functional team. Your communication skills were key to the success.",
    "Your innovative approach to problem-solving helped us overcome significant technical challenges.",
    "I appreciate your proactive attitude in identifying process improvements and implementing solutions.",
    "Your mentoring of junior team members has been invaluable to their professional development.",
    "Outstanding performance in client meetings. Your expertise and professionalism were evident.",
    "Thank you for taking initiative on the documentation project. It will benefit the entire team.",
    "Your analytical skills really shone through in the market research presentation.",
    "Impressive work on the budget analysis. Your recommendations were well-researched and practical.",
    "Your positive attitude and team spirit contribute significantly to our work environment."
]

async def seed_enhanced_employee_data(session: AsyncSession):
    """Seed enhanced employee data with skills, certifications, and performance info."""
    print("🔧 Seeding enhanced employee data...")
    
    # Get existing employees
    employees = (await session.execute(
        select(Employee).options(selectinload(Employee.user))
    )).scalars().all()
    
    skills_options = [
        "Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes",
        "SQL", "MongoDB", "Machine Learning", "Data Analysis", "Project Management",
        "Leadership", "Agile", "DevOps", "UI/UX Design", "Marketing", "Sales",
        "Finance", "HR Management", "Strategic Planning", "Communication"
    ]
    
    certifications_options = [
        "AWS Certified Solutions Architect",
        "PMP - Project Management Professional",
        "Certified ScrumMaster (CSM)",
        "Google Analytics Certified",
        "Microsoft Azure Fundamentals",
        "SHRM-CP (HR Certification)",
        "CPA - Certified Public Accountant",
        "Six Sigma Green Belt",
        "Salesforce Administrator",
        "CompTIA Security+"
    ]
    
    for employee in employees:
        # Add skills
        selected_skills = random.sample(skills_options, random.randint(3, 8))
        skills_data = {}
        for skill in selected_skills:
            skills_data[skill] = {
                "level": random.choice(["Beginner", "Intermediate", "Advanced", "Expert"]),
                "years_experience": random.randint(1, 10)
            }
        employee.skills = skills_data
        
        # Add certifications
        if random.random() > 0.3:  # 70% chance of having certifications
            selected_certs = random.sample(certifications_options, random.randint(1, 4))
            cert_data = {}
            for cert in selected_certs:
                cert_data[cert] = {
                    "date_obtained": (date.today() - timedelta(days=random.randint(30, 1095))).isoformat(),
                    "expiry_date": (date.today() + timedelta(days=random.randint(365, 1095))).isoformat(),
                    "issuer": "Professional Certification Body"
                }
            employee.certifications = cert_data
        
        # Add performance rating
        employee.performance_rating = round(random.uniform(3.0, 5.0), 1)
        
        # Add career goals
        employee.career_goals = random.choice([
            "Advance to senior leadership role within 3 years",
            "Become a subject matter expert in emerging technologies",
            "Transition into product management role",
            "Lead larger strategic initiatives and cross-functional teams",
            "Develop expertise in data science and analytics",
            "Build and mentor a high-performing team",
            "Pursue advanced degree in business administration",
            "Establish thought leadership in industry"
        ])
    
    await session.commit()
    print(f"✅ Enhanced data for {len(employees)} employees")

async def seed_performance_reviews(session: AsyncSession):
    """Seed performance review data."""
    print("📊 Seeding performance reviews...")
    
    # Get employees and reviewers
    employees = (await session.execute(
        select(Employee).options(selectinload(Employee.user))
    )).scalars().all()
    reviewers = [emp for emp in employees if emp.job_title and "manager" in emp.job_title.lower() or "director" in emp.job_title.lower() or "lead" in emp.job_title.lower()]
    
    if not reviewers:
        reviewers = employees[:min(5, len(employees))]  # Use first 5 as reviewers if no managers found
    
    reviews_created = 0
    
    for employee in employees:
        # Create 1-2 reviews per employee
        num_reviews = random.randint(1, 2)
        
        for i in range(num_reviews):
            reviewer = random.choice(reviewers)
            if reviewer.id == employee.id:  # Don't self-review
                continue
            
            # Create review for different periods
            months_ago = 6 + (i * 6)  # 6 months ago, 12 months ago, etc.
            review_start = date.today() - timedelta(days=months_ago * 30)
            review_end = review_start + timedelta(days=180)  # 6 month period
            
            # Determine status based on review age
            if months_ago <= 6:
                status = random.choice([ReviewStatus.COMPLETED, ReviewStatus.IN_PROGRESS])
            else:
                status = ReviewStatus.COMPLETED
            
            # Create categories with ratings
            categories = {
                "Technical Skills": {
                    "score": round(random.uniform(3.5, 5.0), 1),
                    "weight": 30,
                    "comments": "Demonstrates strong technical competency and continuous learning"
                },
                "Communication": {
                    "score": round(random.uniform(3.0, 4.8), 1),
                    "weight": 20,
                    "comments": "Effective communicator with team members and stakeholders"
                },
                "Leadership": {
                    "score": round(random.uniform(3.0, 4.5), 1),
                    "weight": 25,
                    "comments": "Shows leadership potential and team collaboration skills"
                },
                "Innovation": {
                    "score": round(random.uniform(3.2, 4.7), 1),
                    "weight": 15,
                    "comments": "Brings creative solutions and process improvements"
                },
                "Collaboration": {
                    "score": round(random.uniform(3.5, 4.9), 1),
                    "weight": 10,
                    "comments": "Works well with cross-functional teams and colleagues"
                }
            }
            
            # Calculate overall rating
            overall_rating = sum(cat["score"] * cat["weight"] for cat in categories.values()) / 100
            
            review = PerformanceReview(
                id=str(uuid.uuid4()),  # Generate UUID explicitly
                tenant_id=employee.tenant_id,  # Use employee's tenant_id
                employee_id=employee.id,
                reviewer_id=reviewer.id,
                review_period_start=review_start,
                review_period_end=review_end,
                status=status,
                review_type=ReviewType.SEMI_ANNUAL if i % 2 == 0 else ReviewType.ANNUAL,
                overall_rating=round(overall_rating, 1) if status == ReviewStatus.COMPLETED else None,
                review_date=review_end + timedelta(days=random.randint(1, 30)) if status == ReviewStatus.COMPLETED else None,
                due_date=review_end + timedelta(days=45),
                strengths=random.choice(PERFORMANCE_STRENGTHS),
                improvements=random.choice(PERFORMANCE_IMPROVEMENTS),
                achievements="Successfully completed key projects and exceeded quarterly targets",
                development_areas="Focus on expanding technical skills and leadership capabilities",
                feedback=f"Strong performer with consistent results. {random.choice(PERFORMANCE_STRENGTHS)}",
                manager_comments="Recommend for advancement opportunities and additional responsibilities",
                categories=categories,
                competencies={
                    "Problem Solving": random.uniform(3.5, 5.0),
                    "Teamwork": random.uniform(3.0, 4.8),
                    "Adaptability": random.uniform(3.2, 4.7),
                    "Initiative": random.uniform(3.0, 4.5)
                },
                next_period_goals="Focus on skill development and process improvement initiatives",
                career_development_plan="Structured path towards senior role with increased responsibilities"
            )
            
            session.add(review)
            reviews_created += 1
    
    await session.commit()
    print(f"✅ Created {reviews_created} performance reviews")

async def seed_performance_goals(session: AsyncSession):
    """Seed performance goals data."""
    print("🎯 Seeding performance goals...")
    
    employees = (await session.execute(select(Employee))).scalars().all()
    goals_created = 0
    
    for employee in employees:
        # Create 2-4 goals per employee
        num_goals = random.randint(2, 4)
        
        for i in range(num_goals):
            goal_title = random.choice(GOAL_TITLES)
            
            # Random goal timing
            start_date = date.today() - timedelta(days=random.randint(30, 180))
            target_date = start_date + timedelta(days=random.randint(90, 365))
            
            # Determine status and progress
            days_elapsed = (date.today() - start_date).days
            total_days = (target_date - start_date).days
            time_progress = min(days_elapsed / total_days, 1.0) if total_days > 0 else 0
            
            if target_date < date.today():
                status = random.choice([GoalStatus.ACHIEVED, GoalStatus.PARTIALLY_ACHIEVED, GoalStatus.NOT_ACHIEVED])
                progress = 100 if status == GoalStatus.ACHIEVED else random.uniform(60, 95) if status == GoalStatus.PARTIALLY_ACHIEVED else random.uniform(30, 70)
                completion_date = target_date + timedelta(days=random.randint(-7, 14))
            else:
                status = GoalStatus.ACTIVE
                progress = min(time_progress * 100 + random.uniform(-10, 20), 95)  # Add some randomness
                completion_date = None
            
            goal = PerformanceGoal(
                id=str(uuid.uuid4()),  # Generate UUID explicitly
                tenant_id=employee.tenant_id,  # Use employee's tenant_id
                employee_id=employee.id,
                title=goal_title,
                description=f"Detailed description and requirements for {goal_title.lower()}",
                status=status,
                priority=random.choice(list(GoalPriority)),
                start_date=start_date,
                target_date=target_date,
                completion_date=completion_date,
                progress_percentage=max(0, min(progress, 100)),
                measurement_criteria="Success will be measured by completion of all deliverables and stakeholder approval",
                success_metrics={
                    "deliverables_completed": random.randint(2, 8),
                    "stakeholder_satisfaction": random.uniform(3.5, 5.0),
                    "timeline_adherence": random.uniform(0.8, 1.2)
                },
                achievement_rating=round(random.uniform(3.5, 5.0), 1) if status in [GoalStatus.ACHIEVED, GoalStatus.PARTIALLY_ACHIEVED, GoalStatus.NOT_ACHIEVED] else None,
                manager_feedback="Regular progress updates and strong execution" if status == GoalStatus.ACHIEVED else None,
                category=random.choice(["Professional Development", "Technical Skills", "Leadership", "Process Improvement", "Client Relations"]),
                is_stretch_goal=random.random() > 0.7,
                weight=random.uniform(1.0, 3.0)
            )
            
            session.add(goal)
            goals_created += 1
    
    await session.commit()
    print(f"✅ Created {goals_created} performance goals")

async def seed_performance_feedback(session: AsyncSession):
    """Seed performance feedback data."""
    print("💬 Seeding performance feedback...")
    
    employees = (await session.execute(select(Employee))).scalars().all()
    feedback_created = 0
    
    for employee in employees:
        # Create 3-6 feedback entries per employee
        num_feedback = random.randint(3, 6)
        
        for i in range(num_feedback):
            feedback_giver = random.choice(employees)
            if feedback_giver.id == employee.id:  # No self-feedback
                continue
            
            feedback = PerformanceFeedback(
                id=str(uuid.uuid4()),  # Generate UUID explicitly
                tenant_id=employee.tenant_id,  # Use employee's tenant_id
                employee_id=employee.id,
                feedback_giver_id=feedback_giver.id,
                feedback_type=random.choice(["positive", "constructive", "recognition", "development"]),
                title=f"Feedback from {feedback_giver.job_title or 'Colleague'}",
                content=random.choice(FEEDBACK_CONTENT),
                project_context=random.choice(["Q3 Product Launch", "Client Onboarding", "Process Improvement", "Team Collaboration"]),
                is_anonymous=random.random() > 0.8,
                is_public=random.random() > 0.6,
                visibility_level=random.choice(["manager", "hr", "team"]),
                tags=random.sample(["teamwork", "leadership", "technical", "communication", "innovation"], random.randint(1, 3))
            )
            
            session.add(feedback)
            feedback_created += 1
    
    await session.commit()
    print(f"✅ Created {feedback_created} feedback entries")

async def seed_payroll_data(session: AsyncSession):
    """Seed payroll entries data."""
    print("💰 Seeding payroll data...")
    
    employees = (await session.execute(
        select(Employee).options(selectinload(Employee.user))
    )).scalars().all()
    payroll_created = 0
    
    # Create payroll entries for last 6 months
    for month_offset in range(6):
        pay_period_end = date.today().replace(day=1) - timedelta(days=month_offset * 30)
        pay_period_start = pay_period_end.replace(day=1)
        pay_date = pay_period_end + timedelta(days=5)
        
        for employee in employees:
            # Generate realistic salary based on job title
            base_salary = Decimal(str(random.randint(4000, 12000)))
            if employee.job_title and any(title in employee.job_title.lower() for title in ['senior', 'lead', 'manager']):
                base_salary += Decimal(str(random.randint(2000, 5000)))
            if employee.job_title and any(title in employee.job_title.lower() for title in ['director', 'vp', 'head']):
                base_salary += Decimal(str(random.randint(5000, 10000)))
            
            # Allowances based on role and company policy
            housing_allowance = base_salary * Decimal('0.25')  # 25% of base
            transport_allowance = Decimal(str(random.randint(300, 800)))
            meal_allowance = Decimal(str(random.randint(200, 500)))
            medical_allowance = Decimal(str(random.randint(100, 300)))
            
            # Bonuses (random, not every month)
            performance_bonus = Decimal(str(random.randint(0, 2000))) if random.random() > 0.7 else Decimal('0')
            
            # Deductions
            income_tax = (base_salary + housing_allowance) * Decimal('0.15')  # 15% tax rate
            social_security = base_salary * Decimal('0.08')  # 8% social security
            pension_contribution = base_salary * Decimal('0.10')  # 10% pension
            health_insurance = Decimal(str(random.randint(200, 500)))
            
            # Random loan deductions for some employees
            loan_deduction = Decimal(str(random.randint(0, 1000))) if random.random() > 0.8 else Decimal('0')
            
            # Overtime (occasional)
            overtime_hours = random.randint(0, 20) if random.random() > 0.6 else 0
            hourly_rate = base_salary / Decimal('160')  # Assuming 160 hours/month
            overtime_amount = hourly_rate * Decimal(str(overtime_hours)) * Decimal('1.5') if overtime_hours > 0 else Decimal('0')
            
            # Determine status based on month
            if month_offset == 0:  # Current month
                status = random.choice([PayrollStatus.DRAFT, PayrollStatus.CALCULATED])
            elif month_offset == 1:  # Last month
                status = random.choice([PayrollStatus.APPROVED, PayrollStatus.PAID])
            else:  # Older months
                status = PayrollStatus.PAID
            
            payroll_entry = PayrollEntry(
                id=str(uuid.uuid4()),  # Generate UUID explicitly
                tenant_id=employee.tenant_id,  # Use employee's tenant_id
                employee_id=employee.id,
                pay_period_start=pay_period_start,
                pay_period_end=pay_period_end,
                pay_date=pay_date if status == PayrollStatus.PAID else None,
                status=status,
                basic_salary=base_salary,
                hourly_rate=hourly_rate,
                overtime_hours=overtime_hours,
                overtime_amount=overtime_amount,
                housing_allowance=housing_allowance,
                transport_allowance=transport_allowance,
                meal_allowance=meal_allowance,
                medical_allowance=medical_allowance,
                communication_allowance=Decimal('0'),
                other_allowances=Decimal('0'),
                performance_bonus=performance_bonus,
                sales_commission=Decimal('0'),
                attendance_bonus=Decimal('0'),
                holiday_bonus=Decimal('0'),
                other_bonuses=Decimal('0'),
                income_tax=income_tax,
                social_security=social_security,
                pension_contribution=pension_contribution,
                health_insurance=health_insurance,
                life_insurance=Decimal('0'),
                loan_deduction=loan_deduction,
                advance_deduction=Decimal('0'),
                other_deductions=Decimal('0'),
                payment_method=random.choice(list(PaymentMethod))
            )
            
            # Calculate totals
            payroll_entry.calculate_totals()
            
            # Add YTD calculations (simplified)
            year_start = date.today().replace(month=1, day=1)
            months_ytd = max(1, (pay_period_end - year_start).days // 30)
            payroll_entry.ytd_gross_pay = payroll_entry.gross_pay * months_ytd
            payroll_entry.ytd_tax_paid = payroll_entry.income_tax * months_ytd
            payroll_entry.ytd_net_pay = payroll_entry.net_pay * months_ytd
            
            session.add(payroll_entry)
            payroll_created += 1
    
    await session.commit()
    print(f"✅ Created {payroll_created} payroll entries")

async def seed_salary_structures(session: AsyncSession):
    """Seed salary structure data."""
    print("🏗️ Seeding salary structures...")
    
    departments = (await session.execute(select(Department))).scalars().all()
    
    # Get tenant_id from the first department (assuming single tenant for this seed)
    tenant_id = departments[0].tenant_id if departments else None
    if not tenant_id:
        print("⚠️ No departments found, skipping salary structures")
        return
    
    structures = [
        {
            "name": "Engineering Salary Structure",
            "description": "Salary structure for engineering roles with tech allowances",
            "department_ids": [dept.id for dept in departments if "engineering" in dept.name.lower()],
            "job_grades": ["Junior", "Mid-Level", "Senior", "Principal"],
            "base_salary_ranges": {
                "Junior": {"min": 50000, "max": 70000},
                "Mid-Level": {"min": 70000, "max": 95000},
                "Senior": {"min": 95000, "max": 130000},
                "Principal": {"min": 130000, "max": 180000}
            }
        },
        {
            "name": "Sales Salary Structure",
            "description": "Commission-based salary structure for sales team",
            "department_ids": [dept.id for dept in departments if "sales" in dept.name.lower()],
            "job_grades": ["Associate", "Representative", "Senior", "Manager"],
            "base_salary_ranges": {
                "Associate": {"min": 40000, "max": 55000},
                "Representative": {"min": 55000, "max": 75000},
                "Senior": {"min": 75000, "max": 100000},
                "Manager": {"min": 100000, "max": 150000}
            }
        }
    ]
    
    for struct_data in structures:
        if struct_data["department_ids"]:  # Only create if departments exist
            structure = SalaryStructure(
                id=str(uuid.uuid4()),  # Generate UUID explicitly
                tenant_id=tenant_id,  # Use tenant_id
                name=struct_data["name"],
                description=struct_data["description"],
                is_active=True,
                effective_date=date.today() - timedelta(days=365),
                department_ids=struct_data["department_ids"],
                job_grades=struct_data["job_grades"],
                base_salary_component={
                    "ranges": struct_data["base_salary_ranges"],
                    "currency": "USD"
                },
                allowance_components={
                    "housing": {"percentage": 25, "max_amount": 2000},
                    "transport": {"fixed_amount": 500},
                    "meal": {"fixed_amount": 300}
                },
                deduction_components={
                    "income_tax": {"percentage": 15},
                    "social_security": {"percentage": 8},
                    "pension": {"percentage": 10}
                },
                calculation_rules={
                    "overtime_multiplier": 1.5,
                    "holiday_pay_multiplier": 2.0
                }
            )
            session.add(structure)
    
    await session.commit()
    print("✅ Created salary structures")

async def main():
    """Main seeder function."""
    print("🌱 Starting enterprise data seeding...")
    
    async for session in get_session():
        try:
            # Seed in order of dependencies
            await seed_enhanced_employee_data(session)
            await seed_performance_reviews(session)
            await seed_performance_goals(session)
            await seed_performance_feedback(session)
            await seed_payroll_data(session)
            await seed_salary_structures(session)
            
            print("\n🎉 Enterprise data seeding completed successfully!")
            print("📊 You now have realistic data for:")
            print("   • Enhanced employee profiles with skills and certifications")
            print("   • Performance reviews and ratings")
            print("   • Performance goals and progress tracking")
            print("   • Employee feedback and recognition")
            print("   • Payroll entries with realistic calculations")
            print("   • Salary structures and pay scales")
            
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
        break  # Only use the first session

if __name__ == "__main__":
    asyncio.run(main())

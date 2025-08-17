"""
Database setup script for HRMS-SAAS.
Creates tables and seeds initial data.
"""

import asyncio
from sqlalchemy import text

from app.core.database import init_database, get_session, Base, engine
from app.core.security import SecurityManager
# Import all models to ensure tables are created in correct order
from app.models.base import *
from app.models.tenant import *
from app.models.subscription import *
from app.models.user import *
from app.models.employee import *
from app.models.leave import *


async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    from app.core.database import get_database_engine
    engine = await get_database_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")


async def seed_initial_data():
    """Seed initial demo data."""
    print("Seeding initial data...")
    
    security = SecurityManager()
    
    import uuid
    from app.models.user import UserType
    async for session in get_session():
        # Check if demo tenant already exists
        existing_tenant = await session.execute(
            text("SELECT id FROM tenants WHERE slug = 'demo'")
        )
        tenant_id = existing_tenant.scalar()
        if not tenant_id:
            # Create demo tenant
            demo_tenant = Tenant(
                name="Demo Company",
                slug="demo", 
                domain="demo.hrms.com",
                contact_email="admin@demo.hrms.com",
                company_name="Demo Company Ltd"
            )
            session.add(demo_tenant)
            await session.flush()
            tenant_id = demo_tenant.id
        # Check if admin user exists
        existing_user = await session.execute(
            text("SELECT id FROM users WHERE username = 'admin' AND tenant_id = :tenant_id"),
            {"tenant_id": tenant_id}
        )
        if existing_user.scalar():
            print("Admin user already exists")
            return
        # Create admin user with UUID
        admin_user = User(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@demo.hrms.com",
            first_name="Admin",
            last_name="User",
            hashed_password=security.get_password_hash("admin123"),
            is_active=True,
            is_verified=True,
            user_type=UserType.ADMIN,
            status="ACTIVE",
            tenant_id=tenant_id,
            timezone="UTC",
            locale="en_US",
            preferences={},
        )
        session.add(admin_user)
        await session.commit()
        print("Initial data seeded successfully!")
        break  # Exit the async generator after first iteration


async def setup_database():
    """Set up the entire database."""
    await init_database()
    await create_tables()
    await seed_initial_data()


if __name__ == "__main__":
    asyncio.run(setup_database())

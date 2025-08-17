#!/usr/bin/env python3
"""
Quick script to create an admin user for testing login.
"""

import asyncio
import uuid
from app.core.database import init_database, get_session
from app.core.security import SecurityManager
from app.models.tenant import Tenant
from app.models.user import User, UserType


async def create_admin_user():
    """Create admin user for the demo tenant."""
    print("Creating admin user...")
    
    await init_database()
    security = SecurityManager()
    
    async for session in get_session():
        # Get the demo tenant
        from sqlalchemy import select
        result = await session.execute(
            select(Tenant).where(Tenant.slug == "demo")
        )
        demo_tenant = result.scalar_one_or_none()
        
        if not demo_tenant:
            print("Demo tenant not found! Run setup_db.py first.")
            return
        
        print(f"Found demo tenant: {demo_tenant.name} (ID: {demo_tenant.id})")
        
        # Check if admin user already exists
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Admin user already exists!")
            return
        
        # Create admin user with explicit UUID
        admin_id = str(uuid.uuid4())
        admin_user = User(
            id=admin_id,  # Explicitly set UUID
            username="admin",
            email="admin@demo.hrms.com",
            first_name="Admin",
            last_name="User",
            hashed_password=security.get_password_hash("admin123"),
            is_verified=True,
            user_type=UserType.ADMIN,
            tenant_id=demo_tenant.id
        )
        
        session.add(admin_user)
        await session.commit()
        print(f"Admin user created successfully! ID: {admin_id}")
        break


if __name__ == "__main__":
    asyncio.run(create_admin_user())

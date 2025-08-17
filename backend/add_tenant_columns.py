"""
Manually add tenant_id columns to employees and departments tables.
"""

import asyncio
from app.core.database import get_session
from sqlalchemy import text, select
from app.models.tenant import Tenant

async def add_tenant_columns():
    """Manually add tenant_id columns."""
    async for session in get_session():
        try:
            # Get tenant ID
            tenant_result = await session.execute(select(Tenant))
            tenant = tenant_result.scalars().first()
            
            if not tenant:
                print("❌ No tenant found")
                return
                
            print(f"✅ Using tenant: {tenant.name} (ID: {tenant.id})")
            
            # Add tenant_id to departments
            await session.execute(text("ALTER TABLE departments ADD COLUMN tenant_id INTEGER"))
            await session.execute(text(f"UPDATE departments SET tenant_id = {tenant.id}"))
            await session.execute(text("ALTER TABLE departments ALTER COLUMN tenant_id SET NOT NULL"))
            print("✅ Added tenant_id to departments")
            
            # Add tenant_id to employees
            await session.execute(text("ALTER TABLE employees ADD COLUMN tenant_id INTEGER"))
            await session.execute(text(f"UPDATE employees SET tenant_id = {tenant.id}"))
            await session.execute(text("ALTER TABLE employees ALTER COLUMN tenant_id SET NOT NULL"))
            print("✅ Added tenant_id to employees")
            
            await session.commit()
            print("🎉 Successfully added tenant_id columns!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
        finally:
            await session.close()
        break

if __name__ == "__main__":
    asyncio.run(add_tenant_columns())

"""
Update existing employees and departments with tenant_id values.
This script adds tenant_id to existing data before applying model changes.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.core.database import get_session
from app.models.tenant import Tenant
from app.models.employee import Employee, Department


async def update_tenant_ids():
    """Update existing employees and departments with tenant_id."""
    print("🔧 Updating existing data with tenant_id values...")
    
    async for session in get_session():
        try:
            # Get the first tenant (assuming single tenant for seeding)
            tenant_result = await session.execute(select(Tenant))
            tenant = tenant_result.scalars().first()
            
            if not tenant:
                print("❌ No tenant found. Please ensure tenant data exists.")
                return
                
            print(f"✅ Using tenant: {tenant.name} (ID: {tenant.id})")
            
            # Add tenant_id column to departments if it doesn't exist
            try:
                await session.execute(text("ALTER TABLE departments ADD COLUMN IF NOT EXISTS tenant_id INTEGER"))
                await session.execute(text(f"UPDATE departments SET tenant_id = {tenant.id} WHERE tenant_id IS NULL"))
                await session.execute(text("ALTER TABLE departments ALTER COLUMN tenant_id SET NOT NULL"))
                print("✅ Updated departments with tenant_id")
            except Exception as e:
                print(f"⚠️ Departments already updated or error: {e}")
            
            # Add tenant_id column to employees if it doesn't exist
            try:
                await session.execute(text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS tenant_id INTEGER"))
                await session.execute(text(f"UPDATE employees SET tenant_id = {tenant.id} WHERE tenant_id IS NULL"))
                await session.execute(text("ALTER TABLE employees ALTER COLUMN tenant_id SET NOT NULL"))
                print("✅ Updated employees with tenant_id")
            except Exception as e:
                print(f"⚠️ Employees already updated or error: {e}")
            
            # Add foreign key constraints
            try:
                await session.execute(text("CREATE INDEX IF NOT EXISTS ix_departments_tenant_id ON departments (tenant_id)"))
                await session.execute(text("CREATE INDEX IF NOT EXISTS ix_employees_tenant_id ON employees (tenant_id)"))
                await session.execute(text("ALTER TABLE departments ADD CONSTRAINT IF NOT EXISTS departments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants (id)"))
                await session.execute(text("ALTER TABLE employees ADD CONSTRAINT IF NOT EXISTS employees_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants (id)"))
                print("✅ Added foreign key constraints and indexes")
            except Exception as e:
                print(f"⚠️ Constraints already exist or error: {e}")
            
            await session.commit()
            print("🎉 Successfully updated all existing data with tenant_id!")
            
        except Exception as e:
            print(f"❌ Error updating tenant_ids: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
        break


if __name__ == "__main__":
    asyncio.run(update_tenant_ids())

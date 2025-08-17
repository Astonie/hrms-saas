"""
Simple setup script to create a test admin user for development
"""
import asyncio
import sys
sys.path.append('/path/to/backend')
from app.core.database import get_session
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import hash_password
from sqlalchemy import text

async def create_test_user():
    async for db in get_session():
        try:
            # Check if demo tenant exists
            result = await db.execute(text("SELECT id, slug FROM public.tenants WHERE slug = 'demo' LIMIT 1"))
            tenant = result.fetchone()
            
            if not tenant:
                print("Demo tenant not found, creating...")
                # Create demo tenant
                await db.execute(text("""
                    INSERT INTO public.tenants (name, slug, contact_email, company_name, status, plan) 
                    VALUES ('Demo Company', 'demo', 'admin@demo.com', 'Demo Company Inc.', 'active', 'professional')
                """))
                await db.commit()
                
                # Get the created tenant
                result = await db.execute(text("SELECT id, slug FROM public.tenants WHERE slug = 'demo' LIMIT 1"))
                tenant = result.fetchone()
                
            print(f"Found/Created tenant: {tenant.slug} (ID: {tenant.id})")
            
            # Create tenant schema if not exists
            await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {tenant.slug}"))
            
            # Create users table in tenant schema
            await db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {tenant.slug}.users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_verified BOOLEAN DEFAULT TRUE,
                    user_type VARCHAR(20) DEFAULT 'admin',
                    tenant_id INTEGER REFERENCES public.tenants(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # Check if admin user exists
            result = await db.execute(text(f"SELECT username FROM {tenant.slug}.users WHERE username = 'admin' LIMIT 1"))
            existing_user = result.fetchone()
            
            if not existing_user:
                # Create admin user
                hashed_pw = hash_password("admin123")
                await db.execute(text(f"""
                    INSERT INTO {tenant.slug}.users 
                    (username, email, first_name, last_name, hashed_password, tenant_id, user_type) 
                    VALUES ('admin', 'admin@demo.com', 'Admin', 'User', :password, :tenant_id, 'admin')
                """), {"password": hashed_pw, "tenant_id": tenant.id})
                
                print("✅ Created admin user: admin / admin123")
            else:
                print("✅ Admin user already exists: admin")
                
            await db.commit()
            print("🎯 Setup completed successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(create_test_user())

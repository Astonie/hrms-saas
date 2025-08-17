import asyncio
from app.core.database import get_session
from sqlalchemy import text

async def check_tenants():
    async for db in get_session():
        try:
            result = await db.execute(text("SELECT name FROM tenants"))
            tenants = [r[0] for r in result.fetchall()]
            print(f"Tenants found: {tenants}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(check_tenants())

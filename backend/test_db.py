import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect('postgresql://postgres:passme123@localhost:5432/hrms_saas_db')
        await conn.close()
        print('Database connection successful!')
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())

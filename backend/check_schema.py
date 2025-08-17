import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def check_database_schema():
    try:
        # Connect to SQLite database (as configured in settings)
        engine = create_async_engine("sqlite+aiosqlite:///./dev.db")
        
        async with engine.begin() as conn:
            # Check what tables exist
            result = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in result.fetchall()]
            print("Tables in database:", tables)
            
            # Check departments table structure
            if 'departments' in tables:
                result = await conn.execute(
                    "PRAGMA table_info(departments)"
                )
                dept_columns = [(row[1], row[2]) for row in result.fetchall()]  # column name, type
                print("\nDepartments table columns:", dept_columns)
            
            # Check employees table structure
            if 'employees' in tables:
                result = await conn.execute(
                    "PRAGMA table_info(employees)"
                )
                emp_columns = [(row[1], row[2]) for row in result.fetchall()]
                print("\nEmployees table columns:", emp_columns)
                
            # Check leave_requests table structure
            if 'leave_requests' in tables:
                result = await conn.execute(
                    "PRAGMA table_info(leave_requests)"
                )
                leave_columns = [(row[1], row[2]) for row in result.fetchall()]
                print("\nLeave_requests table columns:", leave_columns)
                
        await engine.dispose()
    except Exception as e:
        print(f"Error checking schema: {e}")

if __name__ == "__main__":
    asyncio.run(check_database_schema())

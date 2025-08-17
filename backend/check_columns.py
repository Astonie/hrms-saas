"""
Check database columns for debugging.
"""

import asyncio
from app.core.database import get_session
from sqlalchemy import text

async def check_columns():
    """Check if tenant_id columns exist."""
    async for session in get_session():
        try:
            # Check employees table
            result = await session.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'employees' AND column_name = 'tenant_id'"
            ))
            emp_columns = result.fetchall()
            print(f"employees.tenant_id exists: {len(emp_columns) > 0}")
            
            # Check departments table  
            result = await session.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'departments' AND column_name = 'tenant_id'"
            ))
            dept_columns = result.fetchall()
            print(f"departments.tenant_id exists: {len(dept_columns) > 0}")
            
            # Check all columns in employees table
            result = await session.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'employees' ORDER BY ordinal_position"
            ))
            all_emp_columns = result.fetchall()
            print(f"All employees columns: {[col[0] for col in all_emp_columns]}")
            # Check all columns in departments table
            result = await session.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'departments' ORDER BY ordinal_position"
            ))
            all_dept_columns = result.fetchall()
            print(f"All departments columns: {[col[0] for col in all_dept_columns]}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await session.close()
        break

if __name__ == "__main__":
    asyncio.run(check_columns())

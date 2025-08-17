#!/usr/bin/env python3
import asyncio
from sqlalchemy import text
from app.core.database import get_session

async def check_schema():
    async for db in get_session():
        try:
            # Check departments table structure
            result = await db.execute(
                text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'departments' ORDER BY ordinal_position")
            )
            print("Department table columns:")
            for row in result.fetchall():
                print(f"  {row[0]} ({row[1]}, nullable: {row[2]})")
            
            # Check employees table structure  
            result = await db.execute(
                text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'employees' ORDER BY ordinal_position")
            )
            print("\nEmployee table columns:")
            for row in result.fetchall():
                print(f"  {row[0]} ({row[1]}, nullable: {row[2]})")
                
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())

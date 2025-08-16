"""
Database configuration and session management for HRMS-SAAS.
Handles multi-tenant database connections and schema management.
"""

import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text, MetaData
from sqlalchemy.pool import NullPool

from .config import settings

# Base class for all models
Base = declarative_base()

# Global engine and session factory
engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


async def create_database_engine() -> AsyncEngine:
    """Create and configure the database engine."""
    global engine
    
    if engine is None:
        engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    
    return engine


async def get_database_engine() -> AsyncEngine:
    """Get the database engine, creating it if necessary."""
    if engine is None:
        await create_database_engine()
    return engine


async def create_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create the session factory."""
    global async_session_maker
    
    if async_session_maker is None:
        engine = await get_database_engine()
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    return async_session_maker


async def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get the session factory, creating it if necessary."""
    if async_session_maker is None:
        await create_session_factory()
    return async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    session_factory = await get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database_connection():
    """Close the database connection."""
    global engine, async_session_maker
    
    if engine:
        await engine.dispose()
        engine = None
    
    async_session_maker = None


# Multi-tenant database management
class TenantDatabaseManager:
    """Manages multi-tenant database operations."""
    
    def __init__(self):
        self.tenant_engines: dict[str, AsyncEngine] = {}
        self.tenant_session_makers: dict[str, async_sessionmaker[AsyncSession]] = {}
    
    async def get_tenant_engine(self, tenant_id: str) -> AsyncEngine:
        """Get or create a database engine for a specific tenant."""
        if tenant_id not in self.tenant_engines:
            # Create tenant-specific engine with schema
            tenant_url = self._get_tenant_database_url(tenant_id)
            self.tenant_engines[tenant_id] = create_async_engine(
                tenant_url,
                echo=settings.database_echo,
                pool_size=5,  # Smaller pool for tenant connections
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
        
        return self.tenant_engines[tenant_id]
    
    async def get_tenant_session(self, tenant_id: str) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session for a specific tenant."""
        if tenant_id not in self.tenant_session_makers:
            engine = await self.get_tenant_engine(tenant_id)
            self.tenant_session_makers[tenant_id] = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        
        session_factory = self.tenant_session_makers[tenant_id]
        async with session_factory() as session:
            try:
                # Set the search path to the tenant's schema
                await session.execute(text(f'SET search_path TO "{tenant_id}", public'))
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def _get_tenant_database_url(self, tenant_id: str) -> str:
        """Generate database URL for a specific tenant."""
        # For schema-based multi-tenancy, we use the same database but different schemas
        # The schema will be set in the session
        return settings.database_url
    
    async def create_tenant_schema(self, tenant_id: str):
        """Create a new schema for a tenant."""
        async with get_session() as session:
            # Create the schema
            await session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{tenant_id}"'))
            await session.commit()
    
    async def drop_tenant_schema(self, tenant_id: str):
        """Drop a tenant's schema (dangerous operation)."""
        async with get_session() as session:
            # Drop the schema and all its contents
            await session.execute(text(f'DROP SCHEMA IF EXISTS "{tenant_id}" CASCADE'))
            await session.commit()
    
    async def tenant_exists(self, tenant_id: str) -> bool:
        """Check if a tenant schema exists."""
        async with get_session() as session:
            result = await session.execute(
                text("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = :tenant_id
                """),
                {"tenant_id": tenant_id}
            )
            return result.scalar() is not None
    
    async def list_tenants(self) -> list[str]:
        """List all tenant schemas."""
        async with get_session() as session:
            result = await session.execute(
                text("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'public')
                    AND schema_name NOT LIKE 'pg_%'
                """)
            )
            return [row[0] for row in result.fetchall()]
    
    async def close_tenant_connections(self, tenant_id: str):
        """Close connections for a specific tenant."""
        if tenant_id in self.tenant_engines:
            await self.tenant_engines[tenant_id].dispose()
            del self.tenant_engines[tenant_id]
        
        if tenant_id in self.tenant_session_makers:
            del self.tenant_session_makers[tenant_id]


# Global tenant database manager
tenant_db_manager = TenantDatabaseManager()


# Database initialization
async def init_database():
    """Initialize the database connection."""
    await create_database_engine()
    await create_session_factory()


async def close_database():
    """Close all database connections."""
    await close_database_connection()
    
    # Close all tenant connections
    for tenant_id in list(tenant_db_manager.tenant_engines.keys()):
        await tenant_db_manager.close_tenant_connections(tenant_id)


# Health check
async def check_database_health() -> bool:
    """Check if the database is healthy."""
    try:
        async with get_session() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False

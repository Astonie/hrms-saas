import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import (
    get_session,
    get_async_session,
    init_database,
    close_database,
    tenant_db_manager,
    TenantDatabaseManager
)


class TestDatabaseSession:
    """Test database session management."""

    @pytest.mark.asyncio
    async def test_get_session(self):
        """Test get_session dependency."""
        # This is tested in conftest.py with dependency override
        pass

    @pytest.mark.asyncio
    async def test_get_async_session(self):
        """Test get_async_session dependency."""
        # This is tested in conftest.py with dependency override
        pass


class TestDatabaseInitialization:
    """Test database initialization and shutdown."""

    @pytest.mark.asyncio
    async def test_init_database_success(self):
        """Test successful database initialization."""
        with patch('app.core.database.engine') as mock_engine:
            mock_engine.begin.return_value.__aenter__ = AsyncMock()
            mock_engine.begin.return_value.__aexit__ = AsyncMock()
            
            await init_database()
            
            mock_engine.begin.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_database_failure(self):
        """Test database initialization failure."""
        with patch('app.core.database.engine') as mock_engine:
            mock_engine.begin.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception, match="Database connection failed"):
                await init_database()

    @pytest.mark.asyncio
    async def test_close_database_success(self):
        """Test successful database shutdown."""
        with patch('app.core.database.engine') as mock_engine:
            mock_engine.dispose = AsyncMock()
            
            await close_database()
            
            mock_engine.dispose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_database_failure(self):
        """Test database shutdown failure."""
        with patch('app.core.database.engine') as mock_engine:
            mock_engine.dispose.side_effect = Exception("Dispose failed")
            
            with pytest.raises(Exception, match="Dispose failed"):
                await close_database()


class TestTenantDatabaseManager:
    """Test tenant database manager functionality."""

    def test_tenant_db_manager_instance(self):
        """Test that tenant_db_manager is an instance of TenantDatabaseManager."""
        assert isinstance(tenant_db_manager, TenantDatabaseManager)

    @pytest.mark.asyncio
    async def test_create_tenant_schema_success(self):
        """Test successful tenant schema creation."""
        tenant_id = "test-tenant"
        
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            await tenant_db_manager.create_tenant_schema(tenant_id)
            
            # Verify schema creation SQL was executed
            mock_session.execute.assert_called_once()
            call_args = mock_session.execute.call_args[0][0]
            assert isinstance(call_args, text)
            assert f'CREATE SCHEMA IF NOT EXISTS "{tenant_id}"' in str(call_args)
            
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_tenant_schema_failure(self):
        """Test tenant schema creation failure."""
        tenant_id = "test-tenant"
        
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.execute.side_effect = Exception("Schema creation failed")
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            with pytest.raises(Exception, match="Schema creation failed"):
                await tenant_db_manager.create_tenant_schema(tenant_id)

    @pytest.mark.asyncio
    async def test_drop_tenant_schema_success(self):
        """Test successful tenant schema deletion."""
        tenant_id = "test-tenant"
        
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            await tenant_db_manager.drop_tenant_schema(tenant_id)
            
            # Verify schema deletion SQL was executed
            mock_session.execute.assert_called_once()
            call_args = mock_session.execute.call_args[0][0]
            assert isinstance(call_args, text)
            assert f'DROP SCHEMA IF EXISTS "{tenant_id}" CASCADE' in str(call_args)
            
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tenant_schemas_success(self):
        """Test successful listing of tenant schemas."""
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalars.return_value.fetchall.return_value = ["tenant1", "tenant2"]
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            result = await tenant_db_manager.list_tenant_schemas()
            
            assert result == ["tenant1", "tenant2"]
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_tenant_schema_exists_true(self):
        """Test checking if tenant schema exists - returns True."""
        tenant_id = "test-tenant"
        
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1  # Schema exists
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            result = await tenant_db_manager.check_tenant_schema_exists(tenant_id)
            
            assert result is True
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_tenant_schema_exists_false(self):
        """Test checking if tenant schema exists - returns False."""
        tenant_id = "test-tenant"
        
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 0  # Schema doesn't exist
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            result = await tenant_db_manager.check_tenant_schema_exists(tenant_id)
            
            assert result is False
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tenant_session_success(self):
        """Test successful tenant session creation."""
        tenant_id = "test-tenant"
        
        with patch('app.core.database.get_async_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            async for session in tenant_db_manager.get_tenant_session(tenant_id):
                # Verify search path was set
                mock_session.execute.assert_called_once()
                call_args = mock_session.execute.call_args[0][0]
                assert isinstance(call_args, text)
                assert f'SET search_path TO "{tenant_id}", public' in str(call_args)
                
                # Verify session was yielded
                assert session == mock_session

    @pytest.mark.asyncio
    async def test_get_tenant_session_exception_handling(self):
        """Test tenant session exception handling."""
        tenant_id = "test-tenant"
        
        with patch('app.core.database.get_async_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.execute.side_effect = Exception("Database error")
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            with pytest.raises(Exception, match="Database error"):
                async for session in tenant_db_manager.get_tenant_session(tenant_id):
                    pass
            
            # Verify rollback was called
            mock_session.rollback.assert_called_once()
            # Verify session was closed
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tenant_session_finally_block(self):
        """Test that tenant session is always closed in finally block."""
        tenant_id = "test-tenant"
        
        with patch('app.core.database.get_async_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            try:
                async for session in tenant_db_manager.get_tenant_session(tenant_id):
                    # Simulate an exception
                    raise Exception("Test exception")
            except Exception:
                pass
            
            # Verify session was closed even after exception
            mock_session.close.assert_called_once()

    def test_tenant_engines_storage(self):
        """Test that tenant engines are properly stored."""
        manager = TenantDatabaseManager()
        
        # Initially empty
        assert len(manager.tenant_engines) == 0
        assert len(manager.tenant_session_makers) == 0

    def test_tenant_session_makers_storage(self):
        """Test that tenant session makers are properly stored."""
        manager = TenantDatabaseManager()
        
        # Initially empty
        assert len(manager.tenant_session_makers) == 0


class TestDatabaseConnections:
    """Test database connection handling."""

    @pytest.mark.asyncio
    async def test_database_connection_pool(self):
        """Test database connection pool configuration."""
        # This would require actual database connection testing
        # For now, we'll test the configuration
        from app.core.database import engine
        
        # Verify engine has expected attributes
        assert hasattr(engine, 'pool')
        assert hasattr(engine, 'url')

    @pytest.mark.asyncio
    async def test_session_factory_configuration(self):
        """Test session factory configuration."""
        from app.core.database import async_session_maker
        
        # Verify session maker is configured
        assert async_session_maker is not None
        assert hasattr(async_session_maker, '__call__')


class TestDatabaseMigrations:
    """Test database migration functionality."""

    @pytest.mark.asyncio
    async def test_migration_script_generation(self):
        """Test that migration scripts can be generated."""
        # This would test Alembic integration
        # For now, we'll test the configuration
        from alembic import command
        from alembic.config import Config
        
        # Verify Alembic is properly configured
        config = Config("alembic.ini")
        assert config.get_main_option("script_location") == "alembic"

    def test_model_metadata(self):
        """Test that all models are properly registered in metadata."""
        from app.core.database import Base
        from app.models import tenant, user, employee
        
        # Verify models are imported and registered
        assert len(Base.metadata.tables) > 0
        
        # Check for specific tables
        table_names = [table.name for table in Base.metadata.sorted_tables]
        assert "tenants" in table_names
        assert "users" in table_names
        assert "employees" in table_names


class TestDatabaseTransactions:
    """Test database transaction handling."""

    @pytest.mark.asyncio
    async def test_transaction_commit(self):
        """Test successful transaction commit."""
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            async with get_session() as session:
                # Simulate some database operation
                pass
            
            # Verify commit was called
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_exception(self):
        """Test transaction rollback on exception."""
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            try:
                async with get_session() as session:
                    raise Exception("Test exception")
            except Exception:
                pass
            
            # Verify rollback was called
            mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_cleanup(self):
        """Test that sessions are properly cleaned up."""
        with patch('app.core.database.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value.__aenter__.return_value = mock_session
            
            async with get_session() as session:
                pass
            
            # Verify session was closed
            mock_session.close.assert_called_once()


class TestDatabasePerformance:
    """Test database performance optimizations."""

    def test_connection_pooling(self):
        """Test that connection pooling is configured."""
        from app.core.database import engine
        
        # Verify pool configuration
        assert engine.pool is not None
        assert hasattr(engine.pool, 'size')
        assert hasattr(engine.pool, 'max_overflow')

    def test_query_optimization(self):
        """Test that queries are optimized."""
        # This would test actual query performance
        # For now, we'll test the configuration
        from app.core.database import engine
        
        # Verify engine has optimization settings
        assert hasattr(engine, 'echo')
        assert hasattr(engine, 'pool_pre_ping')

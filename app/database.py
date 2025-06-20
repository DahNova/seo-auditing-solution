from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine with optimized settings
engine_kwargs = {
    "echo": settings.database_echo,
}

# Add pooling settings only for PostgreSQL
if not settings.database_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_async_engine(settings.async_database_url, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Sync database engine for Celery tasks (avoids async/sync conflicts)
sync_engine_kwargs = {
    "echo": settings.database_echo,
}

# Add pooling settings only for PostgreSQL
if not settings.database_url.startswith("sqlite"):
    sync_engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    })

sync_engine = create_engine(settings.database_url, **sync_engine_kwargs)

# Create sync session factory for Celery tasks
SyncSessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_sync_db():
    """Dependency to get sync database session for Celery tasks"""
    with SyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

async def close_db():
    """Close database connections"""
    await engine.dispose()
    sync_engine.dispose()
    logger.info("Database connections closed")
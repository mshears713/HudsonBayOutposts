"""
Database Configuration and Session Management

This module provides asynchronous database engine and session management
for the Hudson Bay Expedition Console backend. It uses SQLAlchemy's async
capabilities with asyncpg driver for PostgreSQL.

The async pattern allows for non-blocking database operations, essential
for high-performance API endpoints handling concurrent requests.
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Configure logging for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variables
# Format: postgresql+asyncpg://user:password@host:port/database
# Default to a local PostgreSQL instance if not set
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://hudsonbay:hudsonbay@localhost:5432/hudsonbay"
)

# Ensure the connection string uses the async driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create the async engine
# pool_pre_ping=True ensures connections are healthy before use
# echo=True logs all SQL statements (disable in production)
try:
    engine: AsyncEngine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=10,  # Number of connections to maintain in the pool
        max_overflow=20,  # Max additional connections beyond pool_size
        pool_recycle=3600,  # Recycle connections after 1 hour
    )
    logger.info(f"Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Create async session factory
# This factory will be used to create new sessions for each request
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,  # Transactions must be explicitly committed
    autoflush=False,  # Don't auto-flush before queries
)

# Base class for all ORM models
# All database models will inherit from this
Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide database sessions for FastAPI routes.

    This async generator creates a new database session for each request
    and ensures proper cleanup after the request completes.

    Yields:
        AsyncSession: An async SQLAlchemy session

    Example:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()

    Error Handling:
        - Logs any SQLAlchemy errors during session lifecycle
        - Automatically rolls back transactions on error
        - Always closes the session to prevent connection leaks
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Database session created")
            yield session
            # If no exception, commit the transaction
            await session.commit()
            logger.debug("Database session committed")
        except SQLAlchemyError as e:
            # On error, rollback the transaction
            logger.error(f"Database error occurred: {e}")
            await session.rollback()
            raise
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error in database session: {e}")
            await session.rollback()
            raise
        finally:
            # Always close the session
            await session.close()
            logger.debug("Database session closed")


async def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This function should be called during application startup to ensure
    all database tables are created before handling requests.

    Note:
        In production, use Alembic migrations instead of this function
        to manage database schema changes.
    """
    try:
        async with engine.begin() as conn:
            # Create all tables defined in models
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """
    Close all database connections.

    This function should be called during application shutdown to ensure
    clean termination of database connections.
    """
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise

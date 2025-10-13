import os
from typing import AsyncGenerator
from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import uuid

# Database configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'memory_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# SQLAlchemy async setup - configurable echo for debugging
SQL_ECHO = os.getenv('SQL_ECHO', 'False').lower() == 'true'
engine = create_async_engine(DATABASE_URL, echo=SQL_ECHO)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# SQLAlchemy Model
class MemoryModel(Base):
    """
    Memory model for storing user memories.

    Attributes:
        id: Unique identifier for the memory
        user_id: User who owns the memory (indexed for query performance)
        content: The memory text content
        created_at: Timestamp when memory was created
        updated_at: Timestamp when memory was last updated
    """
    __tablename__ = "memories"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True, name='ix_memories_user_id')
    content = Column(Text, nullable=False)
    # Using lambdas for application-level defaults (allows testing with custom timestamps)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.

    Yields:
        AsyncSession: Database session for use in endpoints

    Note:
        Session is automatically closed in the finally block, even if an exception occurs.
        This ensures proper resource cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, delete
from sqlalchemy.exc import SQLAlchemyError
from app.database import MemoryModel
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryData:
    """Data class representing a memory entry with content and timestamps."""
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_model(model: MemoryModel) -> 'MemoryData':
        """
        Convert a MemoryModel ORM instance to a MemoryData dataclass.

        Args:
            model: SQLAlchemy MemoryModel instance

        Returns:
            MemoryData instance with data from the model
        """
        return MemoryData(
            id=model.id,
            user_id=model.user_id,
            content=model.content,
            created_at=model.created_at,
            updated_at=model.updated_at
        )


class MemoryService:
    """Service for memory operations using PostgreSQL with SQLAlchemy."""

    async def create_memory(self, db_session: AsyncSession, user_id: UUID, content: str) -> MemoryData:
        """
        Create a new memory.

        Args:
            db_session: Database session
            user_id: User ID who owns the memory
            content: Memory content text

        Returns:
            MemoryData: The created memory

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            memory_id = uuid4()
            now = datetime.now(timezone.utc)

            db_memory = MemoryModel(
                id=memory_id,
                user_id=user_id,
                content=content,
                created_at=now,
                updated_at=now
            )

            db_session.add(db_memory)
            await db_session.commit()
            await db_session.refresh(db_memory)

            return MemoryData.from_model(db_memory)
        except SQLAlchemyError as e:
            await db_session.rollback()
            logger.error(f"Failed to create memory: {e}")
            raise

    async def get_memory(self, db_session: AsyncSession, memory_id: UUID, user_id: UUID) -> Optional[MemoryData]:
        """
        Get a memory by ID with authorization check.

        Args:
            db_session: Database session
            memory_id: Memory ID to retrieve
            user_id: User ID for authorization check

        Returns:
            MemoryData if found and authorized, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            stmt = select(MemoryModel).filter(
                MemoryModel.id == memory_id,
                MemoryModel.user_id == user_id
            )
            result = await db_session.execute(stmt)
            db_memory = result.scalar_one_or_none()

            if not db_memory:
                return None

            return MemoryData.from_model(db_memory)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            raise

    async def update_memory(self, db_session: AsyncSession, memory_id: UUID, content: str, user_id: UUID) -> Optional[MemoryData]:
        """
        Update an existing memory's content with authorization check.

        Args:
            db_session: Database session
            memory_id: Memory ID to update
            content: New content text
            user_id: User ID for authorization check

        Returns:
            MemoryData if found and updated, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            stmt = select(MemoryModel).filter(
                MemoryModel.id == memory_id,
                MemoryModel.user_id == user_id
            )
            result = await db_session.execute(stmt)
            db_memory = result.scalar_one_or_none()

            if not db_memory:
                return None

            db_memory.content = content
            db_memory.updated_at = datetime.now(timezone.utc)

            await db_session.commit()
            await db_session.refresh(db_memory)

            return MemoryData.from_model(db_memory)
        except SQLAlchemyError as e:
            await db_session.rollback()
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise

    async def search_memories(self, db_session: AsyncSession, user_id: UUID, query: str) -> list[MemoryData]:
        """
        Search user's memories using case-insensitive substring matching.

        Args:
            db_session: Database session
            user_id: User ID to search memories for
            query: Search query string

        Returns:
            List of matching MemoryData objects

        Raises:
            SQLAlchemyError: If database operation fails
        """
        if not query or not query.strip():
            return []

        try:
            stmt = select(MemoryModel).filter(
                MemoryModel.user_id == user_id,
                func.lower(MemoryModel.content).contains(query.lower())
            ).order_by(MemoryModel.created_at.desc())

            result = await db_session.execute(stmt)
            db_memories = result.scalars().all()

            return [MemoryData.from_model(mem) for mem in db_memories]
        except SQLAlchemyError as e:
            logger.error(f"Failed to search memories for user {user_id}: {e}")
            raise

    async def delete_memory(self, db_session: AsyncSession, memory_id: UUID, user_id: UUID) -> bool:
        """
        Delete a memory with authorization check.

        Args:
            db_session: Database session
            memory_id: Memory ID to delete
            user_id: User ID for authorization check

        Returns:
            True if deleted, False if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            stmt = select(MemoryModel).filter(
                MemoryModel.id == memory_id,
                MemoryModel.user_id == user_id
            )
            result = await db_session.execute(stmt)
            db_memory = result.scalar_one_or_none()

            if db_memory:
                await db_session.delete(db_memory)
                await db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await db_session.rollback()
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise

    async def clear_memories(self, db_session: AsyncSession) -> int:
        """
        Clear all memories - useful for testing only.

        Args:
            db_session: Database session

        Returns:
            Number of memories deleted

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            stmt = delete(MemoryModel)
            result = await db_session.execute(stmt)
            await db_session.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            await db_session.rollback()
            logger.error(f"Failed to clear memories: {e}")
            raise

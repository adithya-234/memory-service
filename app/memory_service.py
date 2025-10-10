from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from database import MemoryModel


@dataclass
class MemoryData:
    """Data class representing a memory entry with content and timestamps."""
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime


class MemoryService:
    """Service for memory operations using PostgreSQL with SQLAlchemy."""

    async def create_memory(self, db_session: AsyncSession, user_id: UUID, content: str) -> MemoryData:
        """Create a new memory."""
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

        return MemoryData(
            id=db_memory.id,
            user_id=db_memory.user_id,
            content=db_memory.content,
            created_at=db_memory.created_at,
            updated_at=db_memory.updated_at
        )

    async def get_memory(self, db_session: AsyncSession, memory_id: UUID, user_id: UUID) -> Optional[MemoryData]:
        """Get a memory by ID with authorization check."""
        stmt = select(MemoryModel).filter(
            MemoryModel.id == memory_id,
            MemoryModel.user_id == user_id
        )
        result = await db_session.execute(stmt)
        db_memory = result.scalar_one_or_none()

        if not db_memory:
            return None

        return MemoryData(
            id=db_memory.id,
            user_id=db_memory.user_id,
            content=db_memory.content,
            created_at=db_memory.created_at,
            updated_at=db_memory.updated_at
        )

    async def update_memory(self, db_session: AsyncSession, memory_id: UUID, content: str, user_id: UUID) -> Optional[MemoryData]:
        """Update an existing memory's content with authorization check."""
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

        return MemoryData(
            id=db_memory.id,
            user_id=db_memory.user_id,
            content=db_memory.content,
            created_at=db_memory.created_at,
            updated_at=db_memory.updated_at
        )

    async def search_memories(self, db_session: AsyncSession, user_id: UUID, query: str) -> list[MemoryData]:
        """Search user's memories using case-insensitive substring matching."""
        if not query or not query.strip():
            return []

        stmt = select(MemoryModel).filter(
            MemoryModel.user_id == user_id,
            func.lower(MemoryModel.content).contains(query.lower())
        ).order_by(MemoryModel.created_at.desc())

        result = await db_session.execute(stmt)
        db_memories = result.scalars().all()

        return [
            MemoryData(
                id=mem.id,
                user_id=mem.user_id,
                content=mem.content,
                created_at=mem.created_at,
                updated_at=mem.updated_at
            )
            for mem in db_memories
        ]

    async def delete_memory(self, db_session: AsyncSession, memory_id: UUID, user_id: UUID) -> bool:
        """Delete a memory with authorization check."""
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

    async def clear_memories(self, db_session: AsyncSession):
        """Clear all memories - useful for testing."""
        stmt = select(MemoryModel)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()
        for memory in memories:
            await db_session.delete(memory)
        await db_session.commit()

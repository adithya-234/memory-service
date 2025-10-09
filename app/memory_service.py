from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func
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

    def create_memory(self, db_session: Session, user_id: UUID, content: str) -> MemoryData:
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
        db_session.commit()
        db_session.refresh(db_memory)

        return MemoryData(
            id=db_memory.id,
            user_id=db_memory.user_id,
            content=db_memory.content,
            created_at=db_memory.created_at,
            updated_at=db_memory.updated_at
        )

    def get_memory(self, db_session: Session, memory_id: UUID, user_id: UUID) -> Optional[MemoryData]:
        """Get a memory by ID with authorization check."""
        db_memory = db_session.query(MemoryModel).filter(
            MemoryModel.id == memory_id,
            MemoryModel.user_id == user_id
        ).first()

        if not db_memory:
            return None

        return MemoryData(
            id=db_memory.id,
            user_id=db_memory.user_id,
            content=db_memory.content,
            created_at=db_memory.created_at,
            updated_at=db_memory.updated_at
        )

    def update_memory(self, db_session: Session, memory_id: UUID, content: str, user_id: UUID) -> Optional[MemoryData]:
        """Update an existing memory's content with authorization check."""
        db_memory = db_session.query(MemoryModel).filter(
            MemoryModel.id == memory_id,
            MemoryModel.user_id == user_id
        ).first()

        if not db_memory:
            return None

        db_memory.content = content
        db_memory.updated_at = datetime.now(timezone.utc)

        db_session.commit()
        db_session.refresh(db_memory)

        return MemoryData(
            id=db_memory.id,
            user_id=db_memory.user_id,
            content=db_memory.content,
            created_at=db_memory.created_at,
            updated_at=db_memory.updated_at
        )

    def search_memories(self, db_session: Session, user_id: UUID, query: str) -> list[MemoryData]:
        """Search user's memories using case-insensitive substring matching."""
        if not query or not query.strip():
            return []

        db_memories = db_session.query(MemoryModel).filter(
            MemoryModel.user_id == user_id,
            func.lower(MemoryModel.content).contains(query.lower())
        ).order_by(MemoryModel.created_at.desc()).all()

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

    def delete_memory(self, db_session: Session, memory_id: UUID, user_id: UUID) -> bool:
        """Delete a memory with authorization check."""
        result = db_session.query(MemoryModel).filter(
            MemoryModel.id == memory_id,
            MemoryModel.user_id == user_id
        ).delete()

        db_session.commit()
        return result > 0

    def clear_memories(self, db_session: Session):
        """Clear all memories - useful for testing."""
        db_session.query(MemoryModel).delete()
        db_session.commit()

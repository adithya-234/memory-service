from typing import Dict, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass
from threading import Lock


@dataclass
class MemoryData:
    """Data class representing a memory entry with content and timestamps."""
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime


class MemoryService:
    """Service for thread-safe memory operations including create, read, update, delete, and search."""
    def __init__(self):
        self.memories: Dict[UUID, MemoryData] = {}
        self._lock = Lock()

    def create_memory(self, user_id: UUID, content: str) -> MemoryData:
        with self._lock:
            memory_id = uuid4()
            now = datetime.now(timezone.utc)

            memory = MemoryData(
                id=memory_id,
                user_id=user_id,
                content=content,
                created_at=now,
                updated_at=now,
            )

            self.memories[memory_id] = memory
            return memory

    def get_memory(self, memory_id: UUID) -> Optional[MemoryData]:
        return self.memories.get(memory_id)

    def update_memory(self, memory_id: UUID, content: str, user_id: UUID) -> Optional[MemoryData]:
        """Update an existing memory's content with authorization check."""
        with self._lock:
            memory = self.memories.get(memory_id)
            if not memory:
                return None

            # Authorization check: ensure user owns the memory
            if memory.user_id != user_id:
                return None

            # Create a new instance instead of mutating the existing one
            updated_memory = MemoryData(
                id=memory.id,
                user_id=memory.user_id,
                content=content,
                created_at=memory.created_at,
                updated_at=datetime.now(timezone.utc)
            )
            self.memories[memory_id] = updated_memory
            return updated_memory

    def search_memories(self, user_id: UUID, query: str) -> list[MemoryData]:
        """Search user's memories using case-insensitive substring matching."""
        with self._lock:
            # Validate query - return empty list for empty queries
            if not query or not query.strip():
                return []

            results = []
            query_lower = query.lower()
            for memory in self.memories.values():
                if memory.user_id == user_id and query_lower in memory.content.lower():
                    results.append(memory)
            return results

    def delete_memory(self, memory_id: UUID, user_id: UUID) -> bool:
        """Delete a memory with authorization check."""
        with self._lock:
            memory = self.memories.get(memory_id)
            if not memory:
                return False

            # Authorization check: ensure user owns the memory
            if memory.user_id != user_id:
                return False

            # Use pop for atomic operation
            self.memories.pop(memory_id)
            return True

    def clear_memories(self):
        self.memories.clear()

from typing import Dict, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass
from threading import Lock


@dataclass
class MemoryData:
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime


class MemoryService:
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

    def update_memory(self, memory_id: UUID, content: str) -> Optional[MemoryData]:
        with self._lock:
            memory = self.memories.get(memory_id)
            if not memory:
                return None

            memory.content = content
            memory.updated_at = datetime.now(timezone.utc)
            return memory

    def search_memories(self, user_id: UUID, query: str) -> list[MemoryData]:
        with self._lock:
            results = []
            query_lower = query.lower()
            for memory in self.memories.values():
                if memory.user_id == user_id and query_lower in memory.content.lower():
                    results.append(memory)
            return results

    def delete_memory(self, memory_id: UUID) -> bool:
        with self._lock:
            if memory_id in self.memories:
                del self.memories[memory_id]
                return True
            return False

    def clear_memories(self):
        self.memories.clear()

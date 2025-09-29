from typing import Dict, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass


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

    def create_memory(self, user_id: UUID, content: str) -> MemoryData:
        memory_id = uuid4()
        now = datetime.now(timezone.utc)

        memory = MemoryData(
            id=memory_id,
            user_id=user_id,
            content=content,
            created_at=now,
            updated_at=now
        )

        self.memories[memory_id] = memory
        return memory

    def get_memory(self, memory_id: UUID) -> Optional[MemoryData]:
        return self.memories.get(memory_id)

    def clear_memories(self):
        self.memories.clear()
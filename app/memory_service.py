from typing import Dict, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import or_
from .models import Memory


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

    def __init__(self, db: Session):
        self.db=db
        

    def create_memory(self, user_id: UUID, content: str) -> MemoryData:
        memory=Memory(
            id=uuid4(),
            user_id=user_id,
            content=content,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)

        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return self._to_memory_data(memory)
     

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
        memory=self.db.query(Memory).filter(Memory.id==memory_id).first()
        if not memory:
            return None
        return self._to_memory_data(memory)

    def update_memory(self, memory_id: UUID, content: str, user_id: UUID) -> Optional[MemoryData]:

        """Update an existing memory's content with authorization check."""
        memory=self.db.query(Memory).filter(Memory.id==memory_id).first()
        if not memory:
            return None
        if memory.user_id!=user_id:
            return None
        memory.content=content
        memory.updated_at=datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(memory)
        return self._to_memory_data(memory)
    

       

    def search_memories(self, user_id: UUID, query: str) -> list[MemoryData]:
        """Search user's memories using case-insensitive substring matching."""
        if not query or not query.strip():
            return []
        search_pattern=f"%{query}%"
        memories=self.db.query(Memory).filter(
            Memory.user_id==user_id,
            Memory.content.ilike(search_pattern)

        ).all()
        return [self._to_memory_data(memory) for memory in memories]
            
            
            

            

    def delete_memory(self, memory_id: UUID, user_id: UUID) -> bool:
            memory=self.db.query(Memory).filter(Memory.id==memory_id).first()
            if not memory:
                return False
            if memory.user_id!=user_id:
                return False
            self.db.delete(memory)
            self.db.commit()

        
            return True

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

        self.db.query(Memory).delete()
        self.db.commit()

    @staticmethod
    def _to_memory_data(memory: Memory) -> MemoryData:
           return MemoryData(
              id=memory.id,
              user_id=memory.user_id,
              content=memory.content,
              created_at=memory.created_at,
              updated_at=memory.updated_at
          )
       
         


        self.memories.clear()


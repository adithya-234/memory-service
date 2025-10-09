from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, Annotated
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from app.memory_service import MemoryData, MemoryService
from app.database import get_db, engine
from app import models



VERSION = "1.0.0"

app = FastAPI(
    title="Memory Service",
    description="Memory service for storing and retrieving user memories",
    version=VERSION,
)

# Create tables on startup
models.Base.metadata.create_all(bind=engine)


class MemoryRequest(BaseModel):
    content: str


class MemoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime


class SearchRequest(BaseModel):
    query: str


@app.get("/")
async def root():
    """Root endpoint returning service information."""
    return {
        "message": "Welcome to the Memory Service",
        "service": "memory-service",
        "version": VERSION,
    }


@app.post("/memories", response_model=MemoryResponse)
async def create_memory_endpoint(
    memory: MemoryRequest,
    user_id: Annotated[UUID, Header()],
    db: Session = Depends(get_db)
):
    """Create a new memory for the user."""
    memory_service = MemoryService(db)
    memory_data = memory_service.create_memory(user_id, memory.content)

    return MemoryResponse(
        id=memory_data.id,
        user_id=memory_data.user_id,
        content=memory_data.content,
        created_at=memory_data.created_at,
        updated_at=memory_data.updated_at,
    )


@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory_endpoint(memory_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a memory by its ID."""
    memory_service = MemoryService(db)
    memory_data = memory_service.get_memory(memory_id)

    if not memory_data:
        raise HTTPException(status_code=404, detail="Memory not found")

    return MemoryResponse(
        id=memory_data.id,
        user_id=memory_data.user_id,
        content=memory_data.content,
        created_at=memory_data.created_at,
        updated_at=memory_data.updated_at,
    )


@app.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory_endpoint(
    memory_id: UUID,
    memory: MemoryRequest,
    user_id: Annotated[UUID, Header()],
    db: Session = Depends(get_db)
):
    """Update an existing memory's content."""
    memory_service = MemoryService(db)
    memory_data = memory_service.update_memory(memory_id, memory.content, user_id)
    if not memory_data:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryResponse(
        id=memory_data.id,
        user_id=memory_data.user_id,
        content=memory_data.content,
        created_at=memory_data.created_at,
        updated_at=memory_data.updated_at,
    )


@app.post("/memories/search", response_model=list[MemoryResponse])
async def search_memories_endpoint(
    search: SearchRequest,
    user_id: Annotated[UUID, Header()],
    db: Session = Depends(get_db)
):
    """Search for memories matching the query."""
    memory_service = MemoryService(db)
    memories = memory_service.search_memories(user_id, search.query)
    return [
        MemoryResponse(
            id=memory.id,
            user_id=memory.user_id,
            content=memory.content,
            created_at=memory.created_at,
            updated_at=memory.updated_at,
        )
        for memory in memories
    ]


@app.delete("/memories/{memory_id}")
async def delete_memory_endpoint(
    memory_id: UUID,
    user_id: Annotated[UUID, Header()],
    db: Session = Depends(get_db)
):
    """Delete a memory."""
    memory_service = MemoryService(db)
    deleted = memory_service.delete_memory(memory_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully", "id": memory_id}

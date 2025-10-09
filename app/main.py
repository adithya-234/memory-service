from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, Annotated
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from memory_service import MemoryService, MemoryData
from database import get_db, init_db


VERSION = "1.0.0"

app = FastAPI(
    title="Memory Service",
    description="Memory service for storing and retrieving user memories",
    version=VERSION,
)

memory_service = MemoryService()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


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
    db_session: Session = Depends(get_db)
):
    """Create a new memory for the user."""
    memory_data = memory_service.create_memory(db_session, user_id, memory.content)
    return MemoryResponse(
        id=memory_data.id,
        user_id=memory_data.user_id,
        content=memory_data.content,
        created_at=memory_data.created_at,
        updated_at=memory_data.updated_at,
    )


@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory_endpoint(
    memory_id: UUID,
    user_id: Annotated[UUID, Header()],
    db_session: Session = Depends(get_db)
):
    """Retrieve a memory by its ID."""
    memory_data = memory_service.get_memory(db_session, memory_id, user_id)
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
    db_session: Session = Depends(get_db)
):
    """Update an existing memory's content."""
    memory_data = memory_service.update_memory(db_session, memory_id, memory.content, user_id)
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
    memory_id: Annotated[UUID, Header()],
    db_session: Session = Depends(get_db)
):
    """Search for memories matching the query."""
    # Verify the memory exists and belongs to the user
    memory_exists = memory_service.get_memory(db_session, memory_id, user_id)
    if not memory_exists:
        raise HTTPException(status_code=404, detail="Memory not found")

    memories = memory_service.search_memories(db_session, user_id, search.query)
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
    db_session: Session = Depends(get_db)
):
    """Delete a memory."""
    deleted = memory_service.delete_memory(db_session, memory_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully", "id": memory_id}

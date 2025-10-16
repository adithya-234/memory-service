from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, Annotated
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.memory_service import MemoryService, MemoryData
from app.database import get_db, init_db


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
    await init_db()


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


def to_memory_response(memory: MemoryData) -> MemoryResponse:
    """
    Convert MemoryData to MemoryResponse.

    Args:
        memory: MemoryData instance

    Returns:
        MemoryResponse for API response
    """
    return MemoryResponse(
        id=memory.id,
        user_id=memory.user_id,
        content=memory.content,
        created_at=memory.created_at,
        updated_at=memory.updated_at,
    )


@app.get("/")
async def root() -> Dict[str, str]:
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
    db_session: AsyncSession = Depends(get_db)
):
    """Create a new memory for the user."""
    memory_data = await memory_service.create_memory(db_session, user_id, memory.content)
    return to_memory_response(memory_data)


@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory_endpoint(
    memory_id: UUID,
    user_id: Annotated[UUID, Header()],
    db_session: AsyncSession = Depends(get_db)
):
    """Retrieve a memory by its ID."""
    memory_data = await memory_service.get_memory(db_session, memory_id, user_id)
    if not memory_data:
        raise HTTPException(status_code=404, detail="Memory not found")

    return to_memory_response(memory_data)


@app.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory_endpoint(
    memory_id: UUID,
    memory: MemoryRequest,
    user_id: Annotated[UUID, Header()],
    db_session: AsyncSession = Depends(get_db)
):
    """Update an existing memory's content."""
    memory_data = await memory_service.update_memory(db_session, memory_id, memory.content, user_id)
    if not memory_data:
        raise HTTPException(status_code=404, detail="Memory not found")
    return to_memory_response(memory_data)


@app.post("/memories/search", response_model=list[MemoryResponse])
async def search_memories_endpoint(
    search: SearchRequest,
    user_id: Annotated[UUID, Header()],
    db_session: AsyncSession = Depends(get_db)
):
    """Search for memories matching the query."""
    memories = await memory_service.search_memories(db_session, user_id, search.query)
    return [to_memory_response(memory) for memory in memories]


@app.delete("/memories/{memory_id}")
async def delete_memory_endpoint(
    memory_id: UUID,
    user_id: Annotated[UUID, Header()],
    db_session: AsyncSession = Depends(get_db)
):
    """Delete a memory."""
    deleted = await memory_service.delete_memory(db_session, memory_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully", "id": memory_id}

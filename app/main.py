from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, Annotated
from datetime import datetime, timezone
from uuid import UUID, uuid4
from .memory_service import MemoryService, MemoryData


VERSION = "1.0.0"

app = FastAPI(
    title="Memory Service",
    description="Memory service for storing and retrieving user memories",
    version=VERSION,
)

memory_service = MemoryService()


class MemoryRequest(BaseModel):
    content: str
    
    



class MemoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Memory Service",
        "service": "memory-service",
        "version": VERSION,
    }


@app.post("/memories", response_model=MemoryResponse)
async def create_memory_endpoint(memory: MemoryRequest, user_id: Annotated[UUID , Header()]):
    memory_data = memory_service.create_memory(user_id, memory.content)
    return MemoryResponse(
        id=memory_data.id,
        user_id=memory_data.user_id,
        content=memory_data.content,
        created_at=memory_data.created_at,
        updated_at=memory_data.updated_at
    )


@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory_endpoint(memory_id: UUID):
    memory_data = memory_service.get_memory(memory_id)
    if not memory_data:
        raise HTTPException(status_code=404, detail="Memory not found")

    return MemoryResponse(
        id=memory_data.id,
        user_id=memory_data.user_id,
        content=memory_data.content,
        created_at=memory_data.created_at,
        updated_at=memory_data.updated_at
    )



from uuid import uuid4
from app.memory_service import MemoryService


def test_create_memory():
    service = MemoryService()
    user_id = uuid4()
    content = "test memory"

    memory = service.create_memory(user_id, content)

    assert memory.content == content
    assert memory.user_id == user_id
    assert memory.id is not None
    assert memory.created_at is not None
    assert memory.updated_at is not None


def test_get_memory():
    service = MemoryService()
    user_id = uuid4()
    content = "test memory"

    created_memory = service.create_memory(user_id, content)
    memory_id = created_memory.id

    retrieved_memory = service.get_memory(memory_id)

    assert retrieved_memory is not None
    assert retrieved_memory.id == memory_id
    assert retrieved_memory.content == content
    assert retrieved_memory.user_id == user_id


def test_get_nonexistent_memory():
    service = MemoryService()
    nonexistent_id = uuid4()

    memory = service.get_memory(nonexistent_id)

    assert memory is None

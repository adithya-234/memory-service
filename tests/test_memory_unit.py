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


def test_update_memory():
    service = MemoryService()
    user_id = uuid4()
    content = "original content"

    created_memory = service.create_memory(user_id, content)
    memory_id = created_memory.id

    new_content = "updated content"
    updated_memory = service.update_memory(memory_id, new_content)

    assert updated_memory is not None
    assert updated_memory.content == new_content
    assert updated_memory.updated_at > created_memory.updated_at


def test_update_nonexistent_memory():
    service = MemoryService()
    nonexistent_id = uuid4()

    updated_memory = service.update_memory(nonexistent_id, "new content")

    assert updated_memory is None


def test_delete_memory():
    service = MemoryService()
    user_id = uuid4()

    created_memory = service.create_memory(user_id, "test memory")
    memory_id = created_memory.id

    result = service.delete_memory(memory_id)

    assert result is True
    assert service.get_memory(memory_id) is None


def test_delete_nonexistent_memory():
    service = MemoryService()
    nonexistent_id = uuid4()

    result = service.delete_memory(nonexistent_id)

    assert result is False


def test_search_memories():
    service = MemoryService()
    user_id = uuid4()

    service.create_memory(user_id, "python programming")
    service.create_memory(user_id, "java development")

    results = service.search_memories(user_id, "python")

    assert len(results) == 1
    assert results[0].content == "python programming"

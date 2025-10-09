from uuid import uuid4
from app.memory_service import MemoryService
import threading
import time


def test_create_memory(db_session):
    service = MemoryService(db_session)
    user_id = uuid4()
    content = "test memory"

    memory = service.create_memory(user_id, content)

    assert memory.content == content
    assert memory.user_id == user_id
    assert memory.id is not None
    assert memory.created_at is not None
    assert memory.updated_at is not None


def test_get_memory(db_session):
    service = MemoryService(db_session)
    user_id = uuid4()
    content = "test memory"

    created_memory = service.create_memory(user_id, content)
    memory_id = created_memory.id

    retrieved_memory = service.get_memory(memory_id)

    assert retrieved_memory is not None
    assert retrieved_memory.id == memory_id
    assert retrieved_memory.content == content
    assert retrieved_memory.user_id == user_id


def test_get_nonexistent_memory(db_session):
    service = MemoryService(db_session)
    nonexistent_id = uuid4()

    memory = service.get_memory(nonexistent_id)

    assert memory is None


def test_update_memory(db_session):
    service = MemoryService(db_session)
    user_id = uuid4()
    content = "original content"

    created_memory = service.create_memory(user_id, content)
    memory_id = created_memory.id

    new_content = "updated content"
    updated_memory = service.update_memory(memory_id, new_content, user_id)

    assert updated_memory is not None
    assert updated_memory.content == new_content
    assert updated_memory.updated_at >= created_memory.updated_at


def test_update_nonexistent_memory(db_session):
    service = MemoryService(db_session)
    nonexistent_id = uuid4()
    user_id = uuid4()

    updated_memory = service.update_memory(nonexistent_id, "new content", user_id)

    assert updated_memory is None


def test_delete_memory(db_session):
    service = MemoryService(db_session)
    user_id = uuid4()

    created_memory = service.create_memory(user_id, "test memory")
    memory_id = created_memory.id

    result = service.delete_memory(memory_id, user_id)

    assert result is True
    assert service.get_memory(memory_id) is None


def test_delete_nonexistent_memory(db_session):
    service = MemoryService(db_session)
    nonexistent_id = uuid4()
    user_id = uuid4()

    result = service.delete_memory(nonexistent_id, user_id)

    assert result is False


def test_search_memories(db_session):
    service = MemoryService(db_session)
    user_id = uuid4()

    service.create_memory(user_id, "python programming")
    service.create_memory(user_id, "java development")

    results = service.search_memories(user_id, "python")

    assert len(results) == 1
    assert results[0].content == "python programming"


def test_update_memory_unauthorized(db_session):
    """Test that a user cannot update another user's memory"""
    service = MemoryService(db_session)
    user1_id = uuid4()
    user2_id = uuid4()

    # User 1 creates a memory
    created_memory = service.create_memory(user1_id, "user1's memory")
    memory_id = created_memory.id

    # User 2 tries to update it
    updated_memory = service.update_memory(memory_id, "hacked content", user2_id)

    assert updated_memory is None
    # Verify original memory is unchanged
    original = service.get_memory(memory_id)
    assert original.content == "user1's memory"


def test_delete_memory_unauthorized(db_session):
    """Test that a user cannot delete another user's memory"""
    service = MemoryService(db_session)
    user1_id = uuid4()
    user2_id = uuid4()

    # User 1 creates a memory
    created_memory = service.create_memory(user1_id, "user1's memory")
    memory_id = created_memory.id

    # User 2 tries to delete it
    result = service.delete_memory(memory_id, user2_id)

    assert result is False
    # Verify memory still exists
    memory = service.get_memory(memory_id)
    assert memory is not None


def test_search_memories_empty_query(db_session):
    """Test that empty query returns empty list"""
    service = MemoryService(db_session)
    user_id = uuid4()

    service.create_memory(user_id, "test memory")

    # Empty string
    results = service.search_memories(user_id, "")
    assert len(results) == 0
    results = service.search_memories(user_id, "   ")
    assert len(results) == 0



def test_search_memories_user_with_no_memories(db_session):
    """Test search for user with no memories"""
    service = MemoryService(db_session)
    user_id = uuid4()

    results = service.search_memories(user_id, "anything")
    assert len(results) == 0




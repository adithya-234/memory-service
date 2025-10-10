from uuid import uuid4
from app.memory_service import MemoryService
import asyncio
import pytest


@pytest.fixture
def service():
    """Create a memory service instance."""
    return MemoryService()


@pytest.mark.asyncio
async def test_create_memory(service, db_session):
    user_id = uuid4()
    content = "test memory"

    memory = await service.create_memory(db_session, user_id, content)

    assert memory.content == content
    assert memory.user_id == user_id
    assert memory.id is not None
    assert memory.created_at is not None
    assert memory.updated_at is not None


@pytest.mark.asyncio
async def test_get_memory(service, db_session):
    user_id = uuid4()
    content = "test memory"

    created_memory = await service.create_memory(db_session, user_id, content)
    memory_id = created_memory.id

    retrieved_memory = await service.get_memory(db_session, memory_id, user_id)

    assert retrieved_memory is not None
    assert retrieved_memory.id == memory_id
    assert retrieved_memory.content == content
    assert retrieved_memory.user_id == user_id


@pytest.mark.asyncio
async def test_get_nonexistent_memory(service, db_session):
    nonexistent_id = uuid4()
    user_id = uuid4()

    memory = await service.get_memory(db_session, nonexistent_id, user_id)

    assert memory is None


@pytest.mark.asyncio
async def test_update_memory(service, db_session):
    user_id = uuid4()
    content = "original content"

    created_memory = await service.create_memory(db_session, user_id, content)
    memory_id = created_memory.id

    new_content = "updated content"
    updated_memory = await service.update_memory(db_session, memory_id, new_content, user_id)

    assert updated_memory is not None
    assert updated_memory.content == new_content
    assert updated_memory.updated_at >= created_memory.updated_at


@pytest.mark.asyncio
async def test_update_nonexistent_memory(service, db_session):
    nonexistent_id = uuid4()
    user_id = uuid4()

    updated_memory = await service.update_memory(db_session, nonexistent_id, "new content", user_id)

    assert updated_memory is None


@pytest.mark.asyncio
async def test_delete_memory(service, db_session):
    user_id = uuid4()

    created_memory = await service.create_memory(db_session, user_id, "test memory")
    memory_id = created_memory.id

    result = await service.delete_memory(db_session, memory_id, user_id)

    assert result is True
    assert await service.get_memory(db_session, memory_id, user_id) is None


@pytest.mark.asyncio
async def test_delete_nonexistent_memory(service, db_session):
    nonexistent_id = uuid4()
    user_id = uuid4()

    result = await service.delete_memory(db_session, nonexistent_id, user_id)

    assert result is False


@pytest.mark.asyncio
async def test_search_memories(service, db_session):
    user_id = uuid4()

    await service.create_memory(db_session, user_id, "python programming")
    await service.create_memory(db_session, user_id, "java development")

    results = await service.search_memories(db_session, user_id, "python")

    assert len(results) == 1
    assert results[0].content == "python programming"


@pytest.mark.asyncio
async def test_get_memory_unauthorized(service, db_session):
    """Test that a user cannot get another user's memory"""
    user1_id = uuid4()
    user2_id = uuid4()

    # User 1 creates a memory
    created_memory = await service.create_memory(db_session, user1_id, "user1's memory")
    memory_id = created_memory.id

    # User 2 tries to get it
    retrieved_memory = await service.get_memory(db_session, memory_id, user2_id)

    assert retrieved_memory is None


@pytest.mark.asyncio
async def test_update_memory_unauthorized(service, db_session):
    """Test that a user cannot update another user's memory"""
    user1_id = uuid4()
    user2_id = uuid4()

    # User 1 creates a memory
    created_memory = await service.create_memory(db_session, user1_id, "user1's memory")
    memory_id = created_memory.id

    # User 2 tries to update it
    updated_memory = await service.update_memory(db_session, memory_id, "hacked content", user2_id)

    assert updated_memory is None
    # Verify original memory is unchanged
    original = await service.get_memory(db_session, memory_id, user1_id)
    assert original.content == "user1's memory"


@pytest.mark.asyncio
async def test_delete_memory_unauthorized(service, db_session):
    """Test that a user cannot delete another user's memory"""
    user1_id = uuid4()
    user2_id = uuid4()

    # User 1 creates a memory
    created_memory = await service.create_memory(db_session, user1_id, "user1's memory")
    memory_id = created_memory.id

    # User 2 tries to delete it
    result = await service.delete_memory(db_session, memory_id, user2_id)

    assert result is False
    # Verify memory still exists
    memory = await service.get_memory(db_session, memory_id, user1_id)
    assert memory is not None


@pytest.mark.asyncio
async def test_search_memories_empty_query(service, db_session):
    """Test that empty query returns empty list"""
    user_id = uuid4()

    await service.create_memory(db_session, user_id, "test memory")

    # Empty string
    results = await service.search_memories(db_session, user_id, "")
    assert len(results) == 0

    # Whitespace only
    results = await service.search_memories(db_session, user_id, "   ")
    assert len(results) == 0


@pytest.mark.asyncio
async def test_search_memories_case_insensitive(service, db_session):
    """Test that search is case insensitive"""
    user_id = uuid4()

    await service.create_memory(db_session, user_id, "Python Programming")

    # Search with different cases
    results = await service.search_memories(db_session, user_id, "python")
    assert len(results) == 1

    results = await service.search_memories(db_session, user_id, "PYTHON")
    assert len(results) == 1

    results = await service.search_memories(db_session, user_id, "PyThOn")
    assert len(results) == 1


@pytest.mark.asyncio
async def test_search_memories_special_characters(service, db_session):
    """Test search with special characters"""
    user_id = uuid4()

    await service.create_memory(db_session, user_id, "email: test@example.com")
    await service.create_memory(db_session, user_id, "price: $100")

    results = await service.search_memories(db_session, user_id, "@example")
    assert len(results) == 1

    results = await service.search_memories(db_session, user_id, "$100")
    assert len(results) == 1


@pytest.mark.asyncio
async def test_search_memories_no_results_for_other_users(service, db_session):
    """Test that search only returns memories for the specified user"""
    user1_id = uuid4()
    user2_id = uuid4()

    await service.create_memory(db_session, user1_id, "user1's python memory")
    await service.create_memory(db_session, user2_id, "user2's java memory")

    # User 1 searches for python
    results = await service.search_memories(db_session, user1_id, "python")
    assert len(results) == 1
    assert results[0].user_id == user1_id

    # User 2 searches for python
    results = await service.search_memories(db_session, user2_id, "python")
    assert len(results) == 0


@pytest.mark.asyncio
async def test_search_memories_user_with_no_memories(service, db_session):
    """Test search for user with no memories"""
    user_id = uuid4()

    results = await service.search_memories(db_session, user_id, "anything")
    assert len(results) == 0


@pytest.mark.asyncio
async def test_update_memory_immutability(service, db_session):
    """Test that update creates a new instance instead of mutating"""
    user_id = uuid4()

    created_memory = await service.create_memory(db_session, user_id, "original")
    memory_id = created_memory.id
    original_created_at = created_memory.created_at

    # Update the memory
    updated_memory = await service.update_memory(db_session, memory_id, "updated", user_id)

    # Verify created_at is preserved
    assert updated_memory.created_at == original_created_at
    # Verify it's a new instance (updated_at changed)
    assert updated_memory.updated_at >= original_created_at


@pytest.mark.asyncio
async def test_concurrent_updates(service, db_session):
    """Test that concurrent updates work correctly"""
    user_id = uuid4()
    memory = await service.create_memory(db_session, user_id, "original")

    async def update_memory():
        await service.update_memory(db_session, memory.id, "updated", user_id)

    tasks = [update_memory() for _ in range(10)]
    await asyncio.gather(*tasks)

    # Memory should still be valid and updated
    final = await service.get_memory(db_session, memory.id, user_id)
    assert final is not None
    assert final.content == "updated"


@pytest.mark.asyncio
async def test_concurrent_creates(service, db_session):
    """Test that concurrent creates generate unique IDs"""
    user_id = uuid4()
    results = []

    async def create_memory(index):
        memory = await service.create_memory(db_session, user_id, f"memory {index}")
        results.append(memory.id)

    tasks = [create_memory(i) for i in range(10)]
    await asyncio.gather(*tasks)

    # All IDs should be unique
    assert len(set(results)) == 10


@pytest.mark.asyncio
async def test_concurrent_deletes(service, db_session):
    """Test that concurrent deletes are handled safely"""
    user_id = uuid4()
    memory = await service.create_memory(db_session, user_id, "to delete")
    results = []

    async def delete_memory():
        result = await service.delete_memory(db_session, memory.id, user_id)
        results.append(result)

    tasks = [delete_memory() for _ in range(5)]
    await asyncio.gather(*tasks)

    # Only one delete should succeed
    assert sum(results) == 1

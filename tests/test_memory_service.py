import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_home(client):
    resp = await client.get("/")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_memory(client):
    data = {"content": "test memory"}
    user = str(uuid4())

    resp = await client.post("/memories", json=data, headers={"user-id": user})

    assert resp.status_code == 200
    assert resp.json()["content"] == "test memory"


@pytest.mark.asyncio
async def test_get_memory(client):
    user = str(uuid4())

    # Create memory
    resp = await client.post(
        "/memories", json={"content": "hello"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Get memory
    resp = await client.get(f"/memories/{memory_id}")
    assert resp.status_code == 200
    assert resp.json()["content"] == "hello"


@pytest.mark.asyncio
async def test_memory_not_found(client):
    resp = await client.get(f"/memories/{uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_search_memories(client):
    user = str(uuid4())

    # Create multiple memories
    await client.post(
        "/memories", json={"content": "I love pizza"}, headers={"user-id": user}
    )
    await client.post(
        "/memories", json={"content": "I enjoy pasta"}, headers={"user-id": user}
    )
    await client.post(
        "/memories", json={"content": "The weather is nice"}, headers={"user-id": user}
    )

    # Search for memories containing "pizza"
    resp = await client.post(
        "/memories/search", json={"query": "pizza"}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert any("pizza" in memory["content"].lower() for memory in results)


@pytest.mark.asyncio
async def test_search_memories_no_results(client):
    user = str(uuid4())

    # Create a memory
    await client.post(
        "/memories", json={"content": "hello world"}, headers={"user-id": user}
    )

    # Search for something that doesn't exist
    resp = await client.post(
        "/memories/search", json={"query": "nonexistent"}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 0


@pytest.mark.asyncio
async def test_delete_memory(client):
    user = str(uuid4())

    # Create memory
    resp = await client.post(
        "/memories", json={"content": "to be deleted"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Delete memory
    resp = await client.delete(f"/memories/{memory_id}", headers={"user-id": user})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Memory deleted successfully"
    assert resp.json()["id"] == memory_id

    # Verify memory is deleted
    resp = await client.get(f"/memories/{memory_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_memory_not_found(client):
    user = str(uuid4())
    resp = await client.delete(f"/memories/{uuid4()}", headers={"user-id": user})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_memory(client):
    """Test updating a memory"""
    user = str(uuid4())

    # Create memory
    resp = await client.post(
        "/memories", json={"content": "original content"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Update memory
    resp = await client.put(
        f"/memories/{memory_id}",
        json={"content": "updated content"},
        headers={"user-id": user}
    )
    assert resp.status_code == 200
    assert resp.json()["content"] == "updated content"
    assert resp.json()["id"] == memory_id


@pytest.mark.asyncio
async def test_update_memory_not_found(client):
    """Test updating a non-existent memory"""
    user = str(uuid4())

    resp = await client.put(
        f"/memories/{uuid4()}",
        json={"content": "new content"},
        headers={"user-id": user}
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_memory_unauthorized(client):
    """Test that a user cannot update another user's memory"""
    user1 = str(uuid4())
    user2 = str(uuid4())

    # User 1 creates a memory
    resp = await client.post(
        "/memories", json={"content": "user1's memory"}, headers={"user-id": user1}
    )
    memory_id = resp.json()["id"]

    # User 2 tries to update it
    resp = await client.put(
        f"/memories/{memory_id}",
        json={"content": "hacked content"},
        headers={"user-id": user2}
    )
    assert resp.status_code == 404

    # Verify original content is unchanged
    resp = await client.get(f"/memories/{memory_id}")
    assert resp.status_code == 200
    assert resp.json()["content"] == "user1's memory"


@pytest.mark.asyncio
async def test_delete_memory_unauthorized(client):
    """Test that a user cannot delete another user's memory"""
    user1 = str(uuid4())
    user2 = str(uuid4())

    # User 1 creates a memory
    resp = await client.post(
        "/memories", json={"content": "user1's memory"}, headers={"user-id": user1}
    )
    memory_id = resp.json()["id"]

    # User 2 tries to delete it
    resp = await client.delete(f"/memories/{memory_id}", headers={"user-id": user2})
    assert resp.status_code == 404

    # Verify memory still exists
    resp = await client.get(f"/memories/{memory_id}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_search_memories_empty_query(client):
    """Test that empty query returns empty list"""
    user = str(uuid4())

    # Create a memory
    await client.post(
        "/memories", json={"content": "test memory"}, headers={"user-id": user}
    )

    # Search with empty query
    resp = await client.post(
        "/memories/search", json={"query": ""}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_search_memories_whitespace_query(client):
    """Test that whitespace-only query returns empty list"""
    user = str(uuid4())

    # Create a memory
    await client.post(
        "/memories", json={"content": "test memory"}, headers={"user-id": user}
    )

    # Search with whitespace query
    resp = await client.post(
        "/memories/search", json={"query": "   "}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_search_memories_case_insensitive(client):
    """Test that search is case insensitive"""
    user = str(uuid4())

    # Create memory
    await client.post(
        "/memories", json={"content": "Python Programming"}, headers={"user-id": user}
    )

    # Search with different cases
    for query in ["python", "PYTHON", "PyThOn"]:
        resp = await client.post(
            "/memories/search", json={"query": query}, headers={"user-id": user}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_search_memories_special_characters(client):
    """Test search with special characters"""
    user = str(uuid4())

    # Create memories with special characters
    await client.post(
        "/memories", json={"content": "email: test@example.com"}, headers={"user-id": user}
    )
    await client.post(
        "/memories", json={"content": "price: $100"}, headers={"user-id": user}
    )

    # Search for email
    resp = await client.post(
        "/memories/search", json={"query": "@example"}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Search for price
    resp = await client.post(
        "/memories/search", json={"query": "$100"}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_search_memories_isolation(client):
    """Test that users can only search their own memories"""
    user1 = str(uuid4())
    user2 = str(uuid4())

    # User 1 creates a memory
    await client.post(
        "/memories", json={"content": "user1's python memory"}, headers={"user-id": user1}
    )

    # User 2 creates a memory
    await client.post(
        "/memories", json={"content": "user2's java memory"}, headers={"user-id": user2}
    )

    # User 1 searches for python
    resp = await client.post(
        "/memories/search", json={"query": "python"}, headers={"user-id": user1}
    )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["user_id"] == user1

    # User 2 searches for python
    resp = await client.post(
        "/memories/search", json={"query": "python"}, headers={"user-id": user2}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_delete_memory_return_type(client):
    """Test that delete returns UUID not string"""
    user = str(uuid4())

    # Create memory
    resp = await client.post(
        "/memories", json={"content": "to be deleted"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Delete memory
    resp = await client.delete(f"/memories/{memory_id}", headers={"user-id": user})
    assert resp.status_code == 200
    # Verify the ID is returned as UUID format (not converted to string)
    assert resp.json()["id"] == memory_id

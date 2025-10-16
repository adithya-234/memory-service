import pytest
import asyncio
from uuid import uuid4


async def test_home(client):
    resp = await client.get("/")
    assert resp.status_code == 200


async def test_create_memory(client):
    data = {"content": "test memory"}
    user = str(uuid4())

    resp = await client.post("/memories", json=data, headers={"user-id": user})

    assert resp.status_code == 200
    assert resp.json()["content"] == "test memory"


async def test_get_memory(client):
    user = str(uuid4())

    # Create memory
    resp = await client.post(
        "/memories", json={"content": "hello"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Get memory
    resp = await client.get(f"/memories/{memory_id}", headers={"user-id": user})
    assert resp.status_code == 200
    assert resp.json()["content"] == "hello"


async def test_memory_not_found(client):
    user = str(uuid4())
    resp = await client.get(f"/memories/{uuid4()}", headers={"user-id": user})
    assert resp.status_code == 404


async def test_search_memories(client):
    user = str(uuid4())

    # Create multiple memories
    resp1 = await client.post(
        "/memories", json={"content": "I love pizza"}, headers={"user-id": user}
    )
    memory_id = resp1.json()["id"]

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


async def test_search_memories_no_results(client):
    user = str(uuid4())

    # Create a memory
    resp1 = await client.post(
        "/memories", json={"content": "hello world"}, headers={"user-id": user}
    )
    memory_id = resp1.json()["id"]

    # Search for something that doesn't exist
    resp = await client.post(
        "/memories/search", json={"query": "nonexistent"}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 0


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
    resp = await client.get(f"/memories/{memory_id}", headers={"user-id": user})
    assert resp.status_code == 404


async def test_delete_memory_not_found(client):
    user = str(uuid4())
    resp = await client.delete(f"/memories/{uuid4()}", headers={"user-id": user})
    assert resp.status_code == 404


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


async def test_update_memory_not_found(client):
    """Test updating a non-existent memory"""
    user = str(uuid4())

    resp = await client.put(
        f"/memories/{uuid4()}",
        json={"content": "new content"},
        headers={"user-id": user}
    )
    assert resp.status_code == 404


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
    resp = await client.get(f"/memories/{memory_id}", headers={"user-id": user1})
    assert resp.status_code == 200
    assert resp.json()["content"] == "user1's memory"


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
    resp = await client.get(f"/memories/{memory_id}", headers={"user-id": user1})
    assert resp.status_code == 200


async def test_search_memories_empty_query(client):
    """Test that empty query returns empty list"""
    user = str(uuid4())

    # Create a memory
    resp1 = await client.post(
        "/memories", json={"content": "test memory"}, headers={"user-id": user}
    )
    memory_id = resp1.json()["id"]

    # Search with empty query
    resp = await client.post(
        "/memories/search", json={"query": ""}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0


async def test_search_memories_whitespace_query(client):
    """Test that whitespace-only query returns empty list"""
    user = str(uuid4())

    # Create a memory
    resp1 = await client.post(
        "/memories", json={"content": "test memory"}, headers={"user-id": user}
    )
    memory_id = resp1.json()["id"]

    # Search with whitespace query
    resp = await client.post(
        "/memories/search", json={"query": "   "}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0


async def test_search_memories_case_insensitive(client):
    """Test that search is case insensitive"""
    user = str(uuid4())

    # Create memory
    resp1 = await client.post(
        "/memories", json={"content": "Python Programming"}, headers={"user-id": user}
    )
    memory_id = resp1.json()["id"]

    # Search with different cases
    for query in ["python", "PYTHON", "PyThOn"]:
        resp = await client.post(
            "/memories/search", json={"query": query}, headers={"user-id": user}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1


async def test_search_memories_special_characters(client):
    """Test search with special characters"""
    user = str(uuid4())

    # Create memories with special characters
    resp1 = await client.post(
        "/memories", json={"content": "email: test@example.com"}, headers={"user-id": user}
    )
    memory_id = resp1.json()["id"]

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


async def test_search_memories_isolation(client):
    """Test that users can only search their own memories"""
    user1 = str(uuid4())
    user2 = str(uuid4())

    # User 1 creates a memory
    resp1 = await client.post(
        "/memories", json={"content": "user1's python memory"}, headers={"user-id": user1}
    )
    memory_id_user1 = resp1.json()["id"]

    # User 2 creates a memory
    resp2 = await client.post(
        "/memories", json={"content": "user2's java memory"}, headers={"user-id": user2}
    )
    memory_id_user2 = resp2.json()["id"]

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


async def test_concurrent_create_memories(client):
    """Test concurrent creation of memories by the same user"""
    user = str(uuid4())
    num_concurrent = 5

    # Create multiple memories concurrently
    async def create_memory(index):
        return await client.post(
            "/memories",
            json={"content": f"concurrent memory {index}"},
            headers={"user-id": user}
        )

    tasks = [create_memory(i) for i in range(num_concurrent)]
    responses = await asyncio.gather(*tasks)

    # Verify all creations succeeded
    assert all(resp.status_code == 200 for resp in responses)

    # Verify all memories have unique IDs
    memory_ids = [resp.json()["id"] for resp in responses]
    assert len(memory_ids) == len(set(memory_ids))


async def test_concurrent_read_same_memory(client):
    """Test concurrent reads of the same memory"""
    user = str(uuid4())

    # Create a memory
    resp = await client.post(
        "/memories", json={"content": "test concurrent reads"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Read the same memory concurrently
    async def read_memory():
        return await client.get(f"/memories/{memory_id}", headers={"user-id": user})

    tasks = [read_memory() for _ in range(10)]
    responses = await asyncio.gather(*tasks)

    # Verify all reads succeeded
    assert all(resp.status_code == 200 for resp in responses)
    assert all(resp.json()["content"] == "test concurrent reads" for resp in responses)


async def test_concurrent_update_same_memory(client):
    """Test concurrent updates to the same memory"""
    user = str(uuid4())

    # Create a memory
    resp = await client.post(
        "/memories", json={"content": "original"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Update the same memory concurrently
    async def update_memory(index):
        return await client.put(
            f"/memories/{memory_id}",
            json={"content": f"updated {index}"},
            headers={"user-id": user}
        )

    tasks = [update_memory(i) for i in range(3)]
    responses = await asyncio.gather(*tasks)

    # Verify all updates succeeded
    assert all(resp.status_code == 200 for resp in responses)

    # Verify the final state is one of the updated values
    resp = await client.get(f"/memories/{memory_id}", headers={"user-id": user})
    assert resp.status_code == 200
    assert "updated" in resp.json()["content"]


async def test_concurrent_delete_same_memory(client):
    """Test concurrent deletes of the same memory"""
    user = str(uuid4())

    # Create a memory
    resp = await client.post(
        "/memories", json={"content": "to be deleted"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Delete the same memory concurrently
    async def delete_memory():
        return await client.delete(f"/memories/{memory_id}", headers={"user-id": user})

    tasks = [delete_memory() for _ in range(3)]
    responses = await asyncio.gather(*tasks)

    # At least one delete should succeed (200), others might return 404
    status_codes = [resp.status_code for resp in responses]
    assert 200 in status_codes
    assert all(code in [200, 404] for code in status_codes)

    # Verify memory is deleted
    resp = await client.get(f"/memories/{memory_id}", headers={"user-id": user})
    assert resp.status_code == 404


async def test_concurrent_search_by_multiple_users(client):
    """Test concurrent searches by different users"""
    num_users = 5
    users = [str(uuid4()) for _ in range(num_users)]

    # Each user creates their own memories
    for i, user in enumerate(users):
        await client.post(
            "/memories",
            json={"content": f"user {i} memory with keyword"},
            headers={"user-id": user}
        )
        await client.post(
            "/memories",
            json={"content": f"user {i} other memory"},
            headers={"user-id": user}
        )

    # All users search concurrently
    async def search_memories(user):
        return await client.post(
            "/memories/search",
            json={"query": "keyword"},
            headers={"user-id": user}
        )

    tasks = [search_memories(user) for user in users]
    responses = await asyncio.gather(*tasks)

    # Verify all searches succeeded and returned exactly 1 result per user
    assert all(resp.status_code == 200 for resp in responses)
    assert all(len(resp.json()) == 1 for resp in responses)


async def test_concurrent_mixed_operations(client):
    """Test mixed concurrent operations (create, read, update, search)"""
    user = str(uuid4())

    # Create initial memory
    resp = await client.post(
        "/memories", json={"content": "initial memory"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Define different operations
    async def create_op():
        return await client.post(
            "/memories",
            json={"content": "concurrent create"},
            headers={"user-id": user}
        )

    async def read_op():
        return await client.get(f"/memories/{memory_id}", headers={"user-id": user})

    async def search_op():
        return await client.post(
            "/memories/search",
            json={"query": "memory"},
            headers={"user-id": user}
        )

    # Execute mixed operations concurrently
    tasks = [
        create_op(), create_op(),
        read_op(), read_op(),
        search_op(), search_op()
    ]
    responses = await asyncio.gather(*tasks)

    # Verify all operations completed successfully
    assert all(resp.status_code == 200 for resp in responses)


async def test_concurrent_create_by_different_users(client):
    """Test concurrent creation by different users"""
    num_users = 5
    users = [str(uuid4()) for _ in range(num_users)]

    # Each user creates a memory concurrently
    async def create_for_user(user_id, index):
        return await client.post(
            "/memories",
            json={"content": f"user {index} memory"},
            headers={"user-id": user_id}
        )

    tasks = [create_for_user(users[i], i) for i in range(num_users)]
    responses = await asyncio.gather(*tasks)

    # Verify all creations succeeded
    assert all(resp.status_code == 200 for resp in responses)

    # Verify each user can access their own memory
    for i, user in enumerate(users):
        memory_id = responses[i].json()["id"]
        resp = await client.get(f"/memories/{memory_id}", headers={"user-id": user})
        assert resp.status_code == 200
        assert resp.json()["user_id"] == user

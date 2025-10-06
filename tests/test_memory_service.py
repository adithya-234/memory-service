from uuid import uuid4


def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_create_memory(client):
    data = {"content": "test memory"}
    user = str(uuid4())

    resp = client.post("/memories", json=data, headers={"user-id": user})

    assert resp.status_code == 200
    assert resp.json()["content"] == "test memory"


def test_get_memory(client):
    user = str(uuid4())

    # Create memory
    resp = client.post(
        "/memories", json={"content": "hello"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Get memory
    resp = client.get(f"/memories/{memory_id}")
    assert resp.status_code == 200
    assert resp.json()["content"] == "hello"


def test_memory_not_found(client):
    resp = client.get(f"/memories/{uuid4()}")
    assert resp.status_code == 404


def test_search_memories(client):
    user = str(uuid4())

    # Create multiple memories
    client.post(
        "/memories", json={"content": "I love pizza"}, headers={"user-id": user}
    )
    client.post(
        "/memories", json={"content": "I enjoy pasta"}, headers={"user-id": user}
    )
    client.post(
        "/memories", json={"content": "The weather is nice"}, headers={"user-id": user}
    )

    # Search for memories containing "pizza"
    resp = client.post(
        "/memories/search", json={"query": "pizza"}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) > 0
    assert any("pizza" in memory["content"].lower() for memory in results)


def test_search_memories_no_results(client):
    user = str(uuid4())

    # Create a memory
    client.post(
        "/memories", json={"content": "hello world"}, headers={"user-id": user}
    )

    # Search for something that doesn't exist
    resp = client.post(
        "/memories/search", json={"query": "nonexistent"}, headers={"user-id": user}
    )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 0


def test_delete_memory(client):
    user = str(uuid4())

    # Create memory
    resp = client.post(
        "/memories", json={"content": "to be deleted"}, headers={"user-id": user}
    )
    memory_id = resp.json()["id"]

    # Delete memory
    resp = client.delete(f"/memories/{memory_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Memory deleted successfully"
    assert resp.json()["id"] == memory_id

    # Verify memory is deleted
    resp = client.get(f"/memories/{memory_id}")
    assert resp.status_code == 404


def test_delete_memory_not_found(client):
    resp = client.delete(f"/memories/{uuid4()}")
    assert resp.status_code == 404

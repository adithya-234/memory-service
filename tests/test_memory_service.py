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

    
    resp = client.post("/memories", json={"content": "hello"}, headers={"user-id": user})
    memory_id = resp.json()["id"]

    
    resp = client.get(f"/memories/{memory_id}")
    assert resp.status_code == 200
    assert resp.json()["content"] == "hello"


def test_memory_not_found(client):
    resp = client.get(f"/memories/{uuid4()}")
    assert resp.status_code == 404
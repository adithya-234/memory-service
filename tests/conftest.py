import pytest
from fastapi.testclient import TestClient
from app.main import app, memory_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_memories_store():
    yield
    memory_service.clear_memories()

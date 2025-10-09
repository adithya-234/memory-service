import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.main import app, memory_service
from app.database import engine, Base, get_db


# Set test database environment variables
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DB'] = 'memory_db'
os.environ['POSTGRES_USER'] = 'postgres'
os.environ['POSTGRES_PASSWORD'] = 'postgres'

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables."""
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():
    """Provide a database session for tests."""
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Provide a test client."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_data(db_session):
    """Clear data after each test."""
    yield
    memory_service.clear_memories(db_session)

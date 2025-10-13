import pytest
import os
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app, memory_service
from app.database import Base, get_db


# Set test database environment variables
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DB'] = 'memory_db'
os.environ['POSTGRES_USER'] = 'postgres'
os.environ['POSTGRES_PASSWORD'] = 'postgres'

# Create test async engine
TEST_DATABASE_URL = f"postgresql+asyncpg://postgres:postgres@localhost:5432/memory_db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create and cleanup database tables for test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup: drop all tables after test session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db_session():
    """
    Provide an async database session for tests with transaction rollback.
    Each test gets a clean transaction that rolls back after the test.
    """
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Provide an async test client."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def clear_data(db_session):
    """Clear data after each test."""
    yield
    await memory_service.clear_memories(db_session)

"""Database initialization script."""
import asyncio
import time
import sys
from sqlalchemy import text
from database import init_db, engine


async def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready."""
    for i in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("Database connection established!")
            return True
        except Exception as e:
            print(f"Waiting for database... (attempt {i + 1}/{max_retries})")
            print(f"Error: {e}")
            await asyncio.sleep(delay)
    return False


async def main():
    """Initialize the database."""
    print("Starting database initialization...")

    if not await wait_for_db():
        print("Failed to connect to database after multiple retries.")
        sys.exit(1)

    try:
        print("Creating tables and indexes...")
        await init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

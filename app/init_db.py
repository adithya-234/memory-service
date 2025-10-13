"""Database initialization script."""
import asyncio
import sys
import os
from sqlalchemy import text
from app.database import init_db, engine

# Configuration constants
MAX_DB_RETRIES = int(os.getenv('MAX_DB_RETRIES', '30'))
DB_RETRY_DELAY = int(os.getenv('DB_RETRY_DELAY', '2'))


async def wait_for_db(max_retries=MAX_DB_RETRIES, delay=DB_RETRY_DELAY):
    """
    Wait for database to be ready by attempting connections.

    Args:
        max_retries: Maximum number of connection attempts (default from env: MAX_DB_RETRIES)
        delay: Delay in seconds between retry attempts (default from env: DB_RETRY_DELAY)

    Returns:
        bool: True if database connection successful, False otherwise
    """
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

"""Database initialization script."""
import time
import sys
from database import db


def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready."""
    for i in range(max_retries):
        try:
            db.connect()
            print("Database connection established!")
            return True
        except Exception as e:
            print(f"Waiting for database... (attempt {i + 1}/{max_retries})")
            print(f"Error: {e}")
            time.sleep(delay)
    return False


def main():
    """Initialize the database."""
    print("Starting database initialization...")

    if not wait_for_db():
        print("Failed to connect to database after multiple retries.")
        sys.exit(1)

    try:
        print("Creating tables and indexes...")
        db.init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

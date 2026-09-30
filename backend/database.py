import os
from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file (either in backend or root)
env_path = Path(__file__).resolve().parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DB_NAME = os.getenv("DATABASE_NAME", "shelflife_db")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "PostgreSQL")


def get_connection():
    """
    Create and return a raw PostgreSQL database connection.
    Maintains backward compatibility with legacy endpoints.
    """
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=5
        )
        return connection

    except OperationalError as error:
        print("========================================")
        print("DATABASE CONNECTION ERROR")
        print("========================================")
        print(error)
        print()
        print("Please check:")
        print(f"1. PostgreSQL service is running on {DB_HOST}:{DB_PORT}")
        print(f"2. Database '{DB_NAME}' exists")
        print(f"3. PostgreSQL username '{DB_USER}' is correct")
        print("4. PostgreSQL password is correct")
        print("========================================")
        raise


@contextmanager
def get_db_cursor(commit: bool = False, dict_cursor: bool = False):
    """
    Context manager for database operations that ensures connections
    and cursors are properly opened, committed (if needed), and closed.
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = connection.cursor(cursor_factory=cursor_factory)
        yield cursor
        if commit:
            connection.commit()
    except Exception as error:
        if connection and commit:
            connection.rollback()
        raise error
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
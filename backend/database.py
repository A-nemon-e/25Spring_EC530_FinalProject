import sqlite3
import os
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "mydatabase.db")
# DATABASE_PATH = "mydatabase.db"  # Path to the generated SQLite database file

@contextmanager
def get_db():
    """
    Get a SQLite database connection with foreign key support enabled.

    Usage:
        with get_db() as (conn, cursor):
            cursor.execute(...)
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column-name-based access for query results
    conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key constraints
    cursor = conn.cursor()

    try:
        yield conn, cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

'''
Example:

from database import get_db

with get_db() as (conn, cursor):
    cursor.execute("SELECT * FROM tags")
    rows = cursor.fetchall()
    for row in rows:
        print(row["name"])
'''

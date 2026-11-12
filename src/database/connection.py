import sqlite3
import os
from contextlib import contextmanager

DEFAULT_DB_PATH = "data/storage.sqlite3"

@contextmanager
def get_db(path=DEFAULT_DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

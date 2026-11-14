from pathlib import Path
import sqlite3
import os
from contextlib import contextmanager

from log import log_ok

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / ".turisty" / "storage.sqlite3"
DEFAULT_SCHEMA_PATH = BASE_DIR  / "schema.sql"

@contextmanager
def get_db(path=DEFAULT_DB_PATH):
    """safely gets a database connection"""
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

def init_schema():
    with get_db() as conn, open(DEFAULT_SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())

    log_ok("Schema synced")

import sqlite3
import os
from contextlib import contextmanager

from log import log_ok

DEFAULT_DB_PATH = ".turisty/storage.sqlite3"

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

def init_schema(conn):
    schema_path = "database/schema.sql"

    with get_db() as conn, open(schema_path, encoding="utf-8") as f:
        conn.executescript(f.read())

    log_ok("Synced database")

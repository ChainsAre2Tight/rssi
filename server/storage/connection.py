import sqlite3
from typing import Optional

import config


def _configure(conn: sqlite3.Connection) -> None:
    # conn.execute("PRAGMA foreign_keys = ON") # disabled for testing purposes
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 5000")

    conn.row_factory = sqlite3.Row

class Session:

    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(config.DB_FILE)
        _configure(self.conn)
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        if self.conn is None:
            return

        try:
            if exc is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()
            self.conn = None

class Transaction:

    def __init__(self, conn: sqlite3.Connection, immediate: bool = False):
        self.conn = conn
        self.immediate = immediate

    def __enter__(self):

        if self.immediate:
            self.conn.execute("BEGIN IMMEDIATE")
        else:
            self.conn.execute("BEGIN")

        return self.conn

    def __exit__(self, exc_type, exc, tb):

        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

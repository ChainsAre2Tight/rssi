import sqlite3
from typing import Dict, Any, List

import config

class Connect:
    _conn: sqlite3.Connection | None

    def __init__(self):
        self._conn = None

    def __enter__(self) -> sqlite3.Connection:
        self._conn = sqlite3.connect(config.DB_FILE)
        return self._conn

    def __exit__(self, *args: List[Any], **kwargs: Dict[Any, Any]) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

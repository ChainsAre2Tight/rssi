import json

import sqlite3

from storage.connection import Session


def insert_measurement(room_id: int) -> int:
    with Session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO measurements (room_id)
            VALUES (?)
            RETURNING id
        """, (room_id,))
        id = cursor.fetchone()[0]
        conn.commit()
    
    return id

def get_latest_measurement_id() -> int:
    with Session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM measurements ORDER BY 1 DESC LIMIT 1
        """)
        id = cursor.fetchone()[0]
    return id

def load_measurement_whitelist(
    conn: sqlite3.Connection,
    measurement_id: int,
) -> dict:

    cur = conn.execute(
        """
        SELECT whitelist_json
        FROM measurements
        WHERE id = ?
        """,
        (measurement_id,),
    )

    row = cur.fetchone()

    if row is None:
        return {}

    whitelist_json = row[0]

    if whitelist_json is None:
        return {}

    return json.loads(whitelist_json)
        
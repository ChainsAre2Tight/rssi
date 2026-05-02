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

def store_measurement_whitelist(
    conn: sqlite3.Connection,
    measurement_id: int,
    whitelist: dict
) -> None:

    whitelist_json = json.dumps(whitelist)

    conn.execute(
        """
        UPDATE measurements
        SET whitelist_json = ?
        WHERE id = ?
        """,
        (whitelist_json, measurement_id),
    )

def list_measurements(
    conn: sqlite3.Connection,
) -> list[dict]:

    cur = conn.cursor()

    rows = cur.execute("""
        SELECT id, name, description, room_id
        FROM measurements
        ORDER BY created DESC
    """).fetchall()

    return [
        {
            "measurement_id": row[0],
            "name": row[1],
            "description": row[2],
            "room_id": row[3],
        }
        for row in rows
    ]

def update_measurement(
    conn: sqlite3.Connection,
    measurement_id: int,
    name: str | None = None,
    description: str | None = None,
) -> tuple[bool, str, dict | None]:

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, description FROM measurements WHERE id = ?",
        (measurement_id,)
    )
    row = cursor.fetchone()

    if row is None:
        return False, "not_found", None

    current_id, current_name, current_description = row

    updates = []
    params = []

    changed = False

    if name is not None and name != current_name:
        updates.append("name = ?")
        params.append(name)
        changed = True

    if description is not None and description != current_description:
        updates.append("description = ?")
        params.append(description)
        changed = True

    if changed:
        query = f"""
            UPDATE measurements
            SET {", ".join(updates)}
            WHERE id = ?
        """
        params.append(measurement_id)
        cursor.execute(query, params)
        conn.commit()

    # Always return final state
    cursor.execute(
        "SELECT id, name, description FROM measurements WHERE id = ?",
        (measurement_id,)
    )
    final_row = cursor.fetchone()

    measurement = {
        "measurement_id": final_row[0],
        "name": final_row[1],
        "description": final_row[2],
    }

    if not changed:
        return False, "no_changes", measurement

    return True, "updated", measurement

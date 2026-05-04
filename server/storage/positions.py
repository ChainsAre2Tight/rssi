import sqlite3
from storage.connection import Session

def get_device_position(measurement_id: int, device: str) -> tuple[float, float, float]:
    with Session() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT x, y, z
            FROM positions
            WHERE
                measurement_id = ?
                AND device = ?
        """, (measurement_id, device,))
        row = cur.fetchone()
        if row:
            return row[0], row[1], row[2]
        return 0, 0, 0

def update_device_description(
    conn: sqlite3.Connection,
    measurement_id: int,
    device: str,
    description: str,
) -> None:
    conn.execute("""
        UPDATE positions
        SET description = ?
        WHERE measurement_id = ?
            AND device = ?
    """, (
        description,
        measurement_id,
        device,
    ))

def update_device_position(
    conn: sqlite3.Connection,
    measurement_id: int,
    device: str,
    x: int,
    y: int,
    z: int,
) -> None:
    conn.execute("""
        UPDATE positions
        SET x = ?, y = ?, z = ?
        WHERE measurement_id = ?
            AND device = ?
    """, (
        x, y, z,
        measurement_id,
        device,
    ))

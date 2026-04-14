import sqlite3

from my_types import DEVICE


def get_all_devices(conn: sqlite3.Connection) -> list[DEVICE]:
    cur = conn.cursor()
    cur.execute("""
        SELECT name, description, mac
        FROM devices
    """)
    rows = cur.fetchall()
    return [
        {
            "name": row[0],
            "description": row[1],
            "mac": row[2],
            "gain": 0,  # not used, keep contract
        }
        for row in rows
    ]

def get_device_positions(
    conn: sqlite3.Connection,
    measurement_id: int,
) -> dict[str, tuple[float, float, float]]:
    cur = conn.cursor()
    cur.execute("""
        SELECT device, x, y, z
        FROM positions
        WHERE measurement_id = ?
    """, (measurement_id,))
    rows = cur.fetchall()

    return {
        row[0]: (row[1], row[2], row[3])
        for row in rows
    }

def load_sensors_for_measurement(
    conn: sqlite3.Connection,
    measurement_id: int,
) -> list[dict]:

    cur = conn.cursor()

    rows = cur.execute("""
        SELECT
            d.name,
            d.mac,
            d.description,
            p.x,
            p.y,
            p.z
        FROM positions p
        JOIN devices d ON d.name = p.device
        WHERE p.measurement_id = ?
        ORDER BY d.name
    """, (measurement_id,)).fetchall()

    return [
        {
            "name": row[0],
            "mac": row[1],
            "description": row[2],
            "x": row[3],
            "y": row[4],
            "z": row[5],
        }
        for row in rows
    ]

from storage.connection import Connect

def get_device_position(measurement_id: int, device: str) -> tuple[float, float, float]:
    with Connect() as conn:
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

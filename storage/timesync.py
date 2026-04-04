import sqlite3
from typing import List

import my_types

def insert_time_sync(conn: sqlite3.Connection, measurement_id: int, device: str, sync_event: my_types.TIME_SYNC):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO time_sync (
            measurement_id, device, boot_time_us, unix_time_us
        ) VALUES (?, ?, ?, ?)
    """,
        (
            measurement_id,
            device,
            sync_event.get("boot_time_us", 0),
            int(sync_event.get("boot_unix_time", 0) * 1_000_000),
        )
    )


def load_time_sync(
    conn: sqlite3.Connection,
    measurement_id: int,
) -> List[my_types.TimeSyncRow]:

    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT
            device,
            measurement_id,
            boot_time_us,
            unix_time_us
        FROM time_sync
        WHERE measurement_id = ?
        ORDER BY device, boot_time_us
        """,
        (measurement_id,),
    )

    return [
        my_types.TimeSyncRow(
            device=row["device"],
            measurement_id=row["measurement_id"],
            boot_time_us=row["boot_time_us"],
            unix_time_us=row["unix_time_us"],
        )
        for row in rows
    ]
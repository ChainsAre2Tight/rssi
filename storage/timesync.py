import sqlite3

import my_types

def insert_time_sync(conn: sqlite3.Connection, device: str, sync_event: my_types.TIME_SYNC):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO time_sync (
            device, boot_time_us, unix_time
        ) VALUES (?, ?, ?)
    """,
        (
            device,
            sync_event.get("boot_time_us", 0),
            sync_event.get("boot_unix_time", 0),
        )
    )
    conn.commit()
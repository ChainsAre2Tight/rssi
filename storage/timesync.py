from typing import List, Tuple

import storage
import my_types

def insert_time_sync(device: str, sync_event: my_types.TIME_SYNC):
    with storage.Connect() as conn:
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
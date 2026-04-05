import sqlite3
from typing import List

import my_types


def insert_events(
    conn: sqlite3.Connection,
    measurement_id: int,
    events: List[my_types.EventRow],
) -> List[int]:

    if not events:
        return []

    values = [
        (
            measurement_id,
            ev.src_mac,
            ev.seq,
            ev.type,
            ev.subtype,
            ev.dst_mac,
            ev.bssid,
            ev.ssid,
            ev.first_time_us,
            ev.last_time_us,
            ev.approx_time_us,
        )
        for ev in events
    ]

    placeholders = ",".join(["(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"] * len(values))

    flat_values = [v for row in values for v in row]

    sql = f"""
        INSERT INTO events (
            measurement_id,
            src_mac,
            seq,
            type,
            subtype,
            dst_mac,
            bssid,
            ssid,
            first_time_us,
            last_time_us,
            approx_unix_time_us
        )
        VALUES {placeholders}
        RETURNING id
    """

    cur = conn.cursor()
    rows = cur.execute(sql, flat_values)

    return [row[0] for row in rows]
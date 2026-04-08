from typing import List, Tuple, Iterable

import sqlite3

import my_types

def insert_events(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    events: List[my_types.EventRow],
) -> List[int]:

    if not events:
        return []

    values = [
        (
            measurement_id,
            window_id,
            ev.src_mac,
            ev.seq,
            ev.type,
            ev.subtype,
            ev.dst_mac,
            ev.bssid,
            ev.ssid,
            ev.role,
            ev.first_time_us,
            ev.last_time_us,
            ev.approx_time_us,
        )
        for ev in events
    ]

    placeholders = ",".join(["(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"] * len(values))

    flat_values = [v for row in values for v in row]

    sql = f"""
        INSERT INTO events (
            measurement_id,
            window_id,
            src_mac,
            seq,
            type,
            subtype,
            dst_mac,
            bssid,
            ssid,
            role,
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


def insert_event_packets(
    conn: sqlite3.Connection,
    event_ids: List[int],
    observations_per_event: List[List[int]],
) -> None:

    if not event_ids:
        return

    pairs = []

    for event_id, packet_ids in zip(event_ids, observations_per_event):
        for packet_id in packet_ids:
            pairs.append((event_id, packet_id))

    if not pairs:
        return

    placeholders = ",".join(["(?, ?)"] * len(pairs))

    flat_values = [v for pair in pairs for v in pair]

    sql = f"""
        INSERT INTO event_packets (
            event_id,
            packet_id
        )
        VALUES {placeholders}
    """

    cur = conn.cursor()
    cur.execute(sql, flat_values)


def load_window_events(
    conn: sqlite3.Connection,
    window_id: int,
) -> List[Tuple[int, str | None]]:
    """Returns list of (event_id, bssid)"""
    cur = conn.execute(
        """
        SELECT id, bssid
        FROM events
        WHERE window_id = ?
        """,
        (window_id,),
    )

    return cur.fetchall()

def update_event_observation_ids(
    conn: sqlite3.Connection,
    rows: Iterable[Tuple[int, int]],
) -> None:
    """
    rows = (observation_id, event_id)
    """

    conn.executemany(
        """
        UPDATE events
        SET observation_id = ?
        WHERE id = ?
        """,
        rows,
    )

from typing import List

import sqlite3

import my_types


def insert_csi_signals(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
    signals: List[my_types.CSISignal],
) -> None:

    rows = [
        (
            measurement_id,
            window_id,
            start_time_us,
            end_time_us,
            s.bssid,
            s.importance,
            s.metadata_json,
        )
        for s in signals
    ]

    conn.executemany(
        """
        INSERT INTO csi_signals (
            measurement_id,
            window_id,
            start_time_us,
            end_time_us,
            bssid,
            severity,
            metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

def load_csi_signals_for_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
) -> list[my_types.CSISignal]:

    cur = conn.cursor()

    rows = cur.execute("""
        SELECT
            bssid,
            severity,
            metadata_json
        FROM csi_signals
        WHERE window_id = ?
    """, (window_id,)).fetchall()

    return [
        my_types.CSISignal(
            measurement_id=measurement_id,
            window_id=window_id,
            bssid=row[0],
            importance=row[1],
            metadata_json=row[2],
        )
        for row in rows
    ]

def delete_csi_signals_for_measurement(
    conn: sqlite3.Connection,
    measurement_id: int,
) -> None:
    
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM csi_signals
        WHERE measurement_id = ?
    """, (measurement_id,))

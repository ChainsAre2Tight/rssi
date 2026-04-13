import sqlite3
from typing import List

import my_types


def insert_detection_signals(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
    signals: List[my_types.DetectionSignal],
) -> None:

    rows = [
        (
            measurement_id,
            window_id,
            start_time_us,
            end_time_us,
            s.observation_id,
            s.bssid,
            s.ssid,
            s.detector,
            s.signal,
            s.severity,
            s.metadata_json,
        )
        for s in signals
    ]

    conn.executemany(
        """
        INSERT INTO detection_signals (
            measurement_id,
            window_id,
            start_time_us,
            end_time_us,
            observation_id,
            bssid,
            ssid,
            detector,
            signal,
            severity,
            metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

def load_detection_signals_for_window(
    conn: sqlite3.Connection,
    window_id: int,
) -> list[my_types.DetectionSignal]:

    cur = conn.cursor()

    rows = cur.execute("""
        SELECT
            observation_id,
            bssid,
            ssid,
            detector,
            signal,
            severity,
            metadata_json
        FROM detection_signals
        WHERE window_id = ?
    """, (window_id,)).fetchall()

    return [
        my_types.DetectionSignal(
            observation_id=row[0],
            bssid=row[1],
            ssid=row[2],
            detector=row[3],
            signal=row[4],
            severity=row[5],
            metadata_json=row[6],
        )
        for row in rows
    ]

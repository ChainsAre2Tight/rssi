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
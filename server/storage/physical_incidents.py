import sqlite3

import my_types

def load_physical_incident_groups(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
) -> list[my_types.PhysicalIncidentGroup]:

    cursor = conn.execute(
        """
        SELECT
            bssid,
            MIN(start_time_us) AS first_seen_us,
            MAX(end_time_us) AS last_seen_us,
            COUNT(*) AS signal_count
        FROM csi_signals
        WHERE
            measurement_id = ?
            AND start_time_us >= ?
            AND end_time_us <= ?
        GROUP BY bssid
        """,
        (measurement_id, start_time_us, end_time_us),
    )

    rows = cursor.fetchall()

    return [
        my_types.PhysicalIncidentGroup(
            bssid=row[0],
            first_seen_us=row[1],
            last_seen_us=row[2],
            signal_count=row[3],
        )
        for row in rows
    ]

def load_physical_signals_for_bssid(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
    bssid: str,
) -> list[my_types.PhysicalSignal]:

    cursor = conn.execute(
        """
        SELECT
            bssid,
            detector,
            signal,
            severity,
            metadata_json,
            start_time_us,
            end_time_us
        FROM csi_signals
        WHERE
            measurement_id = ?
            AND start_time_us >= ?
            AND end_time_us <= ?
            AND bssid = ?
        """,
        (measurement_id, start_time_us, end_time_us, bssid),
    )

    rows = cursor.fetchall()

    signals: list[my_types.PhysicalSignal] = []

    for row in rows:
        signals.append(
            my_types.PhysicalSignal(
                bssid=row[0],
                detector=row[1],
                signal=row[2],
                importance=row[3],  # severity -> importance
                metadata_json=row[4],
                start_time_us=row[5],
                end_time_us=row[6],
            )
        )

    return signals
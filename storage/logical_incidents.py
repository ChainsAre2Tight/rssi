from typing import Optional

import sqlite3

import my_types

def load_logical_incident_groups(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
) -> list[my_types.LogicalIncidentGroup]:

    cursor = conn.execute(
        """
        SELECT
            bssid,
            ssid,
            MIN(start_time_us) AS first_seen_us,
            MAX(end_time_us) AS last_seen_us,
            COUNT(*) AS signal_count
        FROM detection_signals
        WHERE
            measurement_id = ?
            AND start_time_us >= ?
            AND end_time_us <= ?
        GROUP BY bssid, ssid
        """,
        (measurement_id, start_time_us, end_time_us),
    )

    rows = cursor.fetchall()

    return [
        my_types.LogicalIncidentGroup(
            bssid=row[0],
            ssid=row[1],
            first_seen_us=row[2],
            last_seen_us=row[3],
            signal_count=row[4],
        )
        for row in rows
    ]

def load_signals_for_identity(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
    bssid: str,
    ssid: Optional[str],
) -> list[my_types.LogicalSignal]:

    if ssid is None:

        cursor = conn.execute(
            """
            SELECT
                observation_id,
                bssid,
                ssid,
                detector,
                signal,
                severity,
                metadata_json,
                start_time_us,
                end_time_us
            FROM detection_signals
            WHERE
                measurement_id = ?
                AND start_time_us >= ?
                AND end_time_us <= ?
                AND bssid = ?
                AND ssid IS NULL
            """,
            (measurement_id, start_time_us, end_time_us, bssid),
        )

    else:

        cursor = conn.execute(
            """
            SELECT
                observation_id,
                bssid,
                ssid,
                detector,
                signal,
                severity,
                metadata_json,
                start_time_us,
                end_time_us
            FROM detection_signals
            WHERE
                measurement_id = ?
                AND start_time_us >= ?
                AND end_time_us <= ?
                AND bssid = ?
                AND ssid = ?
            """,
            (measurement_id, start_time_us, end_time_us, bssid, ssid),
        )

    rows = cursor.fetchall()

    signals: list[my_types.LogicalSignal] = []

    for row in rows:

        signals.append(
            my_types.LogicalSignal(
                observation_id=row[0],
                bssid=row[1],
                ssid=row[2],
                detector=row[3],
                signal=row[4],
                severity=row[5],
                metadata_json=row[6],
                start_time_us=row[7],
                end_time_us=row[8],
            )
        )

    return signals

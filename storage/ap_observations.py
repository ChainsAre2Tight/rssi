from typing import List

import sqlite3

def insert_ap_observations(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    bssids: List[str],
) -> List[int]:
    observation_ids: List[int] = []

    for bssid in bssids:
        cur = conn.execute(
            """
            INSERT INTO ap_observations (
                measurement_id,
                window_id,
                bssid
            )
            VALUES (?, ?, ?)
            RETURNING id
            """,
            (measurement_id, window_id, bssid),
        )

        observation_id = cur.fetchone()[0]
        observation_ids.append(observation_id)

    return observation_ids
from typing import List, Tuple

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

def load_window_observations(
    conn: sqlite3.Connection,
    window_id: int,
) -> List[Tuple[int, str]]:
    """
    Returns:
        List[(observation_id, bssid)]
    """

    cur = conn.execute(
        """
        SELECT id, bssid
        FROM ap_observations
        WHERE window_id = ?
        """,
        (window_id,),
    )

    return cur.fetchall()

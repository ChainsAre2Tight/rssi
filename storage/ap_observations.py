from typing import List, Tuple

import sqlite3

import my_types

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

def load_observation_csi_links(
    conn: sqlite3.Connection,
    observation_ids: List[int],
) -> List[my_types.ObservationCsiLinkRow]:

    if not observation_ids:
        return []

    placeholders = ",".join("?" for _ in observation_ids)

    cur = conn.execute(
        f"""
        SELECT
            observation_id,
            csi_packet_id,
            role
        FROM observation_csi_packets
        WHERE observation_id IN ({placeholders})
        """,
        observation_ids,
    )

    rows = cur.fetchall()

    result: List[my_types.ObservationCsiLinkRow] = []

    for row in rows:
        result.append(
            my_types.ObservationCsiLinkRow(
                observation_id=row[0],
                csi_packet_id=row[1],
                role=row[2],
            )
        )

    return result

def load_observations_in_timerange(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
    layer: int,
) -> List[my_types.ObservationRow]:

    cur = conn.execute(
        """
        SELECT
            ap_observations.id,
            ap_observations.bssid
        FROM ap_observations
        JOIN windows
            ON windows.id = ap_observations.window_id
        WHERE
            windows.measurement_id = ?
            AND windows.layer = ?
            AND windows.start_time_us < ?
            AND windows.end_time_us > ?
        """,
        (
            measurement_id,
            layer,
            end_time_us,
            start_time_us,
        ),
    )

    rows = cur.fetchall()

    result: List[my_types.ObservationRow] = []

    for row in rows:
        result.append(
            my_types.ObservationRow(
                observation_id=row[0],
                bssid=row[1],
            )
        )

    return result


def resolve_observation_id(
    conn: sqlite3.Connection,
    window_id: int,
    bssid: str,
) -> int | None:
    cur = conn.cursor()
    cur.execute("""
        SELECT id
        FROM ap_observations
        WHERE window_id = ?
          AND bssid = ?
    """, (window_id, bssid))

    row = cur.fetchone()
    if row is None:
        return None

    return int(row[0])

def resolve_observation(
    conn: sqlite3.Connection,
    window_id: int,
    bssid: str,
) -> my_types.ObservationRow | None:

    cur = conn.cursor()
    cur.execute("""
        SELECT id, bssid
        FROM ap_observations
        WHERE window_id = ? AND bssid = ?
    """, (window_id, bssid))

    row = cur.fetchone()
    if not row:
        return None

    return my_types.ObservationRow(
        observation_id=row[0],
        bssid=row[1],
    )


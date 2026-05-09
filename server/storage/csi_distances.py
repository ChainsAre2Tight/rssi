import sqlite3

import my_types

def insert_fingerprint_distance(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    bssid: str,
    reference_fingerprint_id: int,
    fingerprint_id: int,
    euclidean_dist: float,
    cosine_dist: float,
    power_ratio_db: float,   # new
) -> int:

    cur = conn.execute(
        """
        INSERT INTO csi_fingerprint_distances (
            measurement_id,
            window_id,
            bssid,
            reference_fingerprint_id,
            fingerprint_id,
            euclidean_dist,
            cosine_dist,
            power_ratio_db
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            measurement_id,
            window_id,
            bssid,
            reference_fingerprint_id,
            fingerprint_id,
            euclidean_dist,
            cosine_dist,
            power_ratio_db,
        ),
    )

    return cur.lastrowid if cur.lastrowid else -1

def get_distances_by_window(
    conn: sqlite3.Connection,
    window_id: int,
) -> list[my_types.FingerprintDistance]:

    rows = conn.execute(
        """
        SELECT id, measurement_id, window_id, bssid,
               reference_fingerprint_id, fingerprint_id,
               euclidean_dist, cosine_dist, power_ratio_db
        FROM csi_fingerprint_distances
        WHERE window_id = ?
        ORDER BY bssid
        """,
        (window_id,),
    ).fetchall()

    return [
        my_types.FingerprintDistance(
            id=r[0],
            measurement_id=r[1],
            window_id=r[2],
            bssid=r[3],
            reference_fingerprint_id=r[4],
            fingerprint_id=r[5],
            euclidean_dist=r[6],
            cosine_dist=r[7],
            power_ratio_db=r[8],
        )
        for r in rows
    ]

def get_distances_by_bssid(
    conn: sqlite3.Connection,
    measurement_id: int,
    bssid: str,
) -> list[my_types.FingerprintDistance]:

    rows = conn.execute(
        """
        SELECT id, measurement_id, window_id, bssid,
               reference_fingerprint_id, fingerprint_id,
               euclidean_dist, cosine_dist, power_ratio_db
        FROM csi_fingerprint_distances
        WHERE measurement_id = ?
          AND bssid = ?
        ORDER BY window_id
        """,
        (measurement_id, bssid),
    ).fetchall()

    return [
        my_types.FingerprintDistance(
            id=r[0],
            measurement_id=r[1],
            window_id=r[2],
            bssid=r[3],
            reference_fingerprint_id=r[4],
            fingerprint_id=r[5],
            euclidean_dist=r[6],
            cosine_dist=r[7],
            power_ratio_db=r[8],
        )
        for r in rows
    ]

def reset_distances_for_measurement(
    conn: sqlite3.Connection,
    measurement_id: int,
) -> None:

    conn.execute("""
        DELETE FROM csi_fingerprint_distances
        WHERE measurement_id = ?
    """, (measurement_id,))

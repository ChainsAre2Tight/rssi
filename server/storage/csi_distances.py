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
) -> int:
    ...

def get_distances_by_window(
    conn: sqlite3.Connection,
    window_id: int,
) -> list[my_types.FingerprintDistance]:
    ...

def get_distances_by_bssid(
    conn: sqlite3.Connection,
    measurement_id: int,
    bssid: str,
) -> list[my_types.FingerprintDistance]:
    ...

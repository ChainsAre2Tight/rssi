import sqlite3

import my_types

def insert_csi_fingerprint(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    bssid: str,
    vector: bytes,
    sensor_names_json: str,
    metadata_json: str,
    is_reference: bool,
) -> int:
    ...

def get_reference_fingerprint(
    conn: sqlite3.Connection,
    measurement_id: int,
    bssid: str,
) -> my_types.CSIFingerprint:
    ...

def get_fingerprint(
    conn: sqlite3.Connection,
    window_id: int,
    bssid: str,
) -> my_types.CSIFingerprint:
    ...

def list_fingerprints_for_bssid(
    conn: sqlite3.Connection,
    measurement_id: int,
    bssid: str,
) -> list[my_types.CSIFingerprint]:
    ...
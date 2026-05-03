import json
import numpy as np
import sqlite3
import my_types


def serialize_vector(vec: np.ndarray) -> bytes:
    """
    Store CSI vector as raw bytes (fast + compact).
    Uses float32 view of complex if needed.
    """
    return vec.astype(np.complex64).tobytes()


def deserialize_vector(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.complex64)


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def loads(s: str):
    return json.loads(s)


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

    cur = conn.execute(
        """
        INSERT INTO csi_fingerprints (
            measurement_id,
            window_id,
            bssid,
            vector,
            sensor_names_json,
            metadata_json,
            is_reference
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            measurement_id,
            window_id,
            bssid,
            vector,
            sensor_names_json,
            metadata_json,
            int(is_reference),
        ),
    )

    return cur.lastrowid

def get_reference_fingerprint(
    conn: sqlite3.Connection,
    measurement_id: int,
    bssid: str,
) -> my_types.CSIFingerprint | None:

    row = conn.execute(
        """
        SELECT id, measurement_id, window_id, bssid, is_reference,
               vector, sensor_names_json, metadata_json
        FROM csi_fingerprints
        WHERE measurement_id = ?
          AND bssid = ?
          AND is_reference = 1
        LIMIT 1
        """,
        (measurement_id, bssid),
    ).fetchone()

    if not row:
        return None

    return my_types.CSIFingerprint(
        id=row[0],
        measurement_id=row[1],
        window_id=row[2],
        bssid=row[3],
        is_reference=bool(row[4]),
        vector=row[5],
        sensor_names=loads(row[6]),
        metadata=loads(row[7]) if row[7] else {},
    )

def get_fingerprint(
    conn: sqlite3.Connection,
    window_id: int,
    bssid: str,
) -> my_types.CSIFingerprint | None:

    row = conn.execute(
        """
        SELECT id, measurement_id, window_id, bssid, is_reference,
               vector, sensor_names_json, metadata_json
        FROM csi_fingerprints
        WHERE window_id = ?
          AND bssid = ?
        LIMIT 1
        """,
        (window_id, bssid),
    ).fetchone()

    if not row:
        return None

    return my_types.CSIFingerprint(
        id=row[0],
        measurement_id=row[1],
        window_id=row[2],
        bssid=row[3],
        is_reference=bool(row[4]),
        vector=row[5],
        sensor_names=loads(row[6]),
        metadata=loads(row[7]) if row[7] else {},
    )

def list_fingerprints_for_bssid(
    conn: sqlite3.Connection,
    measurement_id: int,
    bssid: str,
) -> list[my_types.CSIFingerprint]:

    rows = conn.execute(
        """
        SELECT id, measurement_id, window_id, bssid, is_reference,
               vector, sensor_names_json, metadata_json
        FROM csi_fingerprints
        WHERE measurement_id = ?
          AND bssid = ?
        ORDER BY window_id ASC
        """,
        (measurement_id, bssid),
    ).fetchall()

    return [
        my_types.CSIFingerprint(
            id=r[0],
            measurement_id=r[1],
            window_id=r[2],
            bssid=r[3],
            is_reference=bool(r[4]),
            vector=r[5],
            sensor_names=loads(r[6]),
            metadata=loads(r[7]) if r[7] else {},
        )
        for r in rows
    ]

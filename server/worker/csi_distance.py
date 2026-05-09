import sqlite3
import numpy as np

from config import logger
import config
from compute.csi_distance import (
    IdentityScaler,
    ScalerInterface,
    compute_distances,
)
from storage.csi_fingerprints import (
    get_fingerprint,
    get_reference_fingerprint,
)
from storage.csi_distances import (
    insert_fingerprint_distance,
)
import storage


def csi_distance_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
) -> None:

    logger.info("Running CSI Stage 2 (distance) for window %d", window_id)

    measurement_id = config.MEASUREMENT_ID

    # 1. get all BSSIDs with fingerprints in this window
    cur = conn.execute(
        """
        SELECT bssid
        FROM csi_fingerprints
        WHERE window_id = ?
        GROUP BY bssid
        """,
        (window_id,)
    )
    bssids = [r[0] for r in cur.fetchall()]

    if not bssids:
        logger.info("No fingerprints in window %d", window_id)
        return

    results = []

    for bssid in bssids:
        ref = get_reference_fingerprint(conn, measurement_id, bssid)
        fp = get_fingerprint(conn, window_id, bssid)

        if ref is None:
            raise RuntimeError(f"Missing reference fingerprint for BSSID {bssid}")
        if fp is None:
            raise RuntimeError(f"Missing window fingerprint for BSSID {bssid}")

        # Extract real part (imaginary is zero in our new fingerprints)
        ref_vec = np.frombuffer(ref.vector, dtype=np.complex64).real
        test_vec = np.frombuffer(fp.vector, dtype=np.complex64).real

        if ref_vec.shape != test_vec.shape:
            raise RuntimeError(
                f"Vector size mismatch for {bssid}: "
                f"{ref_vec.shape} vs {test_vec.shape}"
            )

        # Compute shape distances (cosine, euclidean)
        scaler = IdentityScaler()
        euclid, cosine = compute_distances(ref_vec, test_vec, scaler)

        # Compute overall power ratio (in dB) from vector average
        # (the vector is concatenation of amplitude profiles; total power per BSSID is sum of all subcarrier amplitudes)
        ref_power = float(np.sum(ref_vec))          # or np.mean(ref_vec**2) – choose sum for energy proxy
        test_power = float(np.sum(test_vec))

        if ref_power > 0 and test_power > 0:
            power_ratio_db = 10 * np.log10(test_power / ref_power)
        else:
            power_ratio_db = 0.0

        if np.isnan(euclid) or np.isnan(cosine) or np.isnan(power_ratio_db):
            raise RuntimeError(f"NaN distance computed for {bssid}")

        results.append((ref, fp, euclid, cosine, power_ratio_db))

    # Batch write
    with storage.Transaction(conn) as t:
        for ref, fp, euclid, cosine, power_ratio_db in results:
            insert_fingerprint_distance(
                t,
                measurement_id,
                window_id,
                fp.bssid,
                ref.id,
                fp.id,
                euclid,
                cosine,
                power_ratio_db,   # new argument
            )

    logger.info("CSI distances computed for window %d", window_id)

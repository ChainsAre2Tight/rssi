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

    logger.info("Running CSI Stage 2 for window %d", window_id)

    measurement_id = config.MEASUREMENT_ID

    # 1. load all fingerprints for this window
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

        ref_vec = np.frombuffer(ref.vector, dtype=np.complex64)
        test_vec = np.frombuffer(fp.vector, dtype=np.complex64)

        if ref_vec.shape != test_vec.shape:
            raise RuntimeError(
                f"Vector size mismatch for {bssid}: "
                f"{ref_vec.shape} vs {test_vec.shape}"
            )

        scaler: ScalerInterface = IdentityScaler()
        euclid, cosine = compute_distances(ref_vec, test_vec, scaler)

        if np.isnan(euclid) or np.isnan(cosine):
            raise RuntimeError(f"NaN distance computed for {bssid}")

        results.append((ref, fp, euclid, cosine))

    # 2. batch write (IMPORTANT: single transaction)
    with storage.Transaction(conn) as t:

        for ref, fp, euclid, cosine in results:

            insert_fingerprint_distance(
                t,
                measurement_id,
                window_id,
                fp.bssid,
                ref.id,
                fp.id,
                euclid,
                cosine,
            )

    logger.info("CSI distances computed for window %d", window_id)

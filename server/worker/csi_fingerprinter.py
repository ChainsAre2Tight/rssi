import sqlite3
import numpy as np

import config
from config import logger
from storage.devices import get_all_devices
import storage
from compute.csi_feature_extraction import (
    build_csi_fingerprints,
    aggregate_amplitude_profile,
    compute_cross_correlations
)
from storage.csi_fingerprints import (
    insert_csi_fingerprint,
    reference_exists,
    dumps,
    serialize_vector
)


def csi_fingerprinter_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
):
    logger.info("Running CSI Stage fingerprinting for window %d", window_id)
    measurement_id = config.MEASUREMENT_ID

    # Build raw amplitude groups (bssid -> sensor -> list of amplitude arrays)
    _, amplitude_groups, sensor_usage = build_csi_fingerprints(
        conn, measurement_id, window_id, start_time_us, end_time_us
    )

    if not amplitude_groups:
        logger.info("No amplitude data for window %d", window_id)
        return

    # Fixed sensor order (all known sensors, in canonical order)
    sensor_registry = get_all_devices(conn)
    sensor_order = [s["name"] for s in sensor_registry]
    target_len = config.TARGET_CSI_SUBCARRIERS

    fingerprints_to_store = []

    for bssid, sensors_amps in amplitude_groups.items():
        # 1. Build amplitude profile for each sensor present in this window
        amp_profiles = {}
        overall_powers = {}
        for sensor, amps_list in sensors_amps.items():
            profile = aggregate_amplitude_profile(amps_list, target_len=target_len)
            amp_profiles[sensor] = profile
            overall_powers[sensor] = float(np.mean(profile))

        # 2. Build fingerprint vector: concatenate resampled profiles in sensor_order
        fingerprint_parts = []
        for sensor in sensor_order:
            if sensor in amp_profiles:
                fingerprint_parts.append(amp_profiles[sensor])
            else:
                fingerprint_parts.append(np.zeros(target_len, dtype=np.float32))
        fingerprint_vector = np.concatenate(fingerprint_parts)

        # 3. Compute cross‑correlations (on the resampled profiles, using only sensors with data)
        cross_corrs = compute_cross_correlations(amp_profiles, sensor_order)

        # 4. Metadata
        metadata = {
            "sensors": sensor_usage[bssid],
            "overall_power_per_sensor": overall_powers,
            "cross_correlations": cross_corrs,
            "total_packets": sum(sensor_usage[bssid].values()),
            "feature_version": 4,
            "n_subcarriers": target_len,
            "sensor_order": sensor_order
        }

        # Store as complex64 (imag=0) for compatibility
        vector_blob = serialize_vector(fingerprint_vector.astype(np.complex64))

        is_reference = not reference_exists(conn, measurement_id, bssid)

        fingerprints_to_store.append((bssid, vector_blob, metadata, is_reference))

    with storage.Transaction(conn, immediate=True):
        for bssid, vector_blob, metadata, is_reference in fingerprints_to_store:
            insert_csi_fingerprint(
                conn,
                measurement_id,
                window_id,
                bssid,
                vector_blob,
                dumps(sensor_order),
                dumps(metadata),
                is_reference=is_reference,
            )

    logger.info("CSI fingerprinting completed for window %d", window_id)

import sqlite3

import config
from config import logger

from storage.devices import load_sensors_for_measurement
import storage

from compute.csi_feature_extraction import (
    build_csi_fingerprints,
    aggregate_sensor_features,
    build_fingerprint_vector
)
from storage.csi_fingerprints import (
    dumps,
    insert_csi_fingerprint,
    serialize_vector
)


def csi_fingerprinter_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
):

    logger.info("Running CSI Stage 1 for window %d", window_id)

    measurement_id = config.MEASUREMENT_ID

    grouped, sensor_usage = build_csi_fingerprints(
        conn,
        measurement_id,
        window_id,
        start_time_us,
        end_time_us,
    )

    if not grouped:
        logger.info("No fingerprints computed for window %d", window_id)
        return

    sensor_registry = load_sensors_for_measurement(conn, measurement_id)
    sensor_order = [s["name"] for s in sensor_registry]

    fingerprints_to_store = []
    for bssid, sensors in grouped.items():

        sensor_signatures = {}
        metadata = {
            "sensors": {},
            "total_packets": 0,
            "completeness": 0.0,
        }

        total_packets = 0

        for sensor, feats in sensors.items():

            agg = aggregate_sensor_features(feats)
            sensor_signatures[sensor] = agg

            count = sensor_usage[bssid][sensor]
            metadata["sensors"][sensor] = count
            total_packets += count

        fingerprint_vector = build_fingerprint_vector(sensor_signatures, sensor_order)

        completeness = len(sensor_signatures) / len(sensor_order) if sensor_order else 0.0

        metadata["total_packets"] = total_packets
        metadata["completeness"] = completeness
        metadata["feature_version"] = 1
        metadata["sensor_order"] = sensor_order

        fingerprints_to_store.append((bssid, fingerprint_vector, metadata))


    with storage.Transaction(conn):

        for bssid, vector, metadata in fingerprints_to_store:

            insert_csi_fingerprint(
                conn,
                measurement_id,
                window_id,
                bssid,
                serialize_vector(vector),
                dumps(sensor_order),
                dumps(metadata),
                is_reference=False,
            )

    logger.info("Csi fingerprinting completed for window %d", window_id)

import sqlite3
import numpy as np

import config
from config import logger

from storage.devices import get_all_devices, load_sensors_for_measurement
import storage

from compute.csi_feature_extraction import (
    aggregate_amplitude_profile,
    build_csi_fingerprints,
    aggregate_sensor_features,
    build_fingerprint_vector,
    compute_cross_correlations
)
from storage.csi_fingerprints import (
    dumps,
    insert_csi_fingerprint,
    reference_exists,
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

    feature_groups, amplitude_groups, sensor_usage = build_csi_fingerprints(
        conn,
        measurement_id,
        window_id,
        start_time_us,
        end_time_us,
    )

    if not feature_groups:   # достаточно проверить по признакам
        logger.info("No fingerprints computed for window %d", window_id)
        return

    sensor_registry = get_all_devices(conn)
    sensor_order = [s["name"] for s in sensor_registry]  # все возможные сенсоры

    fingerprints_to_store = []

    for bssid, sensors in feature_groups.items():

        sensor_signatures = {}
        amp_profiles_by_sensor = {}
        metadata = {
            "sensors": {},
            "total_packets": 0,
            "completeness": 0.0,
        }

        total_packets = 0

        # Агрегируем 8-мерные признаки
        for sensor, feats in sensors.items():
            agg = aggregate_sensor_features(feats)   # усреднение по пакетам
            sensor_signatures[sensor] = agg
            count = sensor_usage[bssid][sensor]
            metadata["sensors"][sensor] = count
            total_packets += count

        # Агрегируем амплитудные профили (по каждому сенсору)
        for sensor, amps_list in amplitude_groups[bssid].items():
            amp_profiles_by_sensor[sensor] = aggregate_amplitude_profile(amps_list)

        # Строим базовый вектор из 8*N признаков
        fingerprint_vector = build_fingerprint_vector(sensor_signatures, sensor_order)   # это уже есть

        # Добавляем корреляции между сенсорами (только для тех, у которых есть профили)
        cross_corrs = compute_cross_correlations(amp_profiles_by_sensor, sensor_order)
        if cross_corrs:
            # Конкатенируем корреляции в конец вектора
            fingerprint_vector = np.concatenate([fingerprint_vector, np.array(cross_corrs, dtype=np.float32)])

        completeness = len(sensor_signatures) / len(sensor_order) if sensor_order else 0.0

        metadata["total_packets"] = total_packets
        metadata["completeness"] = completeness
        metadata["feature_version"] = 2
        metadata["sensor_order"] = sensor_order
        metadata["cross_corr_size"] = len(cross_corrs)

        fingerprints_to_store.append((bssid, fingerprint_vector, metadata))

    with storage.Transaction(conn, immediate=True):

        for bssid, vector, metadata in fingerprints_to_store:

            if len(metadata["sensors"]) < 2:
                continue

            is_reference = not reference_exists(conn, measurement_id, bssid)
            insert_csi_fingerprint(
                conn,
                measurement_id,
                window_id,
                bssid,
                serialize_vector(vector),   # ВНИМАНИЕ: serialize_vector ожидает complex64, а тут float32.
                dumps(sensor_order),
                dumps(metadata),
                is_reference=is_reference,
            )

    logger.info("Csi fingerprinting completed for window %d", window_id)

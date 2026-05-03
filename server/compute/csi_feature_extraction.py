import sqlite3
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np

import config
from config import logger

from storage.measurements import load_measurement_whitelist
from storage.ap_observations import load_observations_in_timerange, load_observation_csi_links
from storage.packets import load_csi_packets


def parse_csi(packed_csi: str) -> np.ndarray:
    """
    Restores original CSI parsing logic:
    interleaved real/imag → complex vector
    """

    values = np.fromstring(packed_csi, sep=",")

    if values.size % 2 != 0:
        logger.warning("Malformed CSI vector (odd length)")
        values = values[:-1]

    real = values[0::2]
    imag = values[1::2]

    vec = real + 1j * imag
    vec = vec.astype(np.complex64)

    target = config.CSI_COMPLEX_COUNT

    if vec.size == target:
        return vec

    if vec.size > target:
        return vec[:target]

    padded = np.zeros(target, dtype=np.complex64)
    padded[:vec.size] = vec
    return padded

def extract_csi_features(csi_vec: np.ndarray) -> np.ndarray:
    """
    CSIRecognizer-compatible feature extraction boundary.

    IMPORTANT:
    We preserve raw structure (complex vector),
    but this is the ONLY safe transformation layer.
    """

    # Identity transform for now (matches original system behavior)
    # Future-safe place for phase/amplitude transforms if needed
    return csi_vec


def aggregate_sensor_features(features: List[np.ndarray]) -> np.ndarray:
    """
    Aggregate CSI features per sensor stream.
    """
    if not features:
        return np.zeros(config.CSI_COMPLEX_COUNT, dtype=np.complex64)

    stacked = np.vstack(features)

    return np.mean(stacked, axis=0)


def build_fingerprint_vector(
    sensor_signatures: Dict[str, np.ndarray],
    sensor_order: List[str]
) -> np.ndarray:

    vectors = []

    for sensor in sensor_order:

        if sensor in sensor_signatures:
            vectors.append(sensor_signatures[sensor])
        else:
            vectors.append(
                np.zeros(config.CSI_COMPLEX_COUNT, dtype=np.complex64)
            )

    return np.concatenate(vectors)


def build_csi_fingerprints(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
):

    logger.info("Fingerprint build for window %d", window_id)

    whitelist = load_measurement_whitelist(conn, measurement_id)
    allowed_bssids = {
        bssid
        for _, bssids in whitelist.items()
        for bssid in bssids
    }

    observations = load_observations_in_timerange(
        conn,
        measurement_id,
        start_time_us,
        end_time_us,
        layer=0,
    )

    if not observations:
        return {}, {}

    observation_bssid = {
        obs.observation_id: obs.bssid
        for obs in observations
        if obs.bssid in allowed_bssids
    }

    if not observation_bssid:
        return {}, {}

    # CSI links
    links = load_observation_csi_links(
        conn,
        list(observation_bssid.keys()),
    )

    if not links:
        return {}, {}

    packet_to_bssid = {}
    packet_ids = set()

    for link in links:
        if link.role != "ap":
            continue

        bssid = observation_bssid.get(link.observation_id)
        if not bssid:
            continue

        packet_to_bssid[link.csi_packet_id] = bssid
        packet_ids.add(link.csi_packet_id)

    packets = load_csi_packets(conn, list(packet_ids))

    grouped = defaultdict(lambda: defaultdict(list))
    sensor_usage = defaultdict(lambda: defaultdict(int))

    for p in packets:

        bssid = packet_to_bssid.get(p.id)
        if not bssid:
            continue

        csi_vec = parse_csi(p.csi)
        feature = extract_csi_features(csi_vec)

        grouped[bssid][p.device].append(feature)
        sensor_usage[bssid][p.device] += 1

    return grouped, sensor_usage

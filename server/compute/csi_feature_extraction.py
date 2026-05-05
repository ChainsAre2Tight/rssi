import sqlite3
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np

import config
from config import logger

from storage.measurements import load_measurement_whitelist
from storage.ap_observations import load_observations_in_timerange, load_observation_csi_links
from storage.packets import load_csi_packets


def parse_csi(packed_csi: str, skip_meta: int = 4) -> np.ndarray:
    if not isinstance(packed_csi, str):
        return np.zeros(0, dtype=np.complex64)

    try:
        nums = np.fromstring(packed_csi, sep=",", dtype=np.int16)
    except Exception:
        return np.zeros(0, dtype=np.complex64)

    if nums.size <= skip_meta:
        return np.zeros(0, dtype=np.complex64)

    data = nums[skip_meta:]

    if data.size % 2 != 0:
        data = data[:-1]

    real = data[0::2]
    imag = data[1::2]

    return (real + 1j * imag).astype(np.complex64)

def calibrate_phase(phase: np.ndarray) -> np.ndarray:
    """
    Remove linear trend from phase.
    """
    n = len(phase)
    if n < 2:
        return phase

    x = np.arange(n, dtype=np.float32)
    A = np.vstack([x, np.ones(n)]).T

    # Least squares fit: phase ≈ slope * x + intercept
    slope, intercept = np.linalg.lstsq(A, phase, rcond=None)[0]

    return phase - (slope * x + intercept)


def extract_csi_features(csi_vec: np.ndarray) -> np.ndarray:
    """
    Reproduces original CSIRecognizer feature extraction.

    Input:
        complex CSI vector

    Output:
        8-dim float vector
    """

    if csi_vec.size == 0:
        return np.zeros(8, dtype=np.float32)

    # Amplitude
    amp = np.abs(csi_vec)

    # Phase
    phase = np.angle(csi_vec)
    phase_cal = calibrate_phase(phase)

    # Stats
    feats = np.array([
        np.mean(amp),
        np.std(amp),
        np.max(amp),
        np.min(amp),

        np.mean(phase_cal),
        np.std(phase_cal),
        np.max(phase_cal),
        np.min(phase_cal),
    ], dtype=np.float32)

    return feats

def aggregate_amplitude_profile(amps_list: list[np.ndarray]) -> np.ndarray:
    if not amps_list:
        return np.array([], dtype=np.float32)

    min_len = min(len(a) for a in amps_list)
    trimmed = np.array([a[:min_len] for a in amps_list])
    return np.mean(trimmed, axis=0).astype(np.float32)


def compute_cross_correlations(
    amp_profiles_by_sensor: dict[str, np.ndarray],
    sensor_order: list[str]
) -> list[float]:

    correlations = []
    sensors_present = [s for s in sensor_order if s in amp_profiles_by_sensor]

    for i in range(len(sensors_present)):
        for j in range(i + 1, len(sensors_present)):
            s_i = sensors_present[i]
            s_j = sensors_present[j]

            prof_i = amp_profiles_by_sensor[s_i]
            prof_j = amp_profiles_by_sensor[s_j]

            if prof_i.size == 0 or prof_j.size == 0:
                correlations.append(0.0)
                continue

            min_len = min(len(prof_i), len(prof_j))
            if min_len < 2:
                correlations.append(0.0)
                continue

            corr = np.corrcoef(prof_i[:min_len], prof_j[:min_len])[0, 1]
            if np.isnan(corr):
                correlations.append(0.0)
            else:
                correlations.append(float(corr))

    return correlations

def aggregate_sensor_features(features: list[np.ndarray]) -> np.ndarray:
    """
    Aggregate per-sensor packet features → single 8-dim vector
    """
    if not features:
        return np.zeros(8, dtype=np.float32)

    stacked = np.vstack(features)
    return np.mean(stacked, axis=0)


def build_fingerprint_vector(
    sensor_signatures: dict[str, np.ndarray],
    sensor_order: list[str]
) -> np.ndarray:

    vectors = []

    for sensor in sensor_order:
        if sensor in sensor_signatures:
            vectors.append(sensor_signatures[sensor])
        else:
            vectors.append(np.zeros(8, dtype=np.float32))

    return np.concatenate(vectors)


def build_csi_fingerprints(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
):

    logger.info("Fingerprint building for window %d", window_id)

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
        return {}, {}, {}

    observation_bssid = {
        obs.observation_id: obs.bssid
        for obs in observations
        if obs.bssid in allowed_bssids
    }

    if not observation_bssid:
        return {}, {}, {}

    links = load_observation_csi_links(
        conn,
        list(observation_bssid.keys()),
    )

    if not links:
        return {}, {}, {}

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

    feature_groups = defaultdict(lambda: defaultdict(list))      # bssid -> device -> list of 8-dim vectors
    amplitude_groups = defaultdict(lambda: defaultdict(list))    # bssid -> device -> list of amplitude arrays
    sensor_usage = defaultdict(lambda: defaultdict(int))

    for p in packets:
        bssid = packet_to_bssid.get(p.id)
        if not bssid:
            continue

        csi_vec = parse_csi(p.csi)
        if csi_vec.size == 0:
            continue

        feature = extract_csi_features(csi_vec)          # 8 признаков
        amp_profile = np.abs(csi_vec).astype(np.float32) # амплитуды по поднесущим

        feature_groups[bssid][p.device].append(feature)
        amplitude_groups[bssid][p.device].append(amp_profile)
        sensor_usage[bssid][p.device] += 1

    return feature_groups, amplitude_groups, sensor_usage

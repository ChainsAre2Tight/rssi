import sqlite3
from typing import List, Dict, Set

import numpy as np

import config
from config import logger

import my_types
from storage.packets import load_csi_packets
from storage.ap_observations import load_observations_in_timerange, load_observation_csi_links
from storage.measurements import load_measurement_whitelist
from storage.datasets import NPZDatasetWriter



def build_whitelist_bssid_set(whitelist: dict) -> Set[str]:

    result: Set[str] = set()

    for ssid, bssids in whitelist.items():
        for bssid in bssids:
            result.add(bssid)

    return result

def parse_csi_csv_fixed(csi: str) -> np.ndarray:
    values = np.fromstring(csi, sep=",")

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
        logger.debug("Truncating CSI %d to length %d", vec.size, target)
        return vec[:target]

    # pad shorter vectors
    logger.debug("Padding CSI %d to length %d", vec.size, target)

    padded = np.zeros(target, dtype=np.complex64)
    padded[:vec.size] = vec
    return padded


def build_dataset_arrays(samples: List[my_types.DatasetSample]):

    sensor_names = sorted({s.sensor for s in samples})
    bssid_names = sorted({s.bssid for s in samples})
    sensor_index: Dict[str, int] = {s: i for i, s in enumerate(sensor_names)}
    bssid_index: Dict[str, int] = {b: i for i, b in enumerate(bssid_names)}

    n = len(samples)
    packet_ids = np.empty(n, dtype=np.int64)
    timestamps = np.empty(n, dtype=np.int64)
    sensor_idx = np.empty(n, dtype=np.int16)
    bssid_idx = np.empty(n, dtype=np.int16)
    channel = np.empty(n, dtype=np.int16)
    rssi = np.empty(n, dtype=np.int16)
    noise = np.empty(n, dtype=np.int16)

    csi_vectors = []

    for i, s in enumerate(samples):

        packet_ids[i] = s.packet_id
        timestamps[i] = s.timestamp_us
        sensor_idx[i] = sensor_index[s.sensor]
        bssid_idx[i] = bssid_index[s.bssid]
        channel[i] = s.channel
        rssi[i] = s.rssi
        noise[i] = s.noise_floor

        csi_vectors.append(parse_csi_csv_fixed(s.csi))

    csi_matrix = np.vstack(csi_vectors)

    dataset = {
        "packet_id": packet_ids,
        "timestamp_us": timestamps,
        "sensor_index": sensor_idx,
        "bssid_index": bssid_idx,
        "channel": channel,
        "rssi": rssi,
        "noise_floor": noise,
        "csi": csi_matrix,
        "sensor_names": np.array(sensor_names),
        "bssids": np.array(bssid_names),
    }

    return dataset, sensor_names, bssid_names


def dataset_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
) -> None:

    logger.info("Building CSI/RSSI dataset for aggregation window %d", window_id)

    measurement_id = config.MEASUREMENT_ID
    whitelist = load_measurement_whitelist(
        conn,
        measurement_id,
    )

    allowed_bssids = build_whitelist_bssid_set(whitelist)
    if not allowed_bssids:
        logger.warning("Current whitelist has no bssids so dataset will contain no aps")


    observations = load_observations_in_timerange(
        conn,
        measurement_id,
        start_time_us,
        end_time_us,
        my_types.OBSERVATION_WINDOWS.layer,
    )

    if not observations:
        logger.info("No observations in aggregation window %d", window_id)
        return

    observation_bssid: Dict[int, str] = {}
    for obs in observations:
        if obs.bssid not in allowed_bssids:
            continue
        observation_bssid[obs.observation_id] = obs.bssid

    if not observation_bssid:
        logger.info("No whitelisted AP observations in window %d", window_id)
        return

    observation_ids = list(observation_bssid.keys())

    links = load_observation_csi_links(
        conn,
        observation_ids,
    )

    if not links:
        logger.info("No CSI packets linked to observations")
        return

    packet_to_bssid: Dict[int, str] = {}
    unique_packet_ids: Set[int] = set()

    for link in links:

        if link.role != "ap":
            continue

        bssid = observation_bssid.get(link.observation_id)
        if bssid is None:
            continue

        packet_id = link.csi_packet_id
        packet_to_bssid[packet_id] = bssid
        unique_packet_ids.add(packet_id)

    if not unique_packet_ids:
        logger.info("No AP CSI packets found")
        return

    packets = load_csi_packets(
        conn,
        list(unique_packet_ids),
    )

    if not packets:
        logger.info("No CSI packets loaded")
        return

    samples: List[my_types.DatasetSample] = []

    sensors: Set[str] = set()
    bssids: Set[str] = set()

    for packet in packets:

        bssid = packet_to_bssid.get(packet.id)

        if bssid is None:
            continue

        sample = my_types.DatasetSample(
            packet_id=packet.id,
            timestamp_us=packet.unix_time_us,
            sensor=packet.device,
            bssid=bssid,
            channel=packet.channel,
            rssi=packet.rssi,
            noise_floor=packet.noise_floor,
            csi=packet.csi,
        )

        samples.append(sample)
        sensors.add(packet.device)
        bssids.add(bssid)

    logger.info(
        "Dataset window %d: %d packets | %d sensors | %d APs",
        window_id,
        len(samples),
        len(sensors),
        len(bssids),
    )

    dataset, sensor_names, bssid_names = build_dataset_arrays(samples)

    desc = my_types.DatasetDescriptor(
        measurement_id=measurement_id,
        window_id=window_id,
    )
    metadata = my_types.DatasetMetadata(
        measurement_id=measurement_id,
        window_id=window_id,
        start_time_us=start_time_us,
        end_time_us=end_time_us,
        dataset_version=1,
        schema_version=1,
        packet_count=len(samples),
        sensor_count=len(sensor_names),
        ap_count=len(bssid_names),
    )

    writer = NPZDatasetWriter()
    writer.write(
        desc,
        dataset,
        metadata,
    )

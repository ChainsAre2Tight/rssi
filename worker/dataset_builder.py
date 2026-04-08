import sqlite3
from typing import List, Dict, Set

import config
from config import logger

import my_types
from storage.packets import load_csi_packets
from storage.ap_observations import load_observations_in_timerange, load_observation_csi_links
from storage.measurements import load_measurement_whitelist



def build_whitelist_bssid_set(whitelist: dict) -> Set[str]:

    result: Set[str] = set()

    for ssid, bssids in whitelist.items():
        for bssid in bssids:
            result.add(bssid)

    return result


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

    #TODO: store the dataset
import sqlite3
from typing import Dict, List, Tuple

import config
from config import logger

from storage.events import load_window_events, update_event_observation_ids
from storage.ap_observations import insert_ap_observations
import storage


BROADCAST_BSSID = "FF:FF:FF:FF:FF:FF"


def observation_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
) -> None:

    logger.debug("Building AP observations for window %d", window_id)

    events = load_window_events(conn, window_id)

    if not events:
        logger.info("No events for window %d", window_id)
        return

    unique_bssids: List[str] = []
    bssid_index: Dict[str, int] = {}

    event_obs_index: Dict[int, int] = {}

    for event_id, bssid in events:

        if bssid is None:
            continue

        if bssid == BROADCAST_BSSID:
            continue

        idx = bssid_index.get(bssid)

        if idx is None:
            idx = len(unique_bssids)
            unique_bssids.append(bssid)
            bssid_index[bssid] = idx

        event_obs_index[event_id] = idx

    if not unique_bssids:
        logger.info("No valid BSSIDs in window %d", window_id)
        return

    logger.info(
        "Window %d contains %d AP observations",
        window_id,
        len(unique_bssids),
    )

    with storage.Transaction(conn):

        observation_ids = insert_ap_observations(
            conn,
            config.MEASUREMENT_ID,
            window_id,
            unique_bssids,
        )

        update_rows: List[Tuple[int, int]] = []
        for event_id, obs_idx in event_obs_index.items():
            obs_id = observation_ids[obs_idx]
            update_rows.append((obs_id, event_id))

        update_event_observation_ids(conn, update_rows)
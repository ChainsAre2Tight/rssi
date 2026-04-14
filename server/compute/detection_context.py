from typing import Dict, List, Set

import sqlite3

import config

from my_types import EventRow, DetectionContext

from storage.ap_observations import load_window_observations
from storage.events import load_events_for_observations
from storage.measurements import load_measurement_whitelist


def build_detection_context(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
) -> DetectionContext:

    observations = load_window_observations(conn, window_id)

    observation_ids: List[int] = []
    bssid_by_observation: Dict[int, str] = {}

    for obs_id, bssid in observations:
        observation_ids.append(obs_id)
        bssid_by_observation[obs_id] = bssid

    events_raw = load_events_for_observations(conn, observation_ids)

    events_by_observation: Dict[int, List[EventRow]] = {}
    ssids_by_observation: Dict[int, Set[str]] = {}
    hidden_ssid_observed: Dict[int, bool] = {}

    for obs_id in observation_ids:
        events_by_observation[obs_id] = []
        ssids_by_observation[obs_id] = set()
        hidden_ssid_observed[obs_id] = False

    for obs_id, event in events_raw:

        events_by_observation[obs_id].append(event)

        if event.ssid:
            ssids_by_observation[obs_id].add(event.ssid)
        else:
            hidden_ssid_observed[obs_id] = True

    whitelist = load_measurement_whitelist(conn, measurement_id)

    return DetectionContext(
        window_id=window_id,
        start_time_us=start_time_us,
        end_time_us=end_time_us,
        observation_ids=observation_ids,
        bssid_by_observation=bssid_by_observation,
        events_by_observation=events_by_observation,
        ssids_by_observation=ssids_by_observation,
        hidden_ssid_observed=hidden_ssid_observed,
        whitelist=whitelist,
    )
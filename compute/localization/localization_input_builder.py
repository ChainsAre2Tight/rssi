import sqlite3

import my_types
from storage.ap_observations import resolve_observation
from storage.events import get_ap_event_ids, get_packets_for_events


def build_localization_input(
    conn: sqlite3.Connection,
    window_id: int,
    bssid: str,
    calibration_model: my_types.CalibrationModel,
) -> tuple[my_types.LocalizationInput | None, int | None]:

    obs = resolve_observation(conn, window_id, bssid)
    if obs is None:
        return None, None

    event_ids = get_ap_event_ids(conn, obs.observation_id)

    packets = get_packets_for_events(conn, event_ids)

    rssi_values = build_rssi_values(
        calibration_model.devices,
        packets,
    )

    loc_input = my_types.LocalizationInput(
        devices=calibration_model.devices,
        positions=calibration_model.positions,
        gain_models=calibration_model.gain_models,
        rssi_values=rssi_values,
    )

    return loc_input, obs.observation_id

def build_rssi_values(
    devices: list[str],
    packets: list[my_types.ID_PACKET],
) -> dict[str, list[int]]:

    rssi_values = {dev: [] for dev in devices}

    for pkt in packets:
        dev = pkt["device"]
        if dev in rssi_values:
            rssi_values[dev].append(pkt["rssi"])

    return rssi_values

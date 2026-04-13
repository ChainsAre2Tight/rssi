

import sqlite3

import my_types


def build_localization_input(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    observation_id: int,
    calibration_model: my_types.CalibrationModel,
) -> my_types.LocalizationInput | None:
    """
    Should:
        - fetch RSSI per sensor for this AP (window + observation)
        - intersect with calibration devices
        - filter empty sensors
    """
    return None

import sqlite3

import my_types


def calibration_orchestrator(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
) -> my_types.CalibrationModel | None:
    """
    Should:
        - collect sensor↔sensor packets in window
        - build pairwise RSSI structure
        - call calibrate_devices()
        - attach positions
    """
    return None

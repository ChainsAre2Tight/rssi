import sqlite3

from typing import List

import config
from config import logger

from detectors.csi.csi_detector import CSIDetector
from storage.csi_signals import insert_csi_signals
from storage.csi_distances import get_distances_by_window
import storage

import my_types


def csi_detection_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
) -> None:

    logger.debug("Running csi detection stage for window %d", window_id)

    distances = get_distances_by_window(
        conn,
        window_id,
    )

    signals: List[my_types.CSISignal] = []

    for distance in distances:
    
        detected = CSIDetector(distance)
        signals.extend(detected)

    if not signals:
        logger.debug("No csi detection signals for window %d", window_id)
        return

    logger.info(
        "Detected %d csi signals in window %d",
        len(signals),
        window_id,
    )

    with storage.Transaction(conn):

        insert_csi_signals(
            conn,
            config.MEASUREMENT_ID,
            window_id,
            start_time_us,
            end_time_us,
            signals,
        )

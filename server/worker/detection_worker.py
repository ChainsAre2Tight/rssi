import sqlite3

import config
from config import logger

from compute.detection_context import build_detection_context
from compute.run_detectors import run_detectors
from detectors.registry import DETECTORS

from storage.detection_signals import insert_detection_signals
import storage


def detection_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
) -> None:

    logger.debug("Running detection stage for window %d", window_id)

    ctx = build_detection_context(
        conn,
        config.MEASUREMENT_ID,
        window_id,
        start_time_us,
        end_time_us,
    )

    if not ctx.observation_ids:
        logger.info("No observations in window %d", window_id)
        return

    signals = run_detectors(ctx, DETECTORS)

    if not signals:
        logger.debug("No detection signals for window %d", window_id)
        return

    logger.info(
        "Detected %d signals in window %d",
        len(signals),
        window_id,
    )

    with storage.Transaction(conn):

        insert_detection_signals(
            conn,
            config.MEASUREMENT_ID,
            window_id,
            start_time_us,
            end_time_us,
            signals,
        )
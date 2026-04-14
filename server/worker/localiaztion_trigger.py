import sqlite3

import config
import my_types
import storage
from storage.detection_signals import load_detection_signals_for_window

from config import logger
from storage.localization_jobs import insert_localization_jobs


def select_bssids_for_localization(
    signals: list[my_types.DetectionSignal],
    threshold: my_types.Severity,
) -> list[str]:

    by_bssid: dict[str, list[my_types.Severity]] = {}

    for s in signals:
        sev = my_types.Severity.from_str(s.severity)
        by_bssid.setdefault(s.bssid, []).append(sev)

    selected: list[str] = []

    for bssid, severities in by_bssid.items():
        max_sev = max(severities, key=lambda s: s.rank)
        if max_sev.rank >= threshold.rank:
            selected.append(bssid)

    return selected

def localization_trigger_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
) -> None:

    logger.debug("Running localization trigger for window %d", window_id)

    signals = load_detection_signals_for_window(conn, window_id)

    if not signals:
        logger.debug("No signals in window %d", window_id)
        return

    threshold = my_types.Severity.HIGH

    bssids = select_bssids_for_localization(signals, threshold)

    if not bssids:
        logger.debug("No BSSIDs passed threshold in window %d", window_id)
        return

    jobs = [(window_id, bssid) for bssid in bssids]

    with storage.Transaction(conn):
        inserted, ignored = insert_localization_jobs(
            conn,
            config.MEASUREMENT_ID,
            jobs,
        )

    logger.info(
        "Localization jobs for window %d: inserted=%d ignored=%d",
        window_id,
        inserted,
        ignored,
    )
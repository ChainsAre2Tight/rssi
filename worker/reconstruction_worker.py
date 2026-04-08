import sqlite3

from worker.window_worker import run_window_worker
from compute.reconstruction import reconstruct_window_packets
from storage import insert_events, insert_event_packets
import storage

import config
from config import logger

def reconstruction_processor(
    conn: sqlite3.Connection,
    window_id: int,
    start_time_us: int,
    end_time_us: int,
) -> None:

    logger.debug("Reconstructing events for window %d", window_id)
    events, packet_links = reconstruct_window_packets(
        conn,
        config.MEASUREMENT_ID,
        start_time_us,
        end_time_us,
    )
    logger.info("Reconstructed %d events for window %d", len(events), window_id)

    with storage.Transaction(conn):
        event_ids = insert_events(
            conn,
            config.MEASUREMENT_ID,
            window_id,
            events,
        )
        insert_event_packets(
            conn,
            event_ids,
            packet_links,
        )


if __name__ == "__main__":

    run_window_worker(
        required_stage=None,
        completed_stage="reconstructed",
        processor=reconstruction_processor,
    )
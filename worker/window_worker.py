import time
from typing import Callable
import logging

import sqlite3

import config
import storage
from storage.windows import (
    claim_next_window,
    complete_window_stage,
    fail_window,
)

from compute.window import try_create_next_window


def run_window_worker(
    required_stage: str | None,
    completed_stage: str,
    processor: Callable[
        [sqlite3.Connection, int, int, int],
        None
    ],
    sleep_seconds: int = 5,
) -> None:

    while True:
        with storage.Session() as conn:
            with storage.Transaction(conn, immediate=True) as t:
                logging.debug("Trying to claim a window...")
                window = claim_next_window(
                    t,
                    config.MEASUREMENT_ID,
                    required_stage,
                )

        if window is not None:
            logging.debug("Window was claimed")
            window_id, start_time_us, end_time_us = window
            try:
                with storage.Session() as conn:
                    logging.info("Running a processor agains a window %d", window_id)
                    processor(
                        conn,
                        window_id,
                        start_time_us,
                        end_time_us,
                    )
            
                with storage.Session() as conn:
                    with storage.Transaction(conn, immediate=True) as t:
                        complete_window_stage(t, window_id, completed_stage)
                        logging.info("Window processed successfully")

            except Exception as e:
                logging.exception("Error during window processing: %e", e)
                with storage.Session() as conn:
                    with storage.Transaction(conn, immediate=True) as t:
                        fail_window(t, window_id)

                raise

            continue

        created = False
        logging.debug("No window claimed, creating a new one...")
        with storage.Session() as conn:
            with storage.Transaction(conn, immediate=True) as t:
                created = try_create_next_window(t, config.MEASUREMENT_ID)

        if created:
            logging.debug("Window successfully created")
            continue

        logging.debug("No packets for selected measurement exist, sleeping")
        time.sleep(sleep_seconds)
import time
from typing import Callable

import sqlite3

import config
from config import logger
import storage
from storage.windows import (
    claim_next_window,
    complete_window_stage,
    fail_window,
)

import my_types

from compute.window import try_create_next_window


def run_window_worker(
    layer_config: my_types.WindowSpec,
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
                logger.debug("Trying to claim a window...")
                window = claim_next_window(
                    t,
                    config.MEASUREMENT_ID,
                    layer_config.layer,
                    required_stage,
                )

        if window is not None:
            logger.debug("Window was claimed")
            window_id, start_time_us, end_time_us = window
            try:
                with storage.Session() as conn:
                    logger.info("Running a processor against window %d", window_id)
                    processor(
                        conn,
                        window_id,
                        start_time_us,
                        end_time_us,
                    )
            
                with storage.Session() as conn:
                    with storage.Transaction(conn, immediate=True) as t:
                        complete_window_stage(t, window_id, completed_stage)
                        logger.info("Window processed successfully")

            except Exception as e:
                logger.exception("Error during window processing: %e", e)
                with storage.Session() as conn:
                    with storage.Transaction(conn, immediate=True) as t:
                        fail_window(t, window_id)

                raise

            continue

        created = False
        logger.debug("No window claimed, trying to create a new one...")
        with storage.Session() as conn:
            with storage.Transaction(conn, immediate=True) as t:
                created = try_create_next_window(
                    t, 
                    config.MEASUREMENT_ID,
                    layer_config,
                )

        if created:
            logger.debug("Window successfully created")
            continue

        logger.debug("No windows are ready, sleeping for %s sec", sleep_seconds)
        time.sleep(sleep_seconds)
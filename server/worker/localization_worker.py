import time

import storage
from storage.localization_jobs import (
    claim_next_localization_job,
    complete_localization_job,
    fail_localization_job,
)

from config import logger

from compute.localization.processor import localization_orchestrator


def run_localization_worker(
    sleep_seconds: int = 5,
) -> None:

    while True:

        with storage.Session() as conn:
            with storage.Transaction(conn, immediate=True) as t:
                job = claim_next_localization_job(t)

        if job is not None:
            logger.debug("Claimed localization job %s", job["id"])

            try:
                with storage.Session() as conn:
                    logger.info(
                        "Running localization for window=%d bssid=%s",
                        job["window_id"],
                        job["bssid"],
                    )

                    localization_orchestrator(
                        conn,
                        job["measurement_id"],
                        job["window_id"],
                        job["bssid"],
                    )

                with storage.Session() as conn:
                    with storage.Transaction(conn, immediate=True) as t:
                        complete_localization_job(t, job["id"])
                        logger.info("Localization job completed")
                        continue

            except Exception as e:
                logger.exception("Localization job failed")

                with storage.Session() as conn:
                    with storage.Transaction(conn, immediate=True) as t:
                        fail_localization_job(
                            t,
                            job["id"],
                        )
                        continue

        logger.debug("No localization jobs, sleeping %s sec", sleep_seconds)
        time.sleep(sleep_seconds)

import sqlite3

import storage
import config
from my_types import STAGES


def reset_detection(measurement_id: int) -> None:

    with storage.Session() as conn:

        with storage.Transaction(conn):

            conn.execute(
                """
                DELETE FROM detection_signals
                WHERE measurement_id = ?
                """,
                (measurement_id,),
            )

            conn.execute(
                """
                UPDATE windows
                SET stage = ?,
                    status = 'pending'
                WHERE measurement_id = ?
                    AND stage = 'detected'
                """,
                (STAGES.AP_OBSERVATIONS, measurement_id,),
            )


def main() -> None:

    measurement_id = config.MEASUREMENT_ID

    print(f"Resetting detection for measurement {measurement_id}")

    reset_detection(measurement_id)

    print("Done")


if __name__ == "__main__":
    main()
import sqlite3

import storage
import config
from my_types import STAGES, AGGREGATION_WINDOWS, AGGREGATION_STAGES



def reset_aggregation(measurement_id: int) -> None:

    with storage.Session() as conn:

        with storage.Transaction(conn):

            conn.execute(
                """
                UPDATE windows
                SET stage = ?,
                    status = 'pending'
                WHERE
                    measurement_id = ?
                    AND layer = ?
                """,
                (
                    STAGES.NONE,
                    measurement_id,
                    AGGREGATION_WINDOWS.layer,
                ),
            )


def main() -> None:

    measurement_id = config.MEASUREMENT_ID

    print(f"Resetting aggregation windows for measurement {measurement_id}")

    reset_aggregation(measurement_id)

    print("Done")


if __name__ == "__main__":
    main()
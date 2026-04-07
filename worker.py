import time
import sqlite3

import storage
import config

from compute.reconstruction import reconstruct_measurement


def process_measurement(conn: sqlite3.Connection) -> None:

    reconstruct_measurement(conn, config.MEASUREMENT_ID)

    # TODO: future stages
    # process_windows(conn, config.MEASUREMENT_ID)
    # create_ap_observations(conn, config.MEASUREMENT_ID)
    # attach_csi_packets(conn, config.MEASUREMENT_ID)


def main_loop() -> None:

    while True:

        try:

            with storage.Session() as conn:

                with storage.Transaction(conn) as t:

                    process_measurement(t)

        except Exception as exc:
            # simple visibility for now
            print("worker error:", exc)

        time.sleep(5)


if __name__ == "__main__":
    main_loop()
import sqlite3
from typing import List

import my_types


def insert_event_observations(
    conn: sqlite3.Connection,
    event_ids: List[int],
    observations_per_event: List[List[my_types.ObservationRow]],
):
    values = []

    for event_id, observations in zip(event_ids, observations_per_event):

        for obs in observations:

            values.append(
                (
                    event_id,
                    obs.device,
                    obs.boot_time_us,
                    obs.approx_unix_time_us,
                    obs.rssi,
                    obs.noise_floor,
                    obs.channel,
                    obs.packet_id,
                )
            )

    if not values:
        return

    cur = conn.cursor()

    cur.executemany(
        """
        INSERT INTO event_observations (
            event_id,
            device,
            boot_time_us,
            approx_unix_time_us,
            rssi,
            noise_floor,
            channel,
            packet_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        values,
    )
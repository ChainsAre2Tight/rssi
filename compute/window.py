import time
import sqlite3

import config

from storage.windows import (
    get_last_window,
    insert_window,
)
from storage.packets import get_first_packet_time, get_last_packet_time


def align_time_to_window(
    t: int,
    step_us: int,
) -> int:

    return (t // step_us) * step_us

def try_create_next_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    layer: int
):

    last = get_last_window(conn, measurement_id, layer)

    if last is None:

        first_packet = get_first_packet_time(conn, measurement_id)

        if first_packet is None:
            return False

        # TODO: add support for different window sizes for different layers
        start = align_time_to_window(
            first_packet,
            config.WINDOW_STEP_US,
        )

        seq = 0

    else:

        seq, last_start = last

        start = last_start + config.WINDOW_STEP_US
        seq += 1

    max_packet_time = get_last_packet_time(
        conn,
        measurement_id,
    )

    if max_packet_time is None:
        return False

    if start > max_packet_time:
        return False

    end = start + config.WINDOW_SIZE_US

    return insert_window(
        conn,
        measurement_id,
        layer,
        sequence_id=seq,
        start_time_us=start,
        end_time_us=end,
    )
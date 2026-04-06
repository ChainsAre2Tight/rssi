import sqlite3
from typing import List

import my_types

from storage.packets import stream_timed_packets
from compute.event_reconstruction import EventReconstructor

from storage import (
    insert_events,
    insert_event_observations,
    mark_packets_processed,
)


def reconstruct_measurement(
    conn: sqlite3.Connection,
    measurement_id: int,
    batch_commit_events: int = 50,
) -> None:

    recon = EventReconstructor()

    processed_packet_ids: List[int] = []

    event_buffer: List[my_types.EventRow] = []
    obs_buffer: List[List[my_types.ObservationRow]] = []

    for pkt in stream_timed_packets(conn, measurement_id):

        processed_packet_ids.append(pkt["id"])
        recon.process(pkt)
        events, observations = recon.pop_ready()

        if events:
            event_buffer.extend(events)
            obs_buffer.extend(observations)

        if len(event_buffer) >= batch_commit_events:

            event_ids = insert_events(conn, measurement_id, event_buffer)

            insert_event_observations(conn, event_ids, obs_buffer)
            mark_packets_processed(conn, processed_packet_ids)

            event_buffer.clear()
            obs_buffer.clear()
            processed_packet_ids.clear()

    events, observations = recon.flush_all()

    event_buffer.extend(events)
    obs_buffer.extend(observations)

    if event_buffer:
        event_ids = insert_events(conn, measurement_id, event_buffer)
        insert_event_observations(conn, event_ids, obs_buffer)

    if processed_packet_ids:
        mark_packets_processed(conn, processed_packet_ids)

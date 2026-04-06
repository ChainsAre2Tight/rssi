from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

import sqlite3

import my_types
from storage import (
    stream_timed_packets,
    insert_events,
    link_packets_to_events,
)


MERGE_WINDOW_US = 100_000
REORDER_WINDOW_US = 30_000_000


@dataclass(slots=True)
class _ActiveEvent:
    src_mac: str
    seq: int
    type: int
    subtype: int
    dst_mac: str | None
    bssid: str | None
    ssid: str | None

    first_time_us: int
    last_time_us: int

    # stores ids of packets to link them to events later
    observations: List[int] = field(default_factory=list)

    def try_merge(self, pkt: my_types.ID_PACKET) -> bool:

        t = pkt["unix_time_us"]

        new_first = min(self.first_time_us, t)
        new_last = max(self.last_time_us, t)


        if new_last - new_first > MERGE_WINDOW_US:
            return False

        self.first_time_us = new_first
        self.last_time_us = new_last

        self.observations.append(pkt["id"])

        return True


class _EventReconstructor:

    def __init__(self):

        self.active: Dict[
            Tuple[str, int, int, int],
            List[_ActiveEvent],
        ] = defaultdict(list)

        self.max_seen_time = 0

    def process(self, pkt: my_types.ID_PACKET) -> None:

        t = pkt["unix_time_us"]

        if t > self.max_seen_time:
            self.max_seen_time = t

        key = (pkt["src"], pkt["seq"], pkt["type"], pkt["sub"], pkt["dst"], pkt["bssid"], pkt["ch"], pkt["ssid"])

        events = self.active[key]

        for ev in events:
            if ev.try_merge(pkt):
                return

        ev = _ActiveEvent(
            src_mac=pkt["src"],
            seq=pkt["seq"],
            type=pkt["type"],
            subtype=pkt["sub"],
            dst_mac=pkt["dst"],
            bssid=pkt["bssid"],
            ssid=pkt["ssid"],
            first_time_us=t,
            last_time_us=t,
        )

        ev.observations.append(pkt["id"])

        events.append(ev)

    def pop_ready(
        self,
    ) -> Tuple[List[my_types.EventRow], List[List[int]]]:

        watermark = self.max_seen_time - REORDER_WINDOW_US

        ready_events: List[my_types.EventRow] = []
        ready_obs: List[List[int]] = []

        for key in list(self.active.keys()):

            events = self.active[key]
            remaining = []

            for ev in events:

                if ev.last_time_us < watermark:

                    ready_events.append(
                        my_types.EventRow(
                            src_mac=ev.src_mac,
                            seq=ev.seq,
                            type=ev.type,
                            subtype=ev.subtype,
                            dst_mac=ev.dst_mac,
                            bssid=ev.bssid,
                            ssid=ev.ssid,
                            first_time_us=ev.first_time_us,
                            last_time_us=ev.last_time_us,
                            approx_time_us=(
                                ev.first_time_us + ev.last_time_us
                            ) // 2,
                        )
                    )

                    ready_obs.append(ev.observations)

                else:
                    remaining.append(ev)

            if remaining:
                self.active[key] = remaining
            else:
                del self.active[key]

        return ready_events, ready_obs

    def flush_all(
        self,
    ) -> Tuple[List[my_types.EventRow], List[List[int]]]:

        ready_events: List[my_types.EventRow] = []
        ready_obs: List[List[int]] = []

        for events in self.active.values():

            for ev in events:

                ready_events.append(
                    my_types.EventRow(
                        src_mac=ev.src_mac,
                        seq=ev.seq,
                        type=ev.type,
                        subtype=ev.subtype,
                        dst_mac=ev.dst_mac,
                        bssid=ev.bssid,
                        ssid=ev.ssid,
                        first_time_us=ev.first_time_us,
                        last_time_us=ev.last_time_us,
                        approx_time_us=(
                            ev.first_time_us + ev.last_time_us
                        ) // 2,
                    )
                )

                ready_obs.append(ev.observations)

        self.active.clear()

        return ready_events, ready_obs


def reconstruct_measurement(
    conn: sqlite3.Connection,
    measurement_id: int,
    batch_commit_events: int = 50,
) -> None:

    recon = _EventReconstructor()

    processed_packet_ids: List[int] = []

    event_buffer: List[my_types.EventRow] = []
    obs_buffer: List[List[int]] = []

    for pkt in stream_timed_packets(conn, measurement_id):

        processed_packet_ids.append(pkt["id"])
        recon.process(pkt)
        events, observations = recon.pop_ready()

        if events:
            event_buffer.extend(events)
            obs_buffer.extend(observations)

        if len(event_buffer) >= batch_commit_events:

            event_ids = insert_events(conn, measurement_id, event_buffer)

            link_packets_to_events(conn, event_ids, obs_buffer)

            event_buffer.clear()
            obs_buffer.clear()
            processed_packet_ids.clear()

    events, observations = recon.flush_all()

    event_buffer.extend(events)
    obs_buffer.extend(observations)

    if event_buffer:
        event_ids = insert_events(conn, measurement_id, event_buffer)
        link_packets_to_events(conn, event_ids, obs_buffer)

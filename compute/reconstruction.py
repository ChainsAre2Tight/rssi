from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

import sqlite3

import my_types
from storage import (
    stream_timed_packets,
    insert_events,
    insert_event_packets,
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
    role: str

    first_time_us: int
    last_time_us: int

    packet_ids: List[int] = field(default_factory=list)

    def try_merge(self, pkt: my_types.ID_PACKET) -> bool:

        t = pkt["unix_time_us"]

        new_first = min(self.first_time_us, t)
        new_last = max(self.last_time_us, t)

        if new_last - new_first > MERGE_WINDOW_US:
            return False

        self.first_time_us = new_first
        self.last_time_us = new_last

        self.packet_ids.append(pkt["id"])

        return True


class _EventReconstructor:

    def __init__(self):

        self.active: Dict[
            Tuple[str, int, int, int, str | None, str | None, int, str | None],
            List[_ActiveEvent],
        ] = defaultdict(list)

        self.max_seen_time = 0

    def process(self, pkt: my_types.ID_PACKET) -> None:

        t = pkt["unix_time_us"]

        if t > self.max_seen_time:
            self.max_seen_time = t

        key = (
            pkt["src"],
            pkt["seq"],
            pkt["type"],
            pkt["sub"],
            pkt["dst"],
            pkt["bssid"],
            pkt["ch"],
            pkt["ssid"],
        )

        events = self.active[key]

        for ev in events:
            if ev.try_merge(pkt):
                return

        role = _classify_role(pkt)

        ev = _ActiveEvent(
            src_mac=pkt["src"],
            seq=pkt["seq"],
            type=pkt["type"],
            subtype=pkt["sub"],
            dst_mac=pkt["dst"],
            bssid=pkt["bssid"],
            ssid=pkt["ssid"],
            role=role,
            first_time_us=t,
            last_time_us=t,
        )

        ev.packet_ids.append(pkt["id"])

        events.append(ev)

    def pop_ready(
        self,
    ) -> Tuple[List[my_types.EventRow], List[List[int]]]:

        watermark = self.max_seen_time - REORDER_WINDOW_US

        ready_events: List[my_types.EventRow] = []
        ready_packets: List[List[int]] = []

        for key in list(self.active.keys()):

            events = self.active[key]
            remaining = []

            for ev in events:

                if ev.last_time_us < watermark:

                    ready_events.append(
                        my_types.EventRow(
                            src_mac=ev.src_mac,
                            dst_mac=ev.dst_mac,
                            bssid=ev.bssid,
                            type=ev.type,
                            subtype=ev.subtype,
                            seq=ev.seq,
                            ssid=ev.ssid,
                            role=ev.role,
                            first_time_us=ev.first_time_us,
                            last_time_us=ev.last_time_us,
                            approx_time_us=(
                                ev.first_time_us + ev.last_time_us
                            ) // 2,
                        )
                    )

                    ready_packets.append(ev.packet_ids)

                else:
                    remaining.append(ev)

            if remaining:
                self.active[key] = remaining
            else:
                del self.active[key]

        return ready_events, ready_packets

    def flush_all(
        self,
    ) -> Tuple[List[my_types.EventRow], List[List[int]]]:

        ready_events: List[my_types.EventRow] = []
        ready_packets: List[List[int]] = []

        for events in self.active.values():

            for ev in events:

                ready_events.append(
                    my_types.EventRow(
                        src_mac=ev.src_mac,
                        dst_mac=ev.dst_mac,
                        bssid=ev.bssid,
                        type=ev.type,
                        subtype=ev.subtype,
                        seq=ev.seq,
                        ssid=ev.ssid,
                        role=ev.role,
                        first_time_us=ev.first_time_us,
                        last_time_us=ev.last_time_us,
                        approx_time_us=(
                            ev.first_time_us + ev.last_time_us
                        ) // 2,
                    )
                )

                ready_packets.append(ev.packet_ids)

        self.active.clear()

        return ready_events, ready_packets

def reconstruct_window_packets(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
) -> Tuple[List[my_types.EventRow], List[List[int]]]:

    recon = _EventReconstructor()

    events: List[my_types.EventRow] = []
    packet_links: List[List[int]] = []

    for pkt in stream_timed_packets(
        conn,
        measurement_id,
        start_time_us,
        end_time_us,
    ):
        recon.process(pkt)

        ready_events, ready_packets = recon.pop_ready()

        if ready_events:
            events.extend(ready_events)
            packet_links.extend(ready_packets)

    ready_events, ready_packets = recon.flush_all()

    events.extend(ready_events)
    packet_links.extend(ready_packets)

    return events, packet_links
def _classify_role(pkt: my_types.ID_PACKET) -> str:
    """placeholder"""
    if pkt["src"] == pkt["bssid"]:
        return "ap"
    if pkt["dst"] == pkt["bssid"]:
        return "client"
    return "unknown"

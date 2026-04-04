from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import my_types


MERGE_WINDOW_US = 5_000
REORDER_WINDOW_US = 20_000_000


@dataclass(slots=True)
class _ActiveEvent:
    src_mac: str
    seq: int
    type: int
    subtype: int
    dst_mac: str | None
    bssid: str | None

    first_time_us: int
    last_time_us: int

    observations: List[my_types.ObservationRow] = field(default_factory=list)

    def try_merge(self, pkt: my_types.TimedPacket) -> bool:

        t = pkt.approx_unix_time_us

        new_first = min(self.first_time_us, t)
        new_last = max(self.last_time_us, t)


        if new_last - new_first > MERGE_WINDOW_US:
            return False

        self.first_time_us = new_first
        self.last_time_us = new_last

        self.observations.append(
            my_types.ObservationRow(
                device=pkt.device,
                boot_time_us=pkt.boot_time_us,
                approx_unix_time_us=t,
                rssi=pkt.rssi,
                noise_floor=pkt.noise_floor,
                channel=pkt.channel,
                packet_id=pkt.id,
            )
        )

        return True


class EventReconstructor:

    def __init__(self):

        self.active: Dict[
            Tuple[str, int, int, int],
            List[_ActiveEvent],
        ] = defaultdict(list)

        self.max_seen_time = 0

    def process(self, pkt: my_types.TimedPacket) -> None:

        t = pkt.approx_unix_time_us

        if t > self.max_seen_time:
            self.max_seen_time = t

        key = (pkt.src_mac, pkt.seq, pkt.type, pkt.subtype)

        events = self.active[key]

        for ev in events:
            if ev.try_merge(pkt):
                return

        ev = _ActiveEvent(
            src_mac=pkt.src_mac,
            seq=pkt.seq,
            type=pkt.type,
            subtype=pkt.subtype,
            dst_mac=pkt.dst_mac,
            bssid=pkt.bssid,
            first_time_us=t,
            last_time_us=t,
        )

        ev.observations.append(
            my_types.ObservationRow(
                device=pkt.device,
                boot_time_us=pkt.boot_time_us,
                approx_unix_time_us=t,
                rssi=pkt.rssi,
                noise_floor=pkt.noise_floor,
                channel=pkt.channel,
                packet_id=pkt.id,
            )
        )

        events.append(ev)

    def pop_ready(
        self,
    ) -> Tuple[List[my_types.EventRow], List[List[my_types.ObservationRow]]]:

        watermark = self.max_seen_time - REORDER_WINDOW_US

        ready_events: List[my_types.EventRow] = []
        ready_obs: List[List[my_types.ObservationRow]] = []

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
    ) -> Tuple[List[my_types.EventRow], List[List[my_types.ObservationRow]]]:

        ready_events: List[my_types.EventRow] = []
        ready_obs: List[List[my_types.ObservationRow]] = []

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
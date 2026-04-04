from typing import Dict, List

import my_types

class EventReconstructor:

    def __init__(
        self,
        merge_window_us: int = 20_000,
        reorder_window_us: int = 20_000_000,
    ):
        self.merge_window_us = merge_window_us
        self.reorder_window_us = reorder_window_us

        self.active_events: Dict[my_types.EventKey, List[my_types.ActiveEvent]] = {}

        self.max_seen_time_us: int = 0

        self.ready_events: List[my_types.EventRow] = []
        self.ready_observations: List[my_types.ObservationRow] = []


    def process(self, packet: my_types.TimedPacket) -> None:

        t = packet.approx_unix_time_us

        if t > self.max_seen_time_us:
            self.max_seen_time_us = t

        key: my_types.EventKey = (
            packet.src_mac,
            packet.seq,
            packet.type,
            packet.subtype,
        )

        obs = my_types.ObservationRow(
            device=packet.device,
            boot_time_us=packet.boot_time_us,
            approx_unix_time_us=packet.approx_unix_time_us,
            rssi=packet.rssi,
            noise_floor=packet.noise_floor,
            channel=packet.channel,
            packet_id=packet.id,
        )

        events = self.active_events.get(key)

        if events is None:
            event = self._create_event(packet, obs)
            self.active_events[key] = [event]
        else:
            if not self._try_merge(events, packet, obs):
                event = self._create_event(packet, obs)
                events.append(event)

        self._advance_watermark()

    def pop_ready(self):

        events = self.ready_events
        observations = self.ready_observations

        self.ready_events = []
        self.ready_observations = []

        return events, observations

    def flush_all(self):

        for events in self.active_events.values():
            for event in events:
                self._finalize_event(event)

        self.active_events.clear()

        return self.pop_ready()

    def _create_event(
        self,
        packet: my_types.TimedPacket,
        obs: my_types.ObservationRow
    ) -> my_types.ActiveEvent:

        event = my_types.ActiveEvent(
            src_mac=packet.src_mac,
            dst_mac=packet.dst_mac,
            bssid=packet.bssid,
            type=packet.type,
            subtype=packet.subtype,
            seq=packet.seq,
            first_time_us=packet.approx_unix_time_us,
            last_time_us=packet.approx_unix_time_us,
        )

        event.observations.append(obs)

        return event

    def _try_merge(
        self,
        events: List[my_types.ActiveEvent],
        packet: my_types.TimedPacket,
        obs: my_types.ObservationRow,
    ) -> bool:

        t = packet.approx_unix_time_us

        for event in events:

            new_first = min(event.first_time_us, t)
            new_last = max(event.last_time_us, t)

            if new_last - new_first <= self.merge_window_us:

                event.first_time_us = new_first
                event.last_time_us = new_last
                event.observations.append(obs)

                return True

        return False

    def _advance_watermark(self):

        watermark = self.max_seen_time_us - self.reorder_window_us

        remove_keys = []

        for key, events in self.active_events.items():

            remaining = []

            for event in events:

                if event.last_time_us < watermark:
                    self._finalize_event(event)
                else:
                    remaining.append(event)

            if remaining:
                self.active_events[key] = remaining
            else:
                remove_keys.append(key)

        for key in remove_keys:
            del self.active_events[key]

    def _finalize_event(self, event: my_types.ActiveEvent):

        first = event.first_time_us
        last = event.last_time_us

        approx = (first + last) // 2

        event_row = my_types.EventRow(
            src_mac=event.src_mac,
            dst_mac=event.dst_mac,
            bssid=event.bssid,
            type=event.type,
            subtype=event.subtype,
            seq=event.seq,
            first_time_us=first,
            last_time_us=last,
            approx_time_us=approx,
        )

        self.ready_events.append(event_row)

        self.ready_observations.extend(event.observations)
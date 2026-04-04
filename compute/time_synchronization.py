from typing import List, Dict
from collections import defaultdict
from bisect import bisect_right
from dataclasses import dataclass

import my_types

DEFAULT_CLOCK_SLOPE: float = 1.0

class DeviceTimeMapper:

    def __init__(self, device: str, segments: List[my_types.SyncSegment]):
        self.device = device
        self.segments = segments
        self._starts = [s.boot_start for s in segments]

    def map(self, boot_time_us: int) -> int:

        i = bisect_right(self._starts, boot_time_us) - 1

        if i < 0:
            i = 0

        seg = self.segments[i]

        return int(seg.a * boot_time_us + seg.b)


@dataclass(slots=True)
class MeasurementTimeMapper:
    devices: Dict[str, DeviceTimeMapper]

    def map(self, device: str, boot_time_us: int) -> int:
        mapper = self.devices[device]
        return mapper.map(boot_time_us)


def build_time_mapper(
    sync_rows: List[my_types.TimeSyncRow],
    default_slope: float = DEFAULT_CLOCK_SLOPE,
) -> MeasurementTimeMapper:

    per_device: Dict[str, List[my_types.TimeSyncRow]] = defaultdict(list)

    for row in sync_rows:
        per_device[row.device].append(row)

    devices: Dict[str, DeviceTimeMapper] = {}

    for device, rows in per_device.items():

        rows.sort(key=lambda r: r.boot_time_us)

        segments: List[my_types.SyncSegment] = []

        if len(rows) == 1:

            r = rows[0]

            a = default_slope
            b = r.unix_time_us - a * r.boot_time_us

            segments.append(my_types.SyncSegment(r.boot_time_us, a, b))

        else:

            for i in range(len(rows) - 1):

                r1 = rows[i]
                r2 = rows[i + 1]

                a = (r2.unix_time_us - r1.unix_time_us) / (r2.boot_time_us - r1.boot_time_us)
                b = r1.unix_time_us - a * r1.boot_time_us

                segments.append(my_types.SyncSegment(r1.boot_time_us, a, b))

            # last fallback segment

            last = rows[-1]

            a = default_slope
            b = last.unix_time_us - a * last.boot_time_us

            segments.append(my_types.SyncSegment(last.boot_time_us, a, b))

        devices[device] = DeviceTimeMapper(device, segments)

    return MeasurementTimeMapper(devices)
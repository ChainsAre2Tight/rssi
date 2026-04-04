import typing as t
from dataclasses import dataclass

class PACKET(t.TypedDict):
    boot_time_us: int
    rssi: int
    noise_floor: int
    ch: int
    type: int
    sub: int
    seq: int
    src: str
    dst: str
    bssid: str
    ssid: str

class CSI_PACKET(t.TypedDict):
    boot_time_us: int
    rssi: int
    noise_floor: int
    ch: int
    type: int
    sub: int
    seq: int
    src: str
    dst: str
    bssid: str
    csi: list[int]

class DEVICE(t.TypedDict):
    name: str
    description: str
    gain: int
    mac: str

class TIME_SYNC(t.TypedDict):
    boot_time_us: int
    unix_time: int

@dataclass(slots=True)
class TimeSyncRow:
    device: str
    measurement_id: int
    boot_time_us: int
    unix_time_us: int

@dataclass(slots=True)
class SyncSegment:
    """unix = a * boot + b"""
    boot_start: int
    a: float
    b: float


EventKey = t.Tuple[str, int, int, int]


@dataclass(slots=True)
class TimedPacket:
    id: int
    device: str

    boot_time_us: int
    approx_unix_time_us: int

    rssi: int
    noise_floor: int
    channel: int

    type: int
    subtype: int
    seq: int

    src_mac: str
    dst_mac: str | None
    bssid: str | None


@dataclass(slots=True)
class ObservationRow:
    device: str
    boot_time_us: int
    approx_unix_time_us: int
    rssi: int
    noise_floor: int
    channel: int
    packet_id: int


@dataclass(slots=True)
class EventRow:
    src_mac: str
    dst_mac: str | None
    bssid: str | None

    type: int
    subtype: int
    seq: int

    first_time_us: int
    last_time_us: int
    approx_time_us: int

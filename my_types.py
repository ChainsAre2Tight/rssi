import typing as t
from dataclasses import dataclass
from enum import Enum

class PACKET(t.TypedDict):
    unix_time_us: int
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

class ID_PACKET(PACKET):
    id: int
    device: str

class CSI_PACKET(t.TypedDict):
    unix_time_us: int
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

@dataclass(slots=True)
class EventRow:
    src_mac: str
    dst_mac: str | None
    bssid: str | None

    type: int
    subtype: int
    seq: int
    ssid: str | None
    role: str

    first_time_us: int
    last_time_us: int
    approx_time_us: int

#TODO: fix naming convention
class STAGES(Enum):
    NONE = None
    EVENTS = "reconstructed"
    AP_OBSERVATIONS = "ap_observation"

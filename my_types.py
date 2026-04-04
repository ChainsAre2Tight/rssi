import typing as t

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

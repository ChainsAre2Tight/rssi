import typing as t

class PACKET(t.TypedDict):
    time: int
    rssi: int
    ch: int
    type: int
    sub: int
    seq: int
    src: str
    dst: str
    bssid: str
    ssid: str

class CSI_PACKET(t.TypedDict):
    time: int
    rssi: int
    ch: int
    type: int
    sub: int
    seq: int
    src: str
    dst: str
    bssid: str

class DEVICE(t.TypedDict):
    name: str
    description: str
    gain: int
    mac: str

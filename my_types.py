import typing as t
from dataclasses import dataclass
import config

class BASE_PACKET(t.TypedDict):
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

class PACKET(BASE_PACKET):
    ssid: str

class ID_PACKET(PACKET):
    id: int
    device: str

class CSI_PACKET(BASE_PACKET):
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

@dataclass(frozen=True)
class STAGES:
    NONE = None
    EVENTS: int = 1
    AP_OBSERVATIONS: int = 2
    DETECTION: int = 3

class AGGREGATION_STAGES:
    NONE = None
    DATASET_BUILT = 1

@dataclass(slots=True)
class DetectionSignal:
    observation_id: t.Optional[int]

    bssid: str
    ssid: t.Optional[str]

    detector: str
    signal: str
    severity: str

    metadata_json: t.Optional[str]

@dataclass(slots=True)
class DetectionContext:

    window_id: int
    start_time_us: int
    end_time_us: int

    observation_ids: t.List[int]

    bssid_by_observation: t.Dict[int, str]
    events_by_observation: t.Dict[int, t.List[EventRow]]
    ssids_by_observation: t.Dict[int, t.Set[str]]
    hidden_ssid_observed: t.Dict[int, bool]

    whitelist: dict

@dataclass(slots=True)
class WindowSpec:
    layer: int
    step_us: int
    size_us: int

    depends_on_layer: int | None = None
    depends_on_stage: int | None = None

OBSERVATION_WINDOWS = WindowSpec(
    layer=0,
    step_us=config.WINDOW_STEP_US,
    size_us=config.WINDOW_SIZE_US,
    depends_on_layer=None
)

AGGREGATION_WINDOWS = WindowSpec(
    layer=1,
    step_us=config.WINDOW_STEP_US * 5,
    size_us=config.WINDOW_SIZE_US * 10,
    depends_on_layer=0,
    depends_on_stage=STAGES.AP_OBSERVATIONS,
)

@dataclass(slots=True)
class ObservationRow:
    observation_id: int
    bssid: str


@dataclass(slots=True)
class ObservationCsiLinkRow:
    observation_id: int
    csi_packet_id: int
    role: str


@dataclass(slots=True)
class CsiPacketRow:
    id: int
    device: str
    unix_time_us: int
    rssi: int
    noise_floor: int
    channel: int
    csi: str

@dataclass(slots=True)
class DatasetSample:

    packet_id: int
    timestamp_us: int

    sensor: str
    bssid: str

    channel: int
    rssi: int
    noise_floor: int

    csi: str
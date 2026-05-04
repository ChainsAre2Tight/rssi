import typing as t
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum

import sqlite3

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
    LOCALIZATION_TRIGGER: int = 4

class AGGREGATION_STAGES:
    NONE = None
    FINGERPRINTING = 1
    DISTANCE_CALCULATION = 2
    DECISIONS = 3

@dataclass(slots=True)
class DetectionSignal:
    observation_id: t.Optional[int]

    bssid: str
    ssid: t.Optional[str]

    detector: str
    signal: str
    importance: str # maybe enum?

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


class Importance(str, Enum):

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    WHITELIST = "whitelist"

    @property
    def rank(self) -> int:
        return _IMPORTANCE_RANK[self]

    @classmethod
    def from_str(cls, value: str) -> "Importance":
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Unknown importance: {value}")

_IMPORTANCE_RANK = {
    Importance.WHITELIST: -1,
    Importance.INFO: 0,
    Importance.LOW: 1,
    Importance.MEDIUM: 2,
    Importance.HIGH: 3,
    Importance.CRITICAL: 4,
}

def max_importance(values):
    return max(values, key=lambda v: v.rank)

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

class Incident(ABC):

    @abstractmethod
    def to_dict(self) -> t.Dict[str, t.Any]:
        pass

class Modality(ABC):
    name: str

    @abstractmethod
    def build_incidents(
        self,
        conn: sqlite3.Connection,
        measurement_id: int,
        start_time_us: int,
        end_time_us: int,
    ) -> t.List[Incident]:
        pass

    @abstractmethod
    def enqueue_localization_jobs(
        self,
        conn: sqlite3.Connection,
        measurement_id: int,
        start_time_us: int,
        end_time_us: int,
        bssid: str,
    ) -> dict:
        pass

    @abstractmethod
    def get_localization_report(
        self,
        conn: sqlite3.Connection,
        measurement_id: int,
        start_time_us: int,
        end_time_us: int,
        bssid: str,
    ) -> dict:
        pass

@dataclass(slots=True)
class LogicalSignal(DetectionSignal):
    start_time_us: int
    end_time_us: int

@dataclass(slots=True)
class LogicalWarningOccurrence:
    start_time_us: int
    end_time_us: int


@dataclass(slots=True)
class LogicalWarning:
    detector: str
    signal: str
    importance: Importance
    metadata: t.Dict[str, t.Any]
    occurrences: list[LogicalWarningOccurrence]

@dataclass(slots=True)
class LogicalIncidentGroup:
    bssid: str
    ssid: t.Optional[str]
    first_seen_us: int
    last_seen_us: int
    signal_count: int

@dataclass(slots=True)
class LogicalIncident(Incident):

    bssid: str
    ssid: t.Optional[str]

    importance: Importance

    start_time_us: int
    end_time_us: int

    warnings: list[LogicalWarning]

    def to_dict(self) -> dict:

        return {
            "modality": "logical",
            "identity": {
                "bssid": self.bssid,
                "ssid": self.ssid,
            },
            "importance": self.importance.value,
            "start_time_us": self.start_time_us,
            "end_time_us": self.end_time_us,
            "warnings": [
                {
                    "detector": w.detector,
                    "signal": w.signal,
                    "importance": w.importance.value,
                    "occurrences": [asdict(o) for o in w.occurrences],
                    "metadata": w.metadata,
                }
                for w in self.warnings
            ],
        }

@dataclass(slots=True)
class CalibrationModel:
    devices: list[str]
    positions: dict[str, tuple[float, float, float]]
    gain_models: dict[str, t.Any]   # GainModelInterface
    pt: dict[str, float]            # keep even if unused
    is_calibrated: bool


@dataclass(slots=True)
class LocalizationInput:
    devices: list[str]
    positions: dict[str, tuple[float, float, float]]
    gain_models: dict[str, t.Any]
    rssi_values: dict[str, list[int]]


@dataclass(slots=True)
class LocalizationResult:
    window_id: int
    bssid: str

    start_time_us: int
    end_time_us: int

    estimated_position: tuple[float, float, float]
    estimated_p0: float

    device_count: int
    converged: bool

    metadata: dict[str, t.Any] | None = None

@dataclass(slots=True)
class CSIFingerprint:
    id: int | None
    measurement_id: int
    window_id: int

    bssid: str
    is_reference: bool

    vector: bytes

    sensor_names: list[str]
    metadata: dict

@dataclass(slots=True)
class FingerprintDistance:
    id: int | None
    measurement_id: int
    window_id: int

    bssid: str

    reference_fingerprint_id: int
    fingerprint_id: int

    euclidean_dist: float
    cosine_dist: float

@dataclass(slots=True)
class CSISignal:
    measurement_id: int
    window_id: int
    bssid: str

    detector: str
    signal: str
    importance: str

    metadata_json: t.Optional[str]

@dataclass(slots=True)
class PhysicalSignal:
    bssid: str
    detector: str
    signal: str
    importance: str
    metadata_json: str | None
    start_time_us: int
    end_time_us: int

@dataclass(slots=True)
class PhysicalIncidentGroup:
    bssid: str
    first_seen_us: int
    last_seen_us: int
    signal_count: int

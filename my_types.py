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
    severity: str # maybe enum?

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


class Severity(str, Enum):

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        return _SEVERITY_RANK[self]

    @classmethod
    def from_str(cls, value: str) -> "Severity":
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Unknown severity: {value}")

_SEVERITY_RANK = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}

def max_severity(values):
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

@dataclass(slots=True)
class DatasetDescriptor:

    measurement_id: int
    window_id: int
    version: int = 1

@dataclass(slots=True)
class DatasetMetadata:

    measurement_id: int
    window_id: int

    start_time_us: int
    end_time_us: int

    dataset_version: int
    schema_version: int

    packet_count: int
    sensor_count: int
    ap_count: int

class DatasetWriter(ABC):

    @abstractmethod
    def write_dataset(self, desc: DatasetDescriptor, dataset: dict) -> None:
        pass

    @abstractmethod
    def write_metadata(self, desc: DatasetDescriptor, metadata: DatasetMetadata) -> None:
        pass

    def write(
        self,
        desc: DatasetDescriptor,
        dataset: dict,
        metadata: DatasetMetadata,
    ) -> None:

        self.write_dataset(desc, dataset)
        self.write_metadata(desc, metadata)

class DatasetReader(ABC):

    @abstractmethod
    def read_dataset(self, desc: DatasetDescriptor):
        pass

    @abstractmethod
    def read_metadata(self, desc: DatasetDescriptor):
        pass

    def read(self, desc: DatasetDescriptor):
        dataset = self.read_dataset(desc)
        metadata = self.read_metadata(desc)

        return dataset, metadata

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
        start_time: int,
        end_time: int,
    ) -> t.List[Incident]:
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
    severity: Severity
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

    severity: Severity

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
            "severity": self.severity.value,
            "start_time_us": self.start_time_us,
            "end_time_us": self.end_time_us,
            "warnings": [
                {
                    "detector": w.detector,
                    "signal": w.signal,
                    "severity": w.severity.value,
                    "occurrences": [asdict(o) for o in w.occurrences],
                    "metadada": w.metadata,
                }
                for w in self.warnings
            ],
        }

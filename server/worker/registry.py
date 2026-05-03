from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class WorkerSpec:
    name: str
    module: str
    instances: int = 0


WORKERS: List[WorkerSpec] = [
    WorkerSpec(
        name="reconstruction",
        module="cmd.workers.events",
    ),
    WorkerSpec(
        name="ap_observations",
        module="cmd.workers.aps",
    ),
    WorkerSpec(
        name="detection",
        module="cmd.workers.detection",
    ),
    WorkerSpec(
        name="csi_fingerprinting",
        module="cmd.workers.csi_fingerprint",
    ),
    WorkerSpec(
        name="csi_distance",
        module="cmd.workers.csi_distance",
    ),
    WorkerSpec(
        name="localization trigger",
        module="cmd.workers.localization_trigger",
    ),
    WorkerSpec(
        name="localization computation",
        module="cmd.workers.localization_compute",
        instances=2,
    ),
]
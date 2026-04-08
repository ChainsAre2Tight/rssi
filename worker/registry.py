from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class WorkerSpec:
    name: str
    module: str


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
        name="dataset_builder",
        module="cmd.workers.dataset",
    ),
]
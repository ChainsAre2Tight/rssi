from pathlib import Path
import json
from dataclasses import asdict

import numpy as np

import config
import my_types


def dataset_root() -> Path:
    return Path(config.DATASET_DIR)


def measurement_dir(measurement_id: int) -> Path:
    return dataset_root() / f"measurement_{measurement_id}"


def dataset_file(desc: my_types.DatasetDescriptor) -> Path:
    return (
        measurement_dir(desc.measurement_id)
        / f"dataset_{desc.window_id:06d}_v{desc.version}.npz"
    )

def metadata_file(desc: my_types.DatasetDescriptor) -> Path:
    return (
        measurement_dir(desc.measurement_id)
        / f"dataset_{desc.window_id:06d}_v{desc.version}.meta.json"
    )

class NPZDatasetWriter(my_types.DatasetWriter):

    def write_dataset(
        self,
        desc: my_types.DatasetDescriptor,
        dataset: dict,
    ) -> None:
        path = dataset_file(desc)
        measurement_dir(desc.measurement_id).mkdir(
            parents=True,
            exist_ok=True,
        )
        np.savez_compressed(
            path,
            **dataset,
        )

    def write_metadata(
        self,
        desc: my_types.DatasetDescriptor,
        metadata: my_types.DatasetMetadata,
    ) -> None:

        path = metadata_file(desc)
        with open(path, "w") as f:
            json.dump(asdict(metadata), f, indent=2)

class NPZDatasetReader(my_types.DatasetReader):

    def read_dataset(self, desc: my_types.DatasetDescriptor):
        path = dataset_file(desc)
        return np.load(path)

    def read_metadata(self, desc: my_types.DatasetDescriptor):
        path = metadata_file(desc)
        with open(path) as f:
            data = json.load(f)
        return my_types.DatasetMetadata(**data)

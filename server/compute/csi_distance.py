from abc import ABC

import numpy as np

class ScalerInterface(ABC):
    def transform(self, x: np.ndarray) -> np.ndarray: # type: ignore
        pass

class IdentityScaler(ScalerInterface):
    def transform(self, x: np.ndarray) -> np.ndarray:
        return x

class SimpleStandardScaler(ScalerInterface):
    def __init__(self, mean: np.ndarray, std: np.ndarray):
        self.mean = mean
        self.std = np.where(std == 0, 1.0, std)

    def transform(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.std


def compute_distances(
    ref_vec: np.ndarray,
    test_vec: np.ndarray,
    scaler: ScalerInterface,
):
    ref_vec = scaler.transform(ref_vec)
    test_vec = scaler.transform(test_vec)

    diff = ref_vec - test_vec
    euclidean = np.linalg.norm(diff)

    norm_a = np.linalg.norm(ref_vec)
    norm_b = np.linalg.norm(test_vec)

    if norm_a == 0 or norm_b == 0:
        cosine = 1.0
    else:
        cosine = 1 - (np.dot(ref_vec, test_vec) / (norm_a * norm_b))

    if np.isnan(euclidean) or np.isnan(cosine):
        raise RuntimeError("NaN detected in distance computation")

    return float(euclidean), float(cosine)

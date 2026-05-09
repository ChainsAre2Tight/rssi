import json
from typing import List

import my_types
from detectors.config import DETECTORS


def rank_csi_importance_euclidean(euclidean: float) -> my_types.Importance:
    if euclidean > 500:
        return my_types.Importance.CRITICAL
    if euclidean > 300:
        return my_types.Importance.HIGH
    if euclidean > 150:
        return my_types.Importance.MEDIUM
    if euclidean > 80:
        return my_types.Importance.LOW
    if euclidean > 40:
        return my_types.Importance.INFO
    return my_types.Importance.WHITELIST


def rank_csi_importance_cosine(cosine: float) -> my_types.Importance:
    if cosine > 0.8:
        return my_types.Importance.CRITICAL
    if cosine > 0.5:
        return my_types.Importance.HIGH
    if cosine > 0.3:
        return my_types.Importance.MEDIUM
    if cosine > 0.2:
        return my_types.Importance.LOW
    if cosine > 0.1:
        return my_types.Importance.INFO
    return my_types.Importance.WHITELIST


def rank_csi_importance_power_ratio(power_ratio_db: float) -> my_types.Importance:
    abs_ratio = abs(power_ratio_db)
    if abs_ratio > 6:
        return my_types.Importance.CRITICAL
    if abs_ratio > 4:
        return my_types.Importance.HIGH
    if abs_ratio > 2.5:
        return my_types.Importance.MEDIUM
    if abs_ratio > 1.5:
        return my_types.Importance.LOW
    if abs_ratio > 0.5:
        return my_types.Importance.INFO
    return my_types.Importance.WHITELIST


def CSIDetector(distance: my_types.FingerprintDistance) -> List[my_types.CSISignal]:
    detector_name = DETECTORS.csi_detector.name
    euclidean_spec = DETECTORS.csi_detector.signals.euclidean_distance
    cosine_spec = DETECTORS.csi_detector.signals.cosine_distance
    power_spec = DETECTORS.csi_detector.signals.power_ratio

    # metadata = json.dumps({
    #     "euclidean_dist": distance.euclidean_dist,
    #     "cosine_dist": distance.cosine_dist,
    #     "power_ratio_db": distance.power_ratio_db,
    # })
    metadata = json.dumps({})

    signals = [
        my_types.CSISignal(
            measurement_id=distance.measurement_id,
            window_id=distance.window_id,
            bssid=distance.bssid,
            detector=detector_name,
            signal=euclidean_spec.name,
            importance=rank_csi_importance_euclidean(distance.euclidean_dist),
            metadata_json=metadata,
        ),
        my_types.CSISignal(
            measurement_id=distance.measurement_id,
            window_id=distance.window_id,
            bssid=distance.bssid,
            detector=detector_name,
            signal=cosine_spec.name,
            importance=rank_csi_importance_cosine(distance.cosine_dist),
            metadata_json=metadata,
        ),
        my_types.CSISignal(
            measurement_id=distance.measurement_id,
            window_id=distance.window_id,
            bssid=distance.bssid,
            detector=detector_name,
            signal=power_spec.name,
            importance=rank_csi_importance_power_ratio(distance.power_ratio_db),
            metadata_json=metadata,
        ),
    ]

    return signals

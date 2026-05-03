import json
from typing import List

import my_types
from detectors.config import DETECTORS


def rank_csi_importance_euclidean(
    euclidean=my_types.FingerprintDistance.euclidean_dist,
) -> my_types.Importance:
    
    if euclidean > 10:
        return my_types.Importance.CRITICAL
    if euclidean > 6:
        return my_types.Importance.HIGH
    if euclidean > 4:
        return my_types.Importance.MEDIUM
    if euclidean > 2.5:
        return my_types.Importance.LOW
    if euclidean > 1:
        return my_types.Importance.INFO

    return my_types.Importance.WHITELIST

def rank_csi_importance_cosine(
    cosine=my_types.FingerprintDistance.cosine_dist,
) -> my_types.Importance:
    
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

def CSIDetector(
    distance: my_types.FingerprintDistance
) -> List[my_types.CSISignal]:

    detector_name = DETECTORS.csi_detector.name
    euclidean_spec = DETECTORS.csi_detector.signals.euclidean_distance
    cosine_spec = DETECTORS.csi_detector.signals.cosine_distance

    metadata = json.dumps({"TODO": "add metadata"})
    
    euclidean = my_types.CSISignal(
        measurement_id=distance.measurement_id,
        window_id=distance.window_id,
        bssid=distance.bssid,
        detector=detector_name,
        signal=euclidean_spec.name,
        importance=rank_csi_importance_euclidean(
            euclidean=distance.euclidean_dist,
        ),
        metadata_json=metadata,
    )
    
    cosine = my_types.CSISignal(
        measurement_id=distance.measurement_id,
        window_id=distance.window_id,
        bssid=distance.bssid,
        detector=detector_name,
        signal=cosine_spec.name,
        importance=rank_csi_importance_cosine(
            cosine=distance.cosine_dist,
        ),
        metadata_json=metadata,
    )

    return [euclidean, cosine]


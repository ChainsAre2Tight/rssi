import json

import my_types


def rank_csi_mismatch_importance(
    euclidean=my_types.FingerprintDistance.euclidean_dist,
    cosine=my_types.FingerprintDistance.cosine_dist,
) -> my_types.Importance:
    
    if cosine > 0.8 or euclidean > 10:
        return my_types.Importance.CRITICAL
    if cosine > 0.5 or euclidean > 6:
        return my_types.Importance.HIGH
    if cosine > 0.3 or euclidean > 4:
        return my_types.Importance.MEDIUM
    if cosine > 0.2 or euclidean > 2.5:
        return my_types.Importance.LOW
    if cosine > 0.1 or euclidean > 1:
        return my_types.Importance.INFO

    return my_types.Importance.WHITELIST

def CSIDetector(
    distance: my_types.FingerprintDistance
) -> my_types.CSISignal:
    return my_types.CSISignal(
        measurement_id=distance.measurement_id,
        window_id=distance.window_id,
        bssid=distance.bssid,
        importance=rank_csi_mismatch_importance(
            euclidean=distance.euclidean_dist,
            cosine=distance.cosine_dist,
        ),
        metadata_json=json.dumps({"TODO": "add metadata"})
    )

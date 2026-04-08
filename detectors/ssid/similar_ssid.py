import json
from typing import List
import unicodedata
import difflib

import my_types

from detectors.config import DETECTORS


SIMILARITY_THRESHOLD = 0.8
TYPO_DISTANCE_THRESHOLD = 1
MIN_SSID_LENGTH = 4


def normalize_ssid(ssid: str) -> str:
    return unicodedata.normalize("NFKC", ssid).lower()


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))

    for i, ca in enumerate(a, 1):
        current = [i]

        for j, cb in enumerate(b, 1):
            insert = previous[j] + 1
            delete = current[j - 1] + 1
            replace = previous[j - 1] + (ca != cb)

            current.append(min(insert, delete, replace))

        previous = current

    return previous[-1]


class SSIDSimilarityDetector:

    def run(
        self,
        ctx: my_types.DetectionContext,
    ) -> List[my_types.DetectionSignal]:

        signals: List[my_types.DetectionSignal] = []

        whitelist = ctx.whitelist

        if not whitelist:
            return signals

        whitelist_ssids = list(whitelist.keys())

        detector_name = DETECTORS.ssid_similarity.name
        similar_spec = DETECTORS.ssid_similarity.signals.similar_ssid
        typo_spec = DETECTORS.ssid_similarity.signals.typosquat_ssid

        for obs_id in ctx.observation_ids:

            observed_ssids = ctx.ssids_by_observation.get(obs_id)

            if not observed_ssids:
                continue

            bssid = ctx.bssid_by_observation[obs_id]

            for observed in observed_ssids:

                if observed in whitelist:
                    continue

                if len(observed) < MIN_SSID_LENGTH:
                    continue

                norm_observed = normalize_ssid(observed)

                for target in whitelist_ssids:

                    norm_target = normalize_ssid(target)

                    distance = levenshtein(norm_observed, norm_target)

                    if distance <= TYPO_DISTANCE_THRESHOLD:

                        metadata = json.dumps({
                            "observed_ssid": observed,
                            "similar_to": target,
                            "distance": distance,
                        })

                        signals.append(
                            my_types.DetectionSignal(
                                observation_id=obs_id,
                                bssid=bssid,
                                ssid=observed,
                                detector=detector_name,
                                signal=typo_spec.name,
                                severity=typo_spec.severity,
                                metadata_json=metadata,
                            )
                        )

                        break

                    if norm_target in norm_observed:

                        metadata = json.dumps({
                            "observed_ssid": observed,
                            "similar_to": target,
                            "method": "substring",
                        })

                        signals.append(
                            my_types.DetectionSignal(
                                observation_id=obs_id,
                                bssid=bssid,
                                ssid=observed,
                                detector=detector_name,
                                signal=similar_spec.name,
                                severity=similar_spec.severity,
                                metadata_json=metadata,
                            )
                        )

                        break

                    ratio = difflib.SequenceMatcher(
                        None,
                        norm_observed,
                        norm_target,
                    ).ratio()

                    if ratio >= SIMILARITY_THRESHOLD:

                        metadata = json.dumps({
                            "observed_ssid": observed,
                            "similar_to": target,
                            "similarity": ratio,
                        })

                        signals.append(
                            my_types.DetectionSignal(
                                observation_id=obs_id,
                                bssid=bssid,
                                ssid=observed,
                                detector=detector_name,
                                signal=similar_spec.name,
                                severity=similar_spec.severity,
                                metadata_json=metadata,
                            )
                        )

                        break

        return signals
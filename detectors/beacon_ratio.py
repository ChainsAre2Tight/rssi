import json
import typing as t

import my_types

from detectors.config import DETECTORS


BEACON_TYPE = 0
BEACON_SUBTYPE = 8
DATA_TYPE = 2

MIN_BEACONS_FOR_ANALYSIS = 10
RATIO_THRESHOLD = 20


class BeaconRatioDetector:

    def run(
        self,
        ctx: my_types.DetectionContext,
    ) -> t.List[my_types.DetectionSignal]:

        signals: t.List[my_types.DetectionSignal] = []

        detector_name = DETECTORS.beacon_ratio.name
        beacon_only_spec = DETECTORS.beacon_ratio.signals.beacon_only_ap
        high_ratio_spec = DETECTORS.beacon_ratio.signals.high_beacon_ratio

        for obs_id in ctx.observation_ids:

            events = ctx.events_by_observation.get(obs_id)

            if not events:
                continue

            beacon_count = 0
            data_count = 0

            for event in events:

                # count only AP-originated frames
                if event.role != "ap":
                    continue

                if event.type == BEACON_TYPE and event.subtype == BEACON_SUBTYPE:
                    beacon_count += 1

                elif event.type == DATA_TYPE:
                    data_count += 1

            if beacon_count < MIN_BEACONS_FOR_ANALYSIS:
                continue

            bssid = ctx.bssid_by_observation[obs_id]

            # Case 1: beacon-only AP
            if data_count == 0:

                metadata = json.dumps({
                    "beacon_count": beacon_count,
                    "data_count": data_count,
                })

                signals.append(
                    my_types.DetectionSignal(
                        observation_id=obs_id,
                        bssid=bssid,
                        ssid=None,
                        detector=detector_name,
                        signal=beacon_only_spec.name,
                        severity=beacon_only_spec.severity,
                        metadata_json=metadata,
                    )
                )

                continue

            ratio = beacon_count / data_count

            # Case 2: suspicious ratio
            if ratio >= RATIO_THRESHOLD:

                metadata = json.dumps({
                    "beacon_count": beacon_count,
                    "data_count": data_count,
                    "ratio": ratio,
                })

                signals.append(
                    my_types.DetectionSignal(
                        observation_id=obs_id,
                        bssid=bssid,
                        ssid=None,
                        detector=detector_name,
                        signal=high_ratio_spec.name,
                        severity=high_ratio_spec.severity,
                        metadata_json=metadata,
                    )
                )

        return signals
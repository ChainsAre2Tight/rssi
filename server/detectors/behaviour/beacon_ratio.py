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

            # Count data frames (AP‑originated, any subtype of DATA_TYPE)
            data_count = 0
            # Count beacons per SSID
            beacon_counts: t.Dict[t.Optional[str], int] = {}

            for event in events:
                if event.role != "ap":
                    continue

                if event.type == BEACON_TYPE and event.subtype == BEACON_SUBTYPE:
                    # Use event.ssid (may be None for hidden SSID)
                    ssid = event.ssid
                    beacon_counts[ssid] = beacon_counts.get(ssid, 0) + 1

                elif event.type == DATA_TYPE:
                    data_count += 1

            # If no beacons at all, nothing to analyse
            if not beacon_counts:
                continue

            bssid = ctx.bssid_by_observation[obs_id]

            # Case 1: beacon‑only AP (no data frames at all)
            if data_count == 0:
                for ssid, beacon_count in beacon_counts.items():
                    # Only consider SSIDs with enough beacons
                    if beacon_count < MIN_BEACONS_FOR_ANALYSIS:
                        continue

                    # metadata = json.dumps({
                    #     "beacon_count": beacon_count,
                    #     "data_count": 0,
                    # })
                    metadata = json.dumps({})

                    signals.append(
                        my_types.DetectionSignal(
                            observation_id=obs_id,
                            bssid=bssid,
                            ssid=ssid,          # per SSID signal
                            detector=detector_name,
                            signal=beacon_only_spec.name,
                            importance=beacon_only_spec.importance,
                            metadata_json=metadata,
                        )
                    )
                continue

            # Case 2: AP sends both beacons and data – check ratio per SSID
            for ssid, beacon_count in beacon_counts.items():
                if beacon_count < MIN_BEACONS_FOR_ANALYSIS:
                    continue

                ratio = beacon_count / data_count
                if ratio >= RATIO_THRESHOLD:
                    # metadata = json.dumps({
                    #     "beacon_count": beacon_count,
                    #     "data_count": data_count,
                    #     "ratio": ratio,
                    # })
                    metadata = json.dumps({})

                    signals.append(
                        my_types.DetectionSignal(
                            observation_id=obs_id,
                            bssid=bssid,
                            ssid=ssid,          # per SSID signal
                            detector=detector_name,
                            signal=high_ratio_spec.name,
                            importance=high_ratio_spec.importance,
                            metadata_json=metadata,
                        )
                    )

        return signals
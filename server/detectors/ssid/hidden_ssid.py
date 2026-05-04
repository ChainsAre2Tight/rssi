import json
from typing import List

import my_types

from detectors.config import DETECTORS

# TODO: replace this metric
# maybe later change to some activity derived value but idk
# maube unique client or smth
PERSISTENCE_EVENT_THRESHOLD = 50


class HiddenSSIDDetector:

    def run(
        self,
        ctx: my_types.DetectionContext,
    ) -> List[my_types.DetectionSignal]:

        signals: List[my_types.DetectionSignal] = []

        detector_name = DETECTORS.hidden_ssid.name
        hidden_spec = DETECTORS.hidden_ssid.signals.hidden_ssid # pyright: ignore[reportAttributeAccessIssue]
        persistent_spec = DETECTORS.hidden_ssid.signals.persistent_hidden_ssid # pyright: ignore[reportAttributeAccessIssue]

        for obs_id in ctx.observation_ids:

            hidden_seen = ctx.hidden_ssid_observed.get(obs_id, False)

            if not hidden_seen:
                continue

            revealed_ssids = ctx.ssids_by_observation.get(obs_id)

            if revealed_ssids:
                # SSID eventually revealed
                continue

            bssid = ctx.bssid_by_observation[obs_id]
            events = ctx.events_by_observation.get(obs_id, [])

            # metadata = json.dumps({
            #     "event_count": len(events),
            # })
            metadata = json.dumps({})

            # persistent hidden SSID
            if len(events) >= PERSISTENCE_EVENT_THRESHOLD:

                signals.append(
                    my_types.DetectionSignal(
                        observation_id=obs_id,
                        bssid=bssid,
                        ssid=None,
                        detector=detector_name,
                        signal=persistent_spec.name,
                        importance=persistent_spec.importance,
                        metadata_json=metadata,
                    )
                )

            # basic hidden SSID
            else:

                signals.append(
                    my_types.DetectionSignal(
                        observation_id=obs_id,
                        bssid=bssid,
                        ssid=None,
                        detector=detector_name,
                        signal=hidden_spec.name,
                        importance=hidden_spec.importance,
                        metadata_json=metadata,
                    )
                )

        return signals
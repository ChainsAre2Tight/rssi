import json
from typing import List

from my_types import DetectionSignal, DetectionContext


class TestDetector:

    def run(
        self,
        ctx: DetectionContext,
    ) -> List[DetectionSignal]:

        signals: List[DetectionSignal] = []

        for obs_id in ctx.observation_ids:

            bssid = ctx.bssid_by_observation[obs_id]
            ssids = ctx.ssids_by_observation[obs_id]

            for ssid in ssids:

                if ssid == "123321":

                    signals.append(
                        DetectionSignal(
                            observation_id=obs_id,
                            bssid=bssid,
                            ssid=ssid,
                            detector="test_detector",
                            signal="test_ssid_123321",
                            severity="critical",
                            metadata_json=json.dumps(
                                {"test": "test123321"}
                            ),
                        )
                    )

                elif ssid == "dmitry-moosetop":

                    signals.append(
                        DetectionSignal(
                            observation_id=obs_id,
                            bssid=bssid,
                            ssid=ssid,
                            detector="test_detector",
                            signal="test_ssid_moosetop",
                            severity="info",
                            metadata_json=json.dumps(
                                {"test": "mooooooooooooo"}
                            ),
                        )
                    )

        return signals
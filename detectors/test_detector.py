import json
from typing import List

from my_types import DetectionSignal, DetectionContext
from detectors.config import DETECTORS


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
                            detector=DETECTORS.test.name,
                            signal=DETECTORS.test.signals.test_signal.name,
                            severity=DETECTORS.test.signals.test_signal.severity,
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
                            detector=DETECTORS.test.name,
                            signal=DETECTORS.test.signals.test_signal.name,
                            severity=DETECTORS.test.signals.test_signal.severity,
                            metadata_json=json.dumps(
                                {"test": "mooooooooooooo"}
                            ),
                        )
                    )

        return signals
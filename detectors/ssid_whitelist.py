import json

import my_types
from detectors.config import DETECTORS


class SSIDWhitelistDetector:

    def run(
        self,
        ctx: my_types.DetectionContext,
    ) -> list[my_types.DetectionSignal]:

        signals: list[my_types.DetectionSignal] = []

        whitelist = ctx.whitelist

        if not whitelist:
            return signals

        for obs_id in ctx.observation_ids:

            bssid = ctx.bssid_by_observation[obs_id]
            ssids = ctx.ssids_by_observation[obs_id]

            for ssid in ssids:

                if ssid in whitelist:
                    continue

                signals.append(
                    my_types.DetectionSignal(
                        observation_id=obs_id,
                        bssid=bssid,
                        ssid=ssid,
                        detector=DETECTORS.ssid_whitelist.name,
                        signal=DETECTORS.ssid_whitelist.signals.unauthorized_ssid.name,
                        severity=DETECTORS.ssid_whitelist.signals.unauthorized_ssid.severity,
                        metadata_json=json.dumps({
                            "ssid": ssid
                        }),
                    )
                )

        return signals
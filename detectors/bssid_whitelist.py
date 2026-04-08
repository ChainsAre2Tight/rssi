import json

import my_types

from detectors.config import DETECTORS


class BSSIDWhitelistDetector:

    def run(
        self,
        ctx: my_types.DetectionContext,
    ) -> list[my_types.DetectionSignal]:

        signals: list[my_types.DetectionSignal] = []

        whitelist = ctx.whitelist

        if not whitelist:
            return signals

        spec = DETECTORS.bssid_whitelist.signals.unauthorized_bssid
        detector_name = DETECTORS.bssid_whitelist.name

        for obs_id in ctx.observation_ids:

            bssid = ctx.bssid_by_observation[obs_id]
            ssids = ctx.ssids_by_observation[obs_id]

            for ssid in ssids:

                allowed_bssids = whitelist.get(ssid)

                if allowed_bssids is None:
                    continue

                if bssid in allowed_bssids:
                    continue

                signals.append(
                    my_types.DetectionSignal(
                        observation_id=obs_id,
                        bssid=bssid,
                        ssid=ssid,
                        detector=detector_name,
                        signal=spec.name,
                        severity=spec.severity,
                        metadata_json=json.dumps({
                            "ssid": ssid,
                            "authorized_bssids": allowed_bssids,
                        }),
                    )
                )

        return signals
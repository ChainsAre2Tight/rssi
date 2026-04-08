import json

import my_types


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
                        detector="ssid_whitelist",
                        signal="unauthorized_ssid",
                        severity="low",
                        metadata_json=json.dumps({
                            "ssid": ssid
                        }),
                    )
                )

        return signals
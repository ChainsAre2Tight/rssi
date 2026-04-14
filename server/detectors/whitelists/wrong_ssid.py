import json

import my_types

from detectors.config import DETECTORS


class AuthorizedAPWrongSSIDDetector:

    def run(
        self,
        ctx: my_types.DetectionContext,
    ) -> list[my_types.DetectionSignal]:

        signals: list[my_types.DetectionSignal] = []

        whitelist = ctx.whitelist

        if not whitelist:
            return signals

        spec = DETECTORS.authorized_ap_wrong_ssid.signals.wrong_ssid
        detector_name = DETECTORS.authorized_ap_wrong_ssid.name

        # build reverse whitelist: bssid -> allowed ssids
        bssid_to_ssids: dict[str, set[str]] = {}

        for ssid, bssids in whitelist.items():

            for bssid in bssids:

                if bssid not in bssid_to_ssids:
                    bssid_to_ssids[bssid] = set()

                bssid_to_ssids[bssid].add(ssid)

        for obs_id in ctx.observation_ids:

            bssid = ctx.bssid_by_observation[obs_id]

            allowed_ssids = bssid_to_ssids.get(bssid)

            if not allowed_ssids:
                continue

            observed_ssids = ctx.ssids_by_observation[obs_id]

            for ssid in observed_ssids:

                if ssid in allowed_ssids:
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
                            "allowed_ssids": list(allowed_ssids),
                        }),
                    )
                )

        return signals
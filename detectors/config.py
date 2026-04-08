from dataclasses import dataclass


@dataclass(slots=True)
class SignalSpec:
    name: str
    severity: str

@dataclass(slots=True)
class DetectorSpec:
    name: str
    signals: object




@dataclass(slots=True)
class TestSignals:
    test_signal: SignalSpec


@dataclass(slots=True)
class SSIDWhitelistSignals:
    unauthorized_ssid: SignalSpec


@dataclass(slots=True)
class BSSIDWhitelistSignals:
    unauthorized_bssid: SignalSpec

@dataclass(slots=True)
class AuthorizedAPWrongSSIDSignals:
    wrong_ssid: SignalSpec


@dataclass(slots=True)
class HiddenSSIDSignals:
    hidden_ssid: SignalSpec
    persistent_hidden_ssid: SignalSpec


# @dataclass(slots=True)
# class BeaconRatioSignals:
#     suspicious_beacon_ratio: SignalSpec

@dataclass(slots=True)
class DetectorDefinitions:

    test: DetectorSpec

    ssid_whitelist: DetectorSpec
    bssid_whitelist: DetectorSpec
    authorized_ap_wrong_ssid: DetectorSpec

    hidden_ssid: DetectorSpec
    # beacon_ratio: DetectorSpec

DETECTORS = DetectorDefinitions(

    test=DetectorSpec(
        name="test",
        signals=TestSignals(
            test_signal=SignalSpec(
                name="test_signal",
                severity="info",
            )
        ),
    ),

    ssid_whitelist=DetectorSpec(
        name="ssid_whitelist",
        signals=SSIDWhitelistSignals(
            unauthorized_ssid=SignalSpec(
                name="unauthorized_ssid",
                severity="low",
            )
        ),
    ),

    bssid_whitelist=DetectorSpec(
        name="bssid_whitelist",
        signals=BSSIDWhitelistSignals(
            unauthorized_bssid=SignalSpec(
                name="unauthorized_bssid",
                severity="high",
            )
        ),
    ),

    authorized_ap_wrong_ssid=DetectorSpec(
        name="authorized_ap_wrong_ssid",
        signals=AuthorizedAPWrongSSIDSignals(
            wrong_ssid=SignalSpec(
                name="wrong_ssid",
                severity="high",
            )
        ),
    ),

    hidden_ssid=DetectorSpec(
        name="hidden_ssid",
        signals=HiddenSSIDSignals(
            hidden_ssid=SignalSpec(
                name="hidden_ssid",
                severity="info",
            ),
            persistent_hidden_ssid=SignalSpec(
                name="persistent_hidden_ssid",
                severity="medium",
            ),
        ),
    )

    # beacon_ratio=DetectorSpec(
    #     name="beacon_ratio",
    #     signals=BeaconRatioSignals(
    #         suspicious_beacon_ratio=SignalSpec(
    #             name="suspicious_beacon_ratio",
    #             severity="medium",
    #         )
    #     ),
    # ),
)
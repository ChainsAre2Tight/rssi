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


# @dataclass(slots=True)
# class HiddenSSIDSignals:
#     hidden_network: SignalSpec


# @dataclass(slots=True)
# class BeaconRatioSignals:
#     suspicious_beacon_ratio: SignalSpec

@dataclass(slots=True)
class DetectorDefinitions:

    test: DetectorSpec
    ssid_whitelist: DetectorSpec
    bssid_whitelist: DetectorSpec
    # hidden_ssid: DetectorSpec
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

    # hidden_ssid=DetectorSpec(
    #     name="hidden_ssid",
    #     signals=HiddenSSIDSignals(
    #         hidden_network=SignalSpec(
    #             name="hidden_network",
    #             severity="info",
    #         )
    #     ),
    # ),

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
from dataclasses import dataclass

from my_types import Severity


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


@dataclass(slots=True)
class BeaconRatioSignals:
    beacon_only_ap: SignalSpec
    high_beacon_ratio: SignalSpec

@dataclass(slots=True)
class SSIDSimilaritySignals:
    similar_ssid: SignalSpec
    typosquat_ssid: SignalSpec

@dataclass(slots=True)
class DetectorDefinitions:

    test: DetectorSpec

    ssid_whitelist: DetectorSpec
    bssid_whitelist: DetectorSpec
    authorized_ap_wrong_ssid: DetectorSpec
    hidden_ssid: DetectorSpec
    beacon_ratio: DetectorSpec
    ssid_similarity: DetectorSpec

DETECTORS = DetectorDefinitions(

    test=DetectorSpec(
        name="test",
        signals=TestSignals(
            test_signal=SignalSpec(
                name="test_signal",
                severity=Severity.INFO,
            )
        ),
    ),

    ssid_whitelist=DetectorSpec(
        name="ssid_whitelist",
        signals=SSIDWhitelistSignals(
            unauthorized_ssid=SignalSpec(
                name="unauthorized_ssid",
                severity=Severity.LOW,
            )
        ),
    ),

    bssid_whitelist=DetectorSpec(
        name="bssid_whitelist",
        signals=BSSIDWhitelistSignals(
            unauthorized_bssid=SignalSpec(
                name="unauthorized_bssid",
                severity=Severity.HIGH,
            )
        ),
    ),

    authorized_ap_wrong_ssid=DetectorSpec(
        name="authorized_ap_wrong_ssid",
        signals=AuthorizedAPWrongSSIDSignals(
            wrong_ssid=SignalSpec(
                name="wrong_ssid",
                severity=Severity.HIGH,
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
                severity=Severity.MEDIUM,
            ),
        ),
    ),

    beacon_ratio=DetectorSpec(
        name="beacon_ratio",
        signals=BeaconRatioSignals(
            beacon_only_ap=SignalSpec(
                name="beacon_only_ap",
                severity="info",
            ),
            high_beacon_ratio=SignalSpec(
                name="high_beacon_ratio",
                severity=Severity.MEDIUM,
            ),
        ),
    ),

    ssid_similarity=DetectorSpec(
        name="ssid_similarity",
        signals=SSIDSimilaritySignals(
            similar_ssid=SignalSpec(
                name="similar_ssid",
                severity=Severity.HIGH,
            ),
            typosquat_ssid=SignalSpec(
                name="typosquat_ssid",
                severity=Severity.CRITICAL,
            ),
        ),
    ),
)
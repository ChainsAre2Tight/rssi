from dataclasses import dataclass
import typing as t

from my_types import Importance


@dataclass(slots=True)
class SignalSpec:
    name: str
    importance: t.Optional[str]

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
class AuthorizedWhitelistSignals:
    authorized_ap: SignalSpec

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
class CSIDetectorSignals:
    euclidean_distance: SignalSpec
    cosine_distance: SignalSpec
    power_ratio: SignalSpec

@dataclass(slots=True)
class DetectorDefinitions:

    test: DetectorSpec

    ssid_whitelist: DetectorSpec
    bssid_whitelist: DetectorSpec
    authorized_ap_wrong_ssid: DetectorSpec
    hidden_ssid: DetectorSpec
    beacon_ratio: DetectorSpec
    ssid_similarity: DetectorSpec
    authorized_whitelist: DetectorSpec

    csi_detector: DetectorSpec

DETECTORS = DetectorDefinitions(

    test=DetectorSpec(
        name="test",
        signals=TestSignals(
            test_signal=SignalSpec(
                name="test_signal",
                importance=Importance.INFO,
            )
        ),
    ),

    ssid_whitelist=DetectorSpec(
        name="ssid_whitelist",
        signals=SSIDWhitelistSignals(
            unauthorized_ssid=SignalSpec(
                name="unauthorized_ssid",
                importance=Importance.MEDIUM,
            )
        ),
    ),

    bssid_whitelist=DetectorSpec(
        name="bssid_whitelist",
        signals=BSSIDWhitelistSignals(
            unauthorized_bssid=SignalSpec(
                name="unauthorized_bssid",
                importance=Importance.CRITICAL,
            )
        ),
    ),

    authorized_ap_wrong_ssid=DetectorSpec(
        name="authorized_ap_wrong_ssid",
        signals=AuthorizedAPWrongSSIDSignals(
            wrong_ssid=SignalSpec(
                name="wrong_ssid",
                importance=Importance.HIGH,
            )
        ),
    ),

    hidden_ssid=DetectorSpec(
        name="hidden_ssid",
        signals=HiddenSSIDSignals(
            hidden_ssid=SignalSpec(
                name="hidden_ssid",
                importance="info",
            ),
            persistent_hidden_ssid=SignalSpec(
                name="persistent_hidden_ssid",
                importance=Importance.LOW,
            ),
        ),
    ),

    beacon_ratio=DetectorSpec(
        name="beacon_ratio",
        signals=BeaconRatioSignals(
            beacon_only_ap=SignalSpec(
                name="beacon_only_ap",
                importance=Importance.INFO,
            ),
            high_beacon_ratio=SignalSpec(
                name="high_beacon_ratio",
                importance=Importance.INFO,
            ),
        ),
    ),

    ssid_similarity=DetectorSpec(
        name="ssid_similarity",
        signals=SSIDSimilaritySignals(
            similar_ssid=SignalSpec(
                name="similar_ssid",
                importance=Importance.CRITICAL,
            ),
            typosquat_ssid=SignalSpec(
                name="typosquat_ssid",
                importance=Importance.CRITICAL,
            ),
        ),
    ),

    authorized_whitelist=DetectorSpec(
        name="authorized_whitelist",
        signals=AuthorizedWhitelistSignals(
            authorized_ap=SignalSpec(
                name="authorized_ap",
                importance=Importance.WHITELIST,
            )
        ),
    ),

    csi_detector=DetectorSpec(
        name="csi_detector",
        signals=CSIDetectorSignals(
            euclidean_distance=SignalSpec(
                name="euclidean_distance",
                importance=None, # can be any
            ),
            cosine_distance=SignalSpec(
                name="cosine_distance",
                importance=None, # can be any
            ),
            power_ratio=SignalSpec(
                name="power_ratio",
                importance=None, # can be any
            )
        ),
    ),
)
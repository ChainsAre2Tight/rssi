from detectors.test_detector import TestDetector
from detectors.ssid_whitelist import SSIDWhitelistDetector
from detectors.bssid_whitelist import BSSIDWhitelistDetector
from detectors.wrong_ssid import AuthorizedAPWrongSSIDDetector
from detectors.hidden_ssid import HiddenSSIDDetector

DETECTORS = [
    # testing stuff
    # TestDetector(),

    # whitelist / authorization detectors
    SSIDWhitelistDetector(),            # SSID not present in whitelist
    BSSIDWhitelistDetector(),           # BSSID not authorized for a whitelisted SSID
    AuthorizedAPWrongSSIDDetector(),    # authorized AP broadcasting unexpected SSID

    # SSID visibility detector
    HiddenSSIDDetector(),               # SSID hidden

    # behavior detectors
    # BeaconRatioDetector(),            # beacon/data ratio anomaly

    # impersonation detectors
    # SSIDSimilarityDetector(),         # SSID similar to whitelisted one (evil twin)
]
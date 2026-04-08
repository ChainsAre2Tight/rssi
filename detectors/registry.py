from detectors.test_detector import TestDetector
from detectors.ssid_whitelist import SSIDWhitelistDetector
from detectors.bssid_whitelist import BSSIDWhitelistDetector

DETECTORS = [
    # testing stuff
    # TestDetector(),

    # whitelist / authorization detectors
    SSIDWhitelistDetector(),            # SSID not present in whitelist
    BSSIDWhitelistDetector(),           # BSSID not authorized for a whitelisted SSID
    # AuthorizedAPServingWrongSSID(),   # authorized AP broadcasting unexpected SSID

    # SSID visibility detectors
    # HiddenSSIDDetector(),             # SSID hidden in beacons but revealed elsewhere
    # PersistentHiddenSSIDDetector(),   # AP serving hidden SSID with no reveal

    # behavior detectors
    # BeaconRatioDetector(),            # beacon/data ratio anomaly

    # impersonation detectors
    # SSIDSimilarityDetector(),         # SSID similar to whitelisted one (evil twin)
]
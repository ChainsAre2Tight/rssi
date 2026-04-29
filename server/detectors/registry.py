from detectors.test import TestDetector
from detectors.whitelists import (
    SSIDWhitelistDetector,
    BSSIDWhitelistDetector,
    AuthorizedAPWrongSSIDDetector,
    AuthorizedWhitelistDetector,
)
from detectors.ssid import (
    HiddenSSIDDetector,
    SSIDSimilarityDetector
)
from detectors.behaviour import (
    BeaconRatioDetector,
)

DETECTORS = [
    # TestDetector(),
    SSIDWhitelistDetector(),
    BSSIDWhitelistDetector(),
    AuthorizedWhitelistDetector(),
    AuthorizedAPWrongSSIDDetector(),
    HiddenSSIDDetector(),
    BeaconRatioDetector(),
    SSIDSimilarityDetector(),
]
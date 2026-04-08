from typing import List

from my_types import DetectionSignal, DetectionContext


def run_detectors(
    ctx: DetectionContext,
    detectors,
) -> List[DetectionSignal]:

    signals: List[DetectionSignal] = []

    for detector in detectors:
        signals.extend(detector.run(ctx))

    return signals
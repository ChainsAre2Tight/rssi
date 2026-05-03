from worker.csi_detector import csi_detection_processor
from worker.window_worker import run_window_worker

from config import logger
from my_types import AGGREGATION_WINDOWS, AGGREGATION_STAGES

if __name__ == "__main__":
    logger.info("Starting csi detection worker")

    run_window_worker(
        layer_config=AGGREGATION_WINDOWS,
        required_stage=AGGREGATION_STAGES.DISTANCE_CALCULATION,
        completed_stage=AGGREGATION_STAGES.DECISIONS,
        processor=csi_detection_processor,
        sleep_seconds=30,
    )

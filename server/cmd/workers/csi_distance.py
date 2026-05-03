from worker.csi_distance import csi_distance_processor
from worker.window_worker import run_window_worker

from config import logger
from my_types import AGGREGATION_WINDOWS, AGGREGATION_STAGES

if __name__ == "__main__":
    logger.info("Starting distance worker")

    run_window_worker(
        layer_config=AGGREGATION_WINDOWS,
        required_stage=AGGREGATION_STAGES.FINGERPRINTING,
        completed_stage=AGGREGATION_STAGES.DISTANCE_CALCULATION,
        processor=csi_distance_processor,
        sleep_seconds=30,
    )

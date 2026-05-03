from worker.window_worker import run_window_worker
from worker.csi_fingerprinter import csi_fingerprinter_processor

from config import logger
from my_types import STAGES, AGGREGATION_WINDOWS, AGGREGATION_STAGES

if __name__ == "__main__":
    logger.info("Starting fingerprinting worker")

    run_window_worker(
        layer_config=AGGREGATION_WINDOWS,
        required_stage=AGGREGATION_STAGES.NONE,
        completed_stage=AGGREGATION_STAGES.FINGERPRINTING,
        processor=csi_fingerprinter_processor,
        sleep_seconds=30,
    )

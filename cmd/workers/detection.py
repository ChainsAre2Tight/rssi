from worker.window_worker import run_window_worker
from worker.detection_worker import detection_processor

from config import logger
from my_types import STAGES

if __name__ == "__main__":
    logger.info("Starting detection worker")

    run_window_worker(
        required_stage=STAGES.AP_OBSERVATIONS,
        completed_stage=STAGES.DETECTION,
        processor=detection_processor,
    )
from worker.window_worker import run_window_worker
from worker.reconstruction_worker import reconstruction_processor

from config import logger
from my_types import STAGES

if __name__ == "__main__":
    logger.info("Starting event reconstruction worker")

    run_window_worker(
        required_stage=STAGES.NONE,
        completed_stage=STAGES.EVENTS,
        processor=reconstruction_processor,
    )
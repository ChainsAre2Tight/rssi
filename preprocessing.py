from worker.window_worker import run_window_worker
from worker.reconstruction_worker import reconstruction_processor

from config import logger

if __name__ == "__main__":
    logger.info("Starting reconstruction worker")

    run_window_worker(
        required_stage=None,
        completed_stage="reconstructed",
        processor=reconstruction_processor,
    )
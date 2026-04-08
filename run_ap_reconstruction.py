from worker.window_worker import run_window_worker
from worker.observarion_worker import observation_processor

from config import logger

if __name__ == "__main__":
    logger.info("Starting ap reconstruction worker")

    run_window_worker(
        required_stage="reconstructed",
        completed_stage="ap_observation",
        processor=observation_processor,
    )
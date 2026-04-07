import logging

from worker.window_worker import run_window_worker
from worker.reconstruction_worker import reconstruction_processor

if __name__ == "__main__":
    # todo move to a singleton
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting reconstruction worker")

    run_window_worker(
        required_stage=None,
        completed_stage="reconstructed",
        processor=reconstruction_processor,
    )
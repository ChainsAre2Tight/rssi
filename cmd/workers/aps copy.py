from worker.window_worker import run_window_worker
from worker.dataset_builder import dataset_processor

from config import logger
from my_types import STAGES, AGGREGATION_WINDOWS

if __name__ == "__main__":
    raise NotImplementedError
    logger.info("Starting dataset construction worker")

    run_window_worker(
        layer_config=AGGREGATION_WINDOWS,
        required_stage=None,
        completed_stage=None,
        processor=dataset_processor,
    )
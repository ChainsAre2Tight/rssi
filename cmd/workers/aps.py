from worker.window_worker import run_window_worker
from worker.observarion_worker import observation_processor

from config import logger
from my_types import STAGES, OBSERVATION_WINDOWS

if __name__ == "__main__":
    logger.info("Starting ap reconstruction worker")

    run_window_worker(
        layer_config=OBSERVATION_WINDOWS,
        required_stage=STAGES.EVENTS,
        completed_stage=STAGES.AP_OBSERVATIONS,
        processor=observation_processor,
    )
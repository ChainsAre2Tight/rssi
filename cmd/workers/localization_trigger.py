from worker.window_worker import run_window_worker
from worker.localiaztion_trigger import localization_trigger_processor

from config import logger
from my_types import STAGES, OBSERVATION_WINDOWS

if __name__ == "__main__":
    logger.info("Starting localization trigger worker")

    run_window_worker(
        layer_config=OBSERVATION_WINDOWS,
        required_stage=STAGES.DETECTION,
        completed_stage=STAGES.LOCALIZATION_TRIGGER,
        processor=localization_trigger_processor,
    )

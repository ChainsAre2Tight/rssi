from worker.localization_worker import run_localization_worker

from config import logger

if __name__ == "__main__":
    logger.info("Starting localization worker")

    run_localization_worker()

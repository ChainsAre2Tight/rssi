import sqlite3

from compute.localization import run_localizer
from compute.localization.calibration import calibration_orchestrator
from compute.localization.localization_input_builder import build_localization_input
from config import logger
import my_types
from storage.ap_observations import resolve_observation_id



def localization_orchestrator(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_id: int,
    bssid: str,
) -> None:

    logger.info(f"[localization] start window={window_id} bssid={bssid}")

    try:
        observation_id = resolve_observation_id(conn, window_id, bssid)

        if observation_id is None:
            logger.warning(f"[localization] no observation found")
            return

        calibration_model = calibration_orchestrator(
            conn=conn,
            measurement_id=measurement_id,
            window_id=window_id,
        )

        if calibration_model is None:
            logger.warning(f"[localization] calibration failed")
            return

        loc_input = build_localization_input(
            conn=conn,
            measurement_id=measurement_id,
            window_id=window_id,
            observation_id=observation_id,
            calibration_model=calibration_model,
        )

        if loc_input is None or len(loc_input.devices) < 3:
            logger.warning(f"[localization] insufficient data")
            return

        result_raw = run_localizer(loc_input)

        result = my_types.LocalizationResult(
            window_id=window_id,
            bssid=bssid,
            observation_id=observation_id,
            estimated_position=result_raw["estimated_position"],
            estimated_p0=result_raw["estimated_P0"],
            device_count=len(loc_input.devices),
            converged=result_raw["converged"],
            metadata=None,
        )

        logger.info(f"[localization] done: {result}")
        print(result)

    except Exception as e:
        logger.exception(f"[localization] failed: {e}")

if __name__ == "__main__":
    import storage
    import config

    with storage.Session() as conn:
        localization_orchestrator(
            conn, 
            config.MEASUREMENT_ID, 
            15,
            "A8:E2:91:40:8E:C3",
        )
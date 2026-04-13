import json
import sqlite3
import my_types


def upsert_localization_result(
    conn: sqlite3.Connection,
    result: my_types.LocalizationResult,
    measurement_id: int,
    is_calibrated: bool,
) -> None:

    conn.execute(
        """
        INSERT INTO localization_results (
            measurement_id,
            window_id,
            bssid,
            start_time_us,
            end_time_us,
            x, y, z,
            estimated_p0,
            device_count,
            converged,
            is_calibrated,
            metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(window_id, bssid)
        DO UPDATE SET
            x = excluded.x,
            y = excluded.y,
            z = excluded.z,
            estimated_p0 = excluded.estimated_p0,
            device_count = excluded.device_count,
            converged = excluded.converged,
            is_calibrated = excluded.is_calibrated,
            metadata_json = excluded.metadata_json
        """,
        (
            measurement_id,
            result.window_id,
            result.bssid,
            result.start_time_us,
            result.end_time_us,
            result.estimated_position[0],
            result.estimated_position[1],
            result.estimated_position[2],
            result.estimated_p0,
            result.device_count,
            int(result.converged),
            int(is_calibrated),
            json.dumps(result.metadata) if result.metadata else None,
        ),
    )

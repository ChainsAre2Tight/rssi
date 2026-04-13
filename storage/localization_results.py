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

def load_localization_results(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_ids: list[int],
) -> list[my_types.LocalizationResult]:

    if not window_ids:
        return []

    placeholders = ",".join("?" for _ in window_ids)

    cur = conn.cursor()

    rows = cur.execute(
        f"""
        SELECT
            window_id,
            bssid,
            start_time_us,
            end_time_us,
            x, y, z,
            estimated_p0,
            device_count,
            converged,
            metadata_json
        FROM localization_results
        WHERE
            measurement_id = ?
            AND window_id IN ({placeholders})
        """,
        [measurement_id] + window_ids,
    ).fetchall()

    results = []

    for row in rows:
        results.append(
            my_types.LocalizationResult(
                window_id=row[0],
                bssid=row[1],
                start_time_us=row[2],
                end_time_us=row[3],
                estimated_position=(row[4], row[5], row[6]),
                estimated_p0=row[7],
                device_count=row[8],
                converged=bool(row[9]),
                metadata=None if row[10] is None else json.loads(row[10]),
            )
        )

    return results

from typing import Optional, Tuple
import sqlite3
import time

import config
import my_types

def claim_next_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    layer_config: my_types.WindowSpec,
    required_stage: int | None,
):

    now_us = int(time.time() * 1_000_000)
    ready_threshold = now_us - config.WINDOW_MARGIN_US

    layer = layer_config.layer
    dep_layer = layer_config.depends_on_layer
    dep_stage = layer_config.depends_on_stage

    dependency_sql = ""
    dependency_params = []

    if dep_layer is not None and dep_stage is not None:

        dependency_sql = """
            AND NOT EXISTS (
                SELECT 1
                FROM windows dep
                WHERE
                    dep.measurement_id = windows.measurement_id
                    AND dep.layer = ?
                    AND dep.start_time_us < windows.end_time_us
                    AND dep.end_time_us > windows.start_time_us
                    AND dep.stage < ?
            )
        """

        dependency_params = [dep_layer, dep_stage]

    if required_stage is None:
        stage_sql = "AND windows.stage IS NULL"
        stage_params = []
    else:
        stage_sql = "AND windows.stage = ?"
        stage_params = [required_stage]

    sql = f"""
        UPDATE windows
        SET
            status = 'processing',
            processing_started_at = ?
        WHERE id = (
            SELECT id
            FROM windows
            WHERE
                measurement_id = ?
                AND layer = ?
                {stage_sql}
                AND status = 'pending'
                AND end_time_us <= ?
                {dependency_sql}
            ORDER BY sequence_id
            LIMIT 1
        )
        RETURNING id, start_time_us, end_time_us
    """

    params = (
        [now_us, measurement_id, layer]
        + stage_params
        + [ready_threshold]
        + dependency_params
    )

    row = conn.execute(sql, params).fetchone()

    if row is None:
        return None

    return (
        row["id"],
        row["start_time_us"],
        row["end_time_us"],
    )

def complete_window_stage(
    conn: sqlite3.Connection,
    window_id: int,
    new_stage: int,
) -> None:

    conn.execute(
        """
        UPDATE windows
        SET
            stage = ?,
            status = 'pending',
            processing_started_at = NULL
        WHERE id = ?
        """,
        (new_stage, window_id),
    )


def fail_window(
    conn: sqlite3.Connection,
    window_id: int,
) -> None:

    conn.execute(
        """
        UPDATE windows
        SET
            status = 'failed',
            processing_started_at = NULL
        WHERE id = ?
        """,
        (window_id,),
    )

def get_last_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    layer: int,
) -> Optional[Tuple[int, int]]:

    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT sequence_id, start_time_us
        FROM windows
        WHERE measurement_id = ?
            AND layer = ?
        ORDER BY sequence_id DESC
        LIMIT 1
        """,
        (measurement_id, layer),
    ).fetchone()

    if row is None:
        return None

    return row["sequence_id"], row["start_time_us"]


def insert_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    layer: int,
    sequence_id: int,
    start_time_us: int,
    end_time_us: int,
) -> bool:

    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO windows (
            measurement_id,
            layer,
            sequence_id,
            start_time_us,
            end_time_us
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            measurement_id,
            layer,
            sequence_id,
            start_time_us,
            end_time_us,
        ),
    )

    return cur.rowcount == 1
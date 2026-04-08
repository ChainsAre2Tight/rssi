from typing import Optional, Tuple
import sqlite3
import time

import config

def claim_next_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    layer: int,
    required_stage: str,
):

    now_us = int(time.time() * 1_000_000)
    ready_threshold = now_us - config.WINDOW_MARGIN_US

    if required_stage is None:

        row = conn.execute(
            """
            UPDATE windows
            SET
                status = 'processing',
                processing_started_at = ?
            WHERE id = (
                SELECT id
                FROM windows
                WHERE
                    measurement_id = ?
                    AND stage IS NULL
                    AND layer = ?
                    AND status = 'pending'
                    AND end_time_us <= ?
                ORDER BY sequence_id
                LIMIT 1
            )
            RETURNING id, start_time_us, end_time_us
            """,
            (now_us, measurement_id, layer, ready_threshold),
        ).fetchone()

    else:

        row = conn.execute(
            """
            UPDATE windows
            SET
                status = 'processing',
                processing_started_at = ?
            WHERE id = (
                SELECT id
                FROM windows
                WHERE
                    measurement_id = ?
                    AND stage = ?
                    AND layer = ?
                    AND status = 'pending'
                    AND end_time_us <= ?
                ORDER BY sequence_id
                LIMIT 1
            )
            RETURNING id, start_time_us, end_time_us
            """,
            (now_us, measurement_id, required_stage, layer, ready_threshold),
        ).fetchone()

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
    new_stage: str,
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
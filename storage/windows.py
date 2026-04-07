from typing import Optional, Tuple, List
import sqlite3
import time

def claim_next_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    required_stage: str | None,
) -> Optional[Tuple[int, int, int]]:

    now = int(time.time())

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
                    AND status = 'pending'
                ORDER BY sequence_id
                LIMIT 1
            )
            RETURNING id, start_time_us, end_time_us
            """,
            (now, measurement_id),
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
                    AND status = 'pending'
                ORDER BY sequence_id
                LIMIT 1
            )
            RETURNING id, start_time_us, end_time_us
            """,
            (now, measurement_id, required_stage),
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
) -> Optional[Tuple[int, int]]:

    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT sequence_id, start_time_us
        FROM windows
        WHERE measurement_id = ?
        ORDER BY sequence_id DESC
        LIMIT 1
        """,
        (measurement_id,),
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
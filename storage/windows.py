from typing import List, Optional
import sqlite3


def insert_windows(
    conn: sqlite3.Connection,
    measurement_id: int,
    layer: int,
    windows: List[tuple[int, int, int]],
) -> None:
    """
    Insert processing windows.

    windows = [(sequence_id, start_time_us, end_time_us), ...]
    """

    if not windows:
        return

    values = [
        (
            measurement_id,
            layer,
            seq,
            start,
            end,
            "pending",
        )
        for seq, start, end in windows
    ]

    cur = conn.cursor()

    cur.executemany(
        """
        INSERT OR IGNORE INTO windows (
            measurement_id,
            layer,
            sequence_id,
            start_time_us,
            end_time_us,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        values,
    )


def claim_next_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    layer: int,
    ready_before_us: int,
) -> Optional[int]:
    """
    Claim the next pending window that is ready for processing.

    Returns window_id or None.
    """

    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT id
        FROM windows
        WHERE
            measurement_id = ?
            AND layer = ?
            AND status = 'pending'
            AND end_time_us <= ?
        ORDER BY sequence_id
        LIMIT 1
        """,
        (measurement_id, layer, ready_before_us),
    ).fetchone()

    if row is None:
        return None

    window_id = row["id"]

    cur.execute(
        """
        UPDATE windows
        SET
            status = 'processing',
            processing_started_at = strftime('%s','now') * 1000000
        WHERE id = ?
        """,
        (window_id,),
    )

    return window_id


def mark_window_done(
    conn: sqlite3.Connection,
    window_id: int,
) -> None:

    conn.execute(
        """
        UPDATE windows
        SET status = 'done'
        WHERE id = ?
        """,
        (window_id,),
    )


def mark_window_failed(
    conn: sqlite3.Connection,
    window_id: int,
) -> None:

    conn.execute(
        """
        UPDATE windows
        SET status = 'failed'
        WHERE id = ?
        """,
        (window_id,),
    )


def get_window_bounds(
    conn: sqlite3.Connection,
    window_id: int,
) -> tuple[int, int]:

    row = conn.execute(
        """
        SELECT start_time_us, end_time_us
        FROM windows
        WHERE id = ?
        """,
        (window_id,),
    ).fetchone()

    if row is None:
        raise RuntimeError(f"window {window_id} not found")

    return row["start_time_us"], row["end_time_us"]
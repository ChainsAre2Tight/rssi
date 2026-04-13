import sqlite3

import time


def claim_next_localization_job(
    conn: sqlite3.Connection,
):

    now_us = int(time.time() * 1_000_000)

    row = conn.execute(
        """
        UPDATE localization_jobs
        SET
            status = 'processing',
            processing_started_at = ?
        WHERE id = (
            SELECT id
            FROM localization_jobs
            WHERE status = 'pending'
            ORDER BY id
            LIMIT 1
        )
        RETURNING id, measurement_id, window_id, bssid
        """,
        (now_us,),
    ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "measurement_id": row["measurement_id"],
        "window_id": row["window_id"],
        "bssid": row["bssid"],
    }

def complete_localization_job(
    conn: sqlite3.Connection,
    job_id: int,
) -> None:

    conn.execute(
        """
        UPDATE localization_jobs
        SET
            status = 'done',
            processing_started_at = NULL
        WHERE id = ?
        """,
        (job_id,),
    )

def insert_localization_jobs(
    conn: sqlite3.Connection,
    measurement_id: int,
    jobs: list[tuple[int, str]],  # (window_id, bssid)
) -> int:

    cur = conn.cursor()

    cur.executemany(
        """
        INSERT INTO localization_jobs (
            measurement_id,
            window_id,
            bssid
        )
        VALUES (?, ?, ?)
        """,
        [
            (measurement_id, w, b)
            for (w, b) in jobs
        ],
    )

    return cur.rowcount

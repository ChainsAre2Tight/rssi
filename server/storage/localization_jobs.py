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

def fail_localization_job(
    conn: sqlite3.Connection,
    job_id: int,
) -> None:

    conn.execute(
        """
        UPDATE localization_jobs
        SET
            status = 'failed',
            processing_started_at = NULL
        WHERE id = ?
        """,
        (job_id,),
    )

def insert_localization_jobs(
    conn: sqlite3.Connection,
    measurement_id: int,
    jobs: list[tuple[int, str]],  # (window_id, bssid)
) -> tuple[int, int]:

    if not jobs:
        return 0, 0

    cur = conn.cursor()

    cur.executemany(
        """
        INSERT OR IGNORE INTO localization_jobs (
            measurement_id,
            window_id,
            bssid,
            status
        )
        VALUES (?, ?, ?, 'pending')
        """,
        [(measurement_id, w, b) for (w, b) in jobs],
    )

    inserted = cur.rowcount
    ignored = len(jobs) - inserted

    return inserted, ignored

def count_localization_jobs(
    conn: sqlite3.Connection,
    measurement_id: int,
    window_ids: list[int],
    bssid: str,
) -> dict[str, int]:

    if not window_ids:
        return {"pending": 0, "processing": 0, "done": 0, "error": 0}

    placeholders = ",".join("?" for _ in window_ids)

    cur = conn.cursor()

    rows = cur.execute(
        f"""
        SELECT status, COUNT(*)
        FROM localization_jobs
        WHERE
            measurement_id = ?
            AND window_id IN ({placeholders})
            AND bssid = ?
        GROUP BY status
        """,
        [measurement_id] + window_ids + [bssid,],
    ).fetchall()

    result = {"pending": 0, "processing": 0, "done": 0, "error": 0}

    for status, count in rows:
        result[status] = count

    return result

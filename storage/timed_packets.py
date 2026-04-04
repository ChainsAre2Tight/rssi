import sqlite3
from typing import Iterator

from my_types import TimedPacket
from compute.time_synchronization import MeasurementTimeMapper


def stream_timed_packets(
    conn: sqlite3.Connection,
    measurement_id: int,
    mapper: MeasurementTimeMapper,
    batch_size: int = 1000,
) -> Iterator[TimedPacket]:

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            device,
            boot_time_us,
            rssi,
            noise_floor,
            channel,
            type,
            subtype,
            seq,
            src_mac,
            dst_mac,
            bssid
        FROM packets
        WHERE
            measurement_id = ?
            AND processed = 0
        ORDER BY boot_time_us, device
        """,
        (measurement_id,),
    )

    while True:

        rows = cur.fetchmany(batch_size)

        if not rows:
            break

        for row in rows:

            boot_time = row["boot_time_us"]
            device = str(row["device"])

            mapr = mapper.devices.get(device)

            if mapr is None:
                raise RuntimeError(f"No time sync for device {device}")

            approx_time = mapper.map(device, boot_time)

            yield TimedPacket(
                id=row["id"],
                device=device,
                boot_time_us=boot_time,
                approx_unix_time_us=approx_time,
                rssi=row["rssi"],
                noise_floor=row["noise_floor"],
                channel=row["channel"],
                type=row["type"],
                subtype=row["subtype"],
                seq=row["seq"],
                src_mac=row["src_mac"],
                dst_mac=row["dst_mac"],
                bssid=row["bssid"],
            )
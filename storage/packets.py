from typing import List, Iterator, Tuple
import sqlite3

import storage
import my_types


def insert_packets(conn: sqlite3.Connection, measurement_id: int, device: str, packets: List[my_types.PACKET]):
    values = [
        (
            measurement_id,
            device,
            pkt.get("unix_time_us", 0),
            pkt.get("rssi", 0),
            pkt.get("noise_floor", 0),
            pkt.get("ch", 0),
            pkt.get("type", 0),
            pkt.get("sub", 0),
            pkt.get("seq", 0),
            pkt.get("src", ""),
            pkt.get("dst", ""),
            pkt.get("bssid", ""),
            pkt.get("ssid", "")
        )
        for pkt in packets # probably should sort before inserting, might benchmark later
    ]

    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO packets (
            measurement_id, device, unix_time_us, rssi, noise_floor, channel, type,
            subtype, seq, src_mac, dst_mac, bssid, ssid
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, 
        values,
    )

def insert_csi_packets(conn: sqlite3.Connection, measurement_id: int, device: str, packets: List[my_types.CSI_PACKET]):
    values = [
        (
            measurement_id,
            device,
            pkt.get("unix_time_us", 0),
            pkt.get("rssi", 0),
            pkt.get("noise_floor", 0),
            pkt.get("ch", 0),
            pkt.get("type", 0),
            pkt.get("sub", 0),
            pkt.get("seq", 0),
            pkt.get("src", ""),
            pkt.get("dst", ""),
            pkt.get("bssid", ""),
            ",".join([str(value) for value in pkt.get("csi", [])]),
        )
        for pkt in packets # probably should sort before inserting, might benchmark later
    ]
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO csi_packets (
            measurement_id, device, unix_time_us, rssi, noise_floor, channel, type,
            subtype, seq, src_mac, dst_mac, bssid, csi
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, 
        values,
    )

def stream_timed_packets(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
    batch_size: int = 1000,
) -> Iterator[my_types.ID_PACKET]:

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            device,
            unix_time_us,
            rssi,
            noise_floor,
            channel,
            type,
            subtype,
            seq,
            src_mac,
            dst_mac,
            bssid,
            ssid
        FROM packets
        WHERE
            measurement_id = ?
            AND unix_time_us >= ?
            AND unix_time_us < ?
        ORDER BY unix_time_us, device
        """,
        (measurement_id, start_time_us, end_time_us),
    )

    while True:

        rows = cur.fetchmany(batch_size)

        if not rows:
            break

        for row in rows:
            yield my_types.ID_PACKET(
                id=row["id"],
                device=row["device"],
                unix_time_us=row["unix_time_us"],
                rssi=row["rssi"],
                noise_floor=row["noise_floor"],
                ch=row["channel"],
                type=row["type"],
                sub=row["subtype"],
                seq=row["seq"],
                src=row["src_mac"],
                dst=row["dst_mac"],
                bssid=row["bssid"],
                ssid=row["ssid"],
            )

def link_packets_to_events(
    conn: sqlite3.Connection,
    event_ids: List[int],
    observations_per_event: List[List[int]],
):

    cur = conn.cursor()

    for event_id, packet_ids in zip(event_ids, observations_per_event):

        if not packet_ids:
            continue

        placeholders = ",".join("?" for _ in packet_ids)

        query = f"""
            UPDATE packets
            SET event_id = ?
            WHERE id IN ({placeholders})
        """

        cur.execute(query, [event_id] + packet_ids)

def load_csi_packets_in_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
):
    cur = conn.execute(
        """
        SELECT
            id,
            src_mac AS src,
            dst_mac AS dst,
            bssid
        FROM csi_packets
        WHERE measurement_id = ?
        AND unix_time_us >= ?
        AND unix_time_us < ?
        """,
        (measurement_id, start_time_us, end_time_us),
    )

    return cur.fetchall()

def insert_observation_csi_packets(
    conn: sqlite3.Connection,
    rows: List[Tuple[int, int, str]],
) -> None:

    conn.executemany(
        """
        INSERT INTO observation_csi_packets (
            observation_id,
            csi_packet_id,
            role
        )
        VALUES (?, ?, ?)
        """,
        rows,
    )

def load_csi_packets(
    conn: sqlite3.Connection,
    packet_ids: List[int],
) -> List[my_types.CsiPacketRow]:

    if not packet_ids:
        return []

    placeholders = ",".join("?" for _ in packet_ids)

    cur = conn.execute(
        f"""
        SELECT
            id,
            device,
            unix_time_us,
            rssi,
            noise_floor,
            channel,
            csi
        FROM csi_packets
        WHERE id IN ({placeholders})
        """,
        packet_ids,
    )

    rows = cur.fetchall()

    result: List[my_types.CsiPacketRow] = []

    for row in rows:
        result.append(
            my_types.CsiPacketRow(
                id=row[0],
                device=row[1],
                unix_time_us=row[2],
                rssi=row[3],
                noise_floor=row[4],
                channel=row[5],
                csi=row[6],
            )
        )

    return result

def index_rssi(
        measurement_id: int,
        device: str,
        ssid: str,
    ) -> List[int]:

    with storage.Session() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT rssi
            FROM packets
            WHERE
                measurement_id = ?
                AND device = ?
                AND ssid = ?
        """, (measurement_id, device, ssid))
        rows = cur.fetchall()
        if rows:
            return [row[0] for row in rows]
        return []

def index_devices_by_ssid(
        measurement_id: int,
        ssid: str,
    ) -> List[my_types.DEVICE]:

    with storage.Session() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                packets.device,
                devices.description,
                devices.mac
            FROM packets
                INNER JOIN devices on devices.name = packets.device
            WHERE
                packets.measurement_id = ?
                AND packets.ssid = ?
            GROUP BY packets.device
            HAVING count(1) > 0
        """, (measurement_id, ssid,))
        rows = cur.fetchall()
        if rows:
            return [{
                "name": row[0],
                "description": row[1],
                "mac": row[2],
            } for row in rows]
        return []

def index_other_devices_by_device(
        measurement_id: int,
        device: str,
    ) -> List[my_types.DEVICE]:

    with storage.Session() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                devices.name,
                devices.description,
                devices.mac
            FROM packets
                INNER JOIN devices on devices.mac = packets.src_mac
            WHERE
                packets.measurement_id = ?
                AND packets.device = ? 
            GROUP BY packets.src_mac
            HAVING count(1) > 0
        """, (measurement_id, device,))
        rows = cur.fetchall()
        if rows:
            return [{
                "name": row[0],
                "description": row[1],
                "mac": row[2],
            } for row in rows]
        return []

def index_rssi_by_device_and_mac(
    measurement_id: int,
    device: str,
    src_mac: str,
) -> List[int]:
    with storage.Session() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT rssi
            FROM packets
            WHERE
                measurement_id = ?
                AND device = ?
                AND src_mac = ?
        """, (measurement_id, device, src_mac))
        rows = cur.fetchall()
        if rows:
            return [row[0] for row in rows]
        return []

def get_first_packet_time(
    conn: sqlite3.Connection,
    measurement_id: int,
) -> int | None:

    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT MIN(unix_time_us) AS t
        FROM packets
        WHERE measurement_id = ?
        """,
        (measurement_id,),
    ).fetchone()

    return row["t"]

def get_last_packet_time(
    conn,
    measurement_id,
):

    row = conn.execute(
        """
        SELECT MAX(unix_time_us) AS t
        FROM packets
        WHERE measurement_id = ?
        """,
        (measurement_id,),
    ).fetchone()

    if row is None:
        return None

    return row["t"]


def get_sensor_packets_in_window(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
) -> list[my_types.ID_PACKET]:

    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.device,
            p.unix_time_us,
            p.rssi,
            p.noise_floor,
            p.channel,
            p.type,
            p.subtype,
            p.seq,
            p.src_mac,
            p.dst_mac,
            p.bssid,
            p.ssid
        FROM packets p
        WHERE
            p.measurement_id = ?
            AND p.unix_time_us BETWEEN ? AND ?
            AND p.src_mac IN (SELECT mac FROM devices)
    """, (measurement_id, start_time_us, end_time_us))

    rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "device": row[1],
            "unix_time_us": row[2],
            "rssi": row[3],
            "noise_floor": row[4],
            "ch": row[5],
            "type": row[6],
            "sub": row[7],
            "seq": row[8],
            "src": row[9],
            "dst": row[10],
            "bssid": row[11],
            "ssid": row[12],
        }
        for row in rows
    ]

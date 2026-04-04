from typing import List, Tuple
import sqlite3

import storage
import my_types

def insert_packets(conn: sqlite3.Connection, measurement_id: int, device: str, packets: List[my_types.PACKET]):
    values = [
        (
            measurement_id,
            device,
            pkt.get("boot_time_us", 0),
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
        for pkt in packets
    ]

    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO packets (
            measurement_id, device, boot_time_us, rssi, noise_floor, channel, type,
            subtype, seq, src_mac, dst_mac, bssid, ssid
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, 
        values,
    )

    conn.commit()

def insert_csi_packets(conn: sqlite3.Connection, measurement_id: int, device: str, packets: List[my_types.CSI_PACKET]):
    values = [
        (
            measurement_id,
            device,
            pkt.get("boot_time_us", 0),
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
        for pkt in packets
    ]
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO csi_packets (
            measurement_id, device, boot_time_us, rssi, noise_floor, channel, type,
            subtype, seq, src_mac, dst_mac, bssid, csi
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, 
        values,
    )
    conn.commit()

def index_rssi(
        measurement_id: int,
        device: str,
        ssid: str,
    ) -> List[int]:

    with storage.Connect() as conn:
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

    with storage.Connect() as conn:
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

    with storage.Connect() as conn:
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
    with storage.Connect() as conn:
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

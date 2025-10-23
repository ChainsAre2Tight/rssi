from typing import List, Tuple

import storage
import my_types

def insert_packets(measurement_id: int, device: str, packets: List[my_types.PACKET]):
    values = [
        (
            measurement_id,
            device,
            str(pkt.get("ts", "")),
            pkt.get("rssi", 0),
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
    with storage.Connect() as conn:
        cur = conn.cursor()
        cur.executemany("""
            INSERT INTO packets (
                measurement_id, device, tsf, rssi, channel, type,
                subtype, seq, src_mac, dst_mac, bssid, ssid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

def index_devices(
        measurement_id: int,
        ssid: str,
    ) -> List[Tuple[str, int]]:

        with storage.Connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT packets.device, devices.gain
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
                return [(row[0], int(row[1])) for row in rows]
            return []

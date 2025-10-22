from typing import List

import storage
import my_types

def insert_packets(device: str, packets: List[my_types.PACKET]):
    values = [
        (
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
                device, tsf, rssi, channel, type, subtype, seq,
                src_mac, dst_mac, bssid, ssid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, 
            values,
        )
        conn.commit()

def index_rssi_by_device_and_ssid(
        device: str,
        ssid: str
    ) -> List[int]:

    with storage.Connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT rssi
            FROM packets
            WHERE device == ?
                AND ssid == ?
        """, (device, ssid))
        rows = cur.fetchall()
        if rows:
            return [row[0] for row in rows]
        return []

from typing import Dict, List

from flask import Flask, request, jsonify

import config
import storage

app = Flask(config.NAME)


def init_db():
    with storage.Connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device TEXT,
                tsf TEXT,
                rssi INTEGER,
                channel INTEGER,
                type INTEGER,
                subtype INTEGER,
                seq INTEGER,
                src_mac TEXT,
                dst_mac TEXT,
                bssid TEXT,
                ssid TEXT
            )
        """)
        conn.commit()



@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    if not data:
        return "Invalid JSON", 400

    device = data.get("device", "")
    packets: List[Dict[str, str | int]] = data.get("packets", [])

    if not packets:
        return "No packets", 400

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
            values
        )
        conn.commit()

    print(f"[UPLOAD] Received {len(packets)} packets from {device}")
    return jsonify({"status": "ok", "received": len(packets)}), 200

    
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

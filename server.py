from typing import List

from flask import Flask, request, jsonify

import config
import storage
import my_types

app = Flask(config.NAME)

@app.route("/upload-csi", methods=["POST"])
def upload_csi():
    data = request.get_json()
    if not data:
        print(1, request.data)
        return "Invalid JSON", 400

    device = data.get("device", "")
    packets: List[my_types.CSI_PACKET] = data.get("packets", [])

    if not packets:
        print(2, request.data)
        return "No packets", 400

    with storage.Connect() as conn:
        storage.insert_csi_packets(conn, config.MEASUREMENT_ID, device, packets)

    print(f"[UPLOAD] Received {len(packets)} packets with CSI data from {device}")
    return jsonify({"status": "ok", "received": len(packets)}), 200

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    if not data:
        return "Invalid JSON", 400

    device = data.get("device", "")
    packets: List[my_types.PACKET] = data.get("packets", [])

    if not packets:
        return "No packets", 400

    with storage.Connect() as conn:
        storage.insert_packets(conn, config.MEASUREMENT_ID, device, packets)

    print(f"[UPLOAD] Received {len(packets)} packets from {device}")
    return jsonify({"status": "ok", "received": len(packets)}), 200

@app.route("/sync", methods=["POST"])
def upload_time_sync():
    data = request.get_json()
    if not data:
        print(1, request.data)
        return "Invalid JSON", 400

    device = data.get("device", "")
    boot_time_us = data.get("boot_time_us")
    boot_unix_time = data.get("boot_unix_time")

    if boot_time_us is None or boot_unix_time is None:
        print(2, request.data)
        return "Invalid sync event", 400

    sync_event: my_types.TIME_SYNC = {
        "boot_time_us": boot_time_us,
        "boot_unix_time": boot_unix_time
    }

    with storage.Connect() as conn:
        storage.insert_time_sync(conn, device, sync_event)

    print(f"[SYNC] Received time sync from {device} boot={boot_time_us} unix={boot_unix_time}")
    return jsonify({"status": "ok"}), 200

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

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
        return "Invalid JSON", 400

    device = data.get("device", "")
    packets: List[my_types.CSI_PACKET] = data.get("packets", [])

    if not packets:
        return "No packets", 400

    storage.insert_csi_packets(config.MEASUREMENT_ID, device, packets)

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

    storage.insert_packets(config.MEASUREMENT_ID, device, packets)

    print(f"[UPLOAD] Received {len(packets)} packets from {device}")
    return jsonify({"status": "ok", "received": len(packets)}), 200

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

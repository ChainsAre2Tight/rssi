from typing import List

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

import config
from config import logger
import storage
import my_types

app = Flask(config.NAME)

@app.errorhandler(Exception)
def handle_uncaught_exception(e):
    raw_data = request.get_data(as_text=True)

    if isinstance(e, HTTPException):
        code = e.code
        description = e.description
    else:
        code = 500
        description = "Internal Server Error"

    logger.exception(
        "Unhandled exception",
        extra={
            "path": request.path,
            "method": request.method,
            "query": request.query_string.decode(),
            "request_data": raw_data,
            "status_code": code,
        }
    )

    return jsonify({"error": description}), code

@app.route("/upload-csi", methods=["POST"])
def upload_csi():
    data = request.get_json()
    if not data:
        return "Invalid JSON", 400

    device = data.get("device", "")
    packets: List[my_types.CSI_PACKET] = data.get("packets", [])

    if not packets:
        return "No packets", 400

    with storage.Session() as conn:
        storage.insert_csi_packets(conn, config.MEASUREMENT_ID, device, packets)

    logger.info(f"[UPLOAD] Received {len(packets)} packets with CSI data from {device}")
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

    with storage.Session() as conn:
        storage.insert_packets(conn, config.MEASUREMENT_ID, device, packets)

    print(f"[UPLOAD] Received {len(packets)} packets from {device}")
    return jsonify({"status": "ok", "received": len(packets)}), 200
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

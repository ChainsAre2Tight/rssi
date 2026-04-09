import time
from typing import Dict

import sqlite3
from flask import Flask, request, jsonify

import storage
from compute.modalities import LogicalModality
from storage.measurements import load_measurement_whitelist

import my_types

app = Flask(__name__)

MODALITIES = {
    LogicalModality().name: LogicalModality(),
}

DEFAULT_ACTIVE_OFFSET_S = 300


def api_error(message: str, code: int = 400):
    return jsonify({"error": "invalid_request", "message": message}), code


def parse_int_param(name: str, required: bool = True):
    value = request.args.get(name)
    if value is None:
        if required:
            raise ValueError(f"missing parameter: {name}")
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"invalid integer parameter: {name}")


def resolve_modalities(param: str | None):
    if not param:
        return list(MODALITIES.values())

    names = [n.strip() for n in param.split(",") if n.strip()]
    result = []

    for name in names:
        modality = MODALITIES.get(name)
        if modality is None:
            raise ValueError(f"unknown modality: {name}")
        result.append(modality)

    return result


def generate_report(
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
    modalities: Dict[str, my_types.Modality]
) -> Dict:
    result = {}

    with storage.Session() as conn:
        for modality in modalities:
            incidents = modality.build_incidents(
                conn=conn,
                measurement_id=measurement_id,
                start_time_us=start_time_us,
                end_time_us=end_time_us,
            )

            result[modality.name] = [i.to_dict() for i in incidents]

    return {
        "measurement_id": measurement_id,
        "start_time_us": start_time_us,
        "end_time_us": end_time_us,
        "modalities": result,
    }


@app.route("/api/v1/reports", methods=["GET"])
def reports():
    try:
        measurement_id = parse_int_param("measurement_id")
        start_time_us = parse_int_param("start_time_us")
        end_time_us = parse_int_param("end_time_us")

        if start_time_us >= end_time_us:
            return api_error("start_time_us must be less than end_time_us")

        modalities_param = request.args.get("modalities")
        modalities = resolve_modalities(modalities_param)

        report = generate_report(
            measurement_id=measurement_id,
            start_time_us=start_time_us,
            end_time_us=end_time_us,
            modalities=modalities,
        )

        return jsonify(report)

    except ValueError as e:
        return api_error(str(e))


@app.route("/api/v1/active", methods=["GET"])
def active():
    try:
        measurement_id = parse_int_param("measurement_id")
        offset_s = parse_int_param("offset_s", required=False)

        if offset_s is None:
            offset_s = DEFAULT_ACTIVE_OFFSET_S

        now_us = int(time.time() * 1_000_000)
        start_time_us = now_us - offset_s * 1_000_000
        end_time_us = now_us

        modalities_param = request.args.get("modalities")
        modalities = resolve_modalities(modalities_param)

        report = generate_report(
            measurement_id=measurement_id,
            start_time_us=start_time_us,
            end_time_us=end_time_us,
            modalities=modalities,
        )

        return jsonify(report)

    except ValueError as e:
        return api_error(str(e))


@app.route("/api/v1/whitelist", methods=["GET"])
def whitelist():
    try:
        measurement_id = parse_int_param("measurement_id")

        with storage.Session() as conn:
            whitelist = load_measurement_whitelist(conn, measurement_id)

        return jsonify(
            {
                "measurement_id": measurement_id,
                "whitelist": whitelist,
            }
        )

    except ValueError as e:
        return api_error(str(e))


@app.route("/api/v1/localize", methods=["POST"])
def localize():
    return jsonify({"error": "not_implemented"}), 501


@app.route("/api/v1/localizations", methods=["GET"])
def localizations():
    return jsonify({"error": "not_implemented"}), 501


@app.route("/api/v1/sensors", methods=["GET"])
def sensors():
    return jsonify({"error": "not_implemented"}), 501


@app.route("/api/v1/system/status", methods=["GET"])
def system_status():
    return jsonify({"error": "not_implemented"}), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
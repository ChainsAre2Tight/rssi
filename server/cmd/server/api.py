import time
from typing import Dict, List

import sqlite3
from flask import Flask, request, jsonify

from compute.whitelist import (
    add_whitelist_entry,
    remove_whitelist_entry,
    rename_whitelist_ssid,
)
from storage.positions import (
    update_device_description,
    update_device_position,
)
from storage.detection_signals import delete_signals_for_measurement
from storage.windows import (
    reset_detection_for_measurement,
    reset_csi_measurement,
    reset_localization_for_measurement,
)
import storage
from compute.modalities import LogicalModality, PhysicalModality
from storage.devices import load_sensors_for_measurement
from storage.measurements import list_measurements, load_measurement_whitelist, update_measurement
from storage.csi_fingerprints import reset_fingerprints_for_measurement
from storage.csi_distances import reset_distances_for_measurement
from storage.csi_signals import delete_csi_signals_for_measurement
from storage.localization_jobs import delete_localization_jobs_for_measurement
from storage.localization_results import delete_localization_results_for_measurement

import my_types

app = Flask(__name__)

MODALITIES: dict[str, my_types.Modality] = {
    LogicalModality().name: LogicalModality(),
    PhysicalModality().name: PhysicalModality(),
}

DEFAULT_ACTIVE_OFFSET_S = 300


def api_error(message: str, code: int = 400):
    return jsonify({"error": "invalid_request", "message": message}), code


def parse_int_param(name: str, required: bool = True) -> None | int:
    value = request.args.get(name)
    if value is None:
        if required:
            raise ValueError(f"missing parameter: {name}")
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"invalid integer parameter: {name}")

def parse_str_param(name: str, required: bool = True) -> str | None:
    value = request.args.get(name)
    if value is None or value.strip() == "":
        if required:
            raise ValueError(f"missing parameter: {name}")
        return None
    return value.strip()


def resolve_modalities(param: str | None) -> list[my_types.Modality]:
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

def resolve_single_modality(param: str | None) -> my_types.Modality:
    if not param:
        raise ValueError("missing parameter: modality")

    name = param.strip()

    modality = MODALITIES.get(name)
    if modality is None:
        raise ValueError(f"unknown modality: {name}")

    return modality

def generate_report(
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
    modalities: List[my_types.Modality]
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
        measurement_id: int = parse_int_param("measurement_id") # type: ignore
        start_time_us: int = parse_int_param("start_time_us") # type: ignore
        end_time_us: int = parse_int_param("end_time_us") # type: ignore

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
        measurement_id: int = parse_int_param("measurement_id") # type: ignore
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
        measurement_id: int = parse_int_param("measurement_id") # type: ignore

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


@app.route("/api/v1/whitelist", methods=["POST"])
def whitelist_add():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore
        ssid: str = parse_str_param("ssid") # type: ignore
        bssid = parse_str_param("bssid", required=False)

        with storage.Session() as conn:
            changed, action = add_whitelist_entry(
                conn=conn,
                measurement_id=measurement_id,
                ssid=ssid,
                bssid=bssid,
            )

        return jsonify({
            "status": "ok" if changed else "noop",
            "action": action,
        })

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)


@app.route("/api/v1/whitelist", methods=["DELETE"])
def whitelist_remove():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore
        ssid: str = parse_str_param("ssid") # type: ignore
        bssid = parse_str_param("bssid", required=False)

        remove_empty_ssid = request.args.get("remove_empty_ssid", "true").lower() == "true"

        with storage.Session() as conn:
            changed, action = remove_whitelist_entry(
                conn=conn,
                measurement_id=measurement_id,
                ssid=ssid,
                bssid=bssid,
                remove_empty_ssid=remove_empty_ssid,
            )

        return jsonify({
            "status": "ok" if changed else "noop",
            "action": action,
        })

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)


@app.route("/api/v1/whitelist", methods=["PATCH"])
def whitelist_rename():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore
        ssid: str = parse_str_param("ssid") # type: ignore
        new_ssid: str = parse_str_param("new_ssid") # type: ignore

        with storage.Session() as conn:
            changed, action = rename_whitelist_ssid(
                conn=conn,
                measurement_id=measurement_id,
                ssid=ssid,
                new_ssid=new_ssid,
            )

        return jsonify({
            "status": "ok" if changed else "noop",
            "action": action,
        })

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)


@app.route("/api/v1/localize", methods=["POST"])
def localize():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore
        start_time_us: int = parse_int_param("start_time_us") # type: ignore
        end_time_us: int = parse_int_param("end_time_us") # type: ignore
        bssid: str = parse_str_param("bssid") # type: ignore

        if start_time_us >= end_time_us:
            return api_error("start_time_us must be less than end_time_us")

        modality_param = request.args.get("modality")
        modality = resolve_single_modality(modality_param)

        with storage.Session() as conn:
            stats = modality.enqueue_localization_jobs(
                conn=conn,
                measurement_id=measurement_id,
                start_time_us=start_time_us,
                end_time_us=end_time_us,
                bssid=bssid,
            )

        return jsonify(stats)

    except ValueError as e:
        return api_error(str(e))


@app.route("/api/v1/localizations", methods=["GET"])
def localizations():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore
        start_time_us:int = parse_int_param("start_time_us") # type: ignore
        end_time_us:int = parse_int_param("end_time_us") # type: ignore
        bssid: str = parse_str_param("bssid") # type: ignore

        if start_time_us >= end_time_us:
            return api_error("start_time_us must be less than end_time_us")

        modality_param = request.args.get("modality")
        modality = resolve_single_modality(modality_param)

        with storage.Session() as conn:
            report = modality.get_localization_report(
                conn=conn,
                measurement_id=measurement_id,
                start_time_us=start_time_us,
                end_time_us=end_time_us,
                bssid=bssid,
            )

        return jsonify(report)

    except ValueError as e:
        return api_error(str(e))

@app.route("/api/v1/localizations", methods=["DELETE"])
def reset_localizations():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore

        with storage.Session() as conn:
            with storage.Transaction(conn) as t:
                delete_localization_jobs_for_measurement(t, measurement_id)
                delete_localization_results_for_measurement(t, measurement_id)
                reset_localization_for_measurement(t, measurement_id)

        return jsonify({
            "status": "ok",
        })

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)


@app.route("/api/v1/sensors", methods=["GET"])
def sensors():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore

        with storage.Session() as conn:
            sensors = load_sensors_for_measurement(
                conn,
                measurement_id,
            )

        return jsonify({
            "measurement_id": measurement_id,
            "sensors": sensors,
        })

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)

@app.route("/api/v1/sensors", methods=["PATCH"])
def patch_sensors():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore
        sensor: str = parse_str_param("device") # type: ignore
        description: str = parse_str_param("description", required=False) # type: ignore
        x: int = parse_int_param("x", required=False) # type: ignore
        y: int = parse_int_param("y", required=False) # type: ignore
        z: int = parse_int_param("z", required=False) # type: ignore

        res = {}

        with storage.Session() as conn:
            with storage.Transaction(conn) as t:
                if description is not None:
                    update_device_description(
                        t,
                        measurement_id,
                        sensor,
                        description,
                    )
                    res["updated_description"] = True

                if x is not None and y is not None and z is not None:
                    update_device_position(
                        t,
                        measurement_id,
                        sensor,
                        x, y, z,
                    )
                    res["updated_positions"] = True
            
        if len(res.keys()) > 0:
            res["status"] = "ok"
        else:
            res["status"] = "noop"
        
        return jsonify(res)

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)


@app.route("/api/v1/system/status", methods=["GET"])
def system_status():
    return jsonify({"error": "not_implemented"}), 501


@app.route("/api/v1/measurements", methods=["GET"])
def measurements():
    try:
        with storage.Session() as conn:
            result = list_measurements(conn)

        return jsonify({
            "measurements": result
        })

    except Exception as e:
        return api_error(str(e), 500)

def validate_measurement_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError("name must be a string")
    name = name.strip()
    if not name:
        raise ValueError("name cannot be empty")
    return name


def validate_measurement_description(description: str | None) -> str | None:
    if description is None:
        return None
    if not isinstance(description, str):
        raise ValueError("description must be a string")
    return description.strip()

@app.route("/api/v1/measurements", methods=["PATCH"])
def update_measurement_api():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore

        name = parse_str_param("name", required=False)
        description = parse_str_param("description", required=False)

        if name is None and description is None:
            return api_error("at least one of name or description must be provided")

        if name is not None:
            name = validate_measurement_name(name)

        if description is not None:
            description = validate_measurement_description(description)

        with storage.Session() as conn:
            changed, action, measurement = update_measurement(
                conn=conn,
                measurement_id=measurement_id,
                name=name,
                description=description,
            )

        if measurement is None:
            return jsonify({
                "status": "noop",
                "action": action,
            })

        return jsonify({
            "status": "ok" if changed else "noop",
            "action": action,
            "measurement": measurement,
        })

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)

@app.route("/api/v1/detection", methods=["DELETE"])
def reset_detection():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore

        with storage.Session() as conn:
            with storage.Transaction(conn) as t:
                delete_signals_for_measurement(t, measurement_id)
                reset_detection_for_measurement(t, measurement_id)

        return jsonify({
            "status": "ok",
        })

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)

@app.route("/api/v1/csi", methods=["DELETE"])
def reset_csi_detection():
    try:
        measurement_id: int = parse_int_param("measurement_id") # type: ignore

        with storage.Session() as conn:
            with storage.Transaction(conn) as t:
                reset_fingerprints_for_measurement(t, measurement_id)
                reset_distances_for_measurement(t, measurement_id)
                delete_csi_signals_for_measurement(t, measurement_id)
                reset_csi_measurement(t, measurement_id)

        return jsonify({
            "status": "ok",
        })

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_error(str(e), 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

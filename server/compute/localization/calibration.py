import sqlite3

from compute.calc_gain import calibrate_devices
import my_types

from my_types import DEVICE, ID_PACKET
from config import logger
from storage.devices import get_all_devices, get_device_positions
from storage.packets import get_sensor_packets_in_window


def build_calibration_dataset(
    devices: list[DEVICE],
    positions: dict[str, tuple[float, float, float]],
    packets: list[ID_PACKET],
) -> dict:

    logger.debug(f"[calibration] building dataset from {len(packets)} packets")

    mac_to_name = {d["mac"]: d["name"] for d in devices}

    # init structure
    data: dict = {}

    for d in devices:
        name = d["name"]
        data[name] = {
            "position": positions.get(name, (0.0, 0.0, 0.0)),
            "rssi": {}
        }

    # fill
    used_links = 0

    for pkt in packets:
        receiver = pkt["device"]
        sender_mac = pkt["src"]

        sender = mac_to_name.get(sender_mac)
        if sender is None:
            continue

        if sender == receiver:
            continue

        if sender not in data[receiver]["rssi"]:
            data[receiver]["rssi"][sender] = []

        data[receiver]["rssi"][sender].append(pkt["rssi"])
        used_links += 1

    logger.debug(f"[calibration] built {used_links} sensor-sensor links")

    return data


def run_calibration(
    conn: sqlite3.Connection,
    measurement_id: int,
    start_time_us: int,
    end_time_us: int,
) -> my_types.CalibrationModel:

    logger.info(f"[calibration] start measurement={measurement_id} "
                f"window=({start_time_us}, {end_time_us})")

    devices = get_all_devices(conn)
    positions = get_device_positions(conn, measurement_id)

    packets = get_sensor_packets_in_window(
        conn,
        measurement_id,
        start_time_us,
        end_time_us,
    )

    if not packets:
        logger.warning("[calibration] no packets in window")

    dataset = build_calibration_dataset(
        devices,
        positions,
        packets,
    )

    try:
        model_raw = calibrate_devices(dataset)

    except Exception as e:
        logger.exception("[calibration] calibration failed")
        raise

    model = my_types.CalibrationModel(
        devices=model_raw["devices"],
        positions={
            dev: dataset[dev]["position"]
            for dev in model_raw["devices"]
        },
        gain_models=model_raw["GainModels"],
        pt=model_raw["Pt"],
        is_calibrated=model_raw["is_calibrated"]
    )

    logger.info(f"[calibration] done, devices={len(model.devices)}")

    return model

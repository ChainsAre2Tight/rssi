import numpy as np

import storage.packets, storage.positions
import config

devices = ["ESP32_01", "ESP32_02", "ESP32_03"]
base_position = np.array(storage.positions.get_device_position(
        config.VIZ_MEASUREMENT_ID,
        "dmitry-moosetop",
    ))

def data(
        measurement_id: int = config.VIZ_MEASUREMENT_ID,
        ssid: str = config.VIZ_SSID
    ) -> dict:
    out = {}
    
    # data = {
    #     "A": {"position": (0,0,0), "rssi": {"B":[-60,-61], "C":[-58]}},
    #     "B": {"position": (1,0,0), "rssi": {"A":[-62], "C":[-59]}},
    #     "C": {"position": (0.5,1,0), "rssi": {"A":[-57], "B":[-60]}}
    # }

    all_devices_that_found_a_network = [
        device
        for device in storage.packets.index_devices_by_ssid(
            measurement_id,
            ssid,
        )
        # if device["name"] in devices
    ]

    for device in all_devices_that_found_a_network:
        out[device["name"]] = {}
        out[device["name"]]["position"] = storage.positions.get_device_position(
            measurement_id,
            device["name"]
        )
        out[device["name"]]["rssi"] = {}
        # print(a_device_that_found_a_network)
        other_devices = [
            other
            for other in storage.packets.index_other_devices_by_device(
                measurement_id,
                device["name"],
            )
            if other["name"] in [d["name"] for d in all_devices_that_found_a_network]
        ]
        # print(other_devices_that_see_this_one)

        for other_device in other_devices:
            rssi = storage.packets.index_rssi_by_device_and_mac(
                measurement_id,
                device['name'],
                other_device["mac"],
            )

            out[device["name"]]["rssi"][other_device["name"]] = rssi

            # print(f"{a_device_that_found_a_network['name']} -> {other_device["name"]}")
            # rssi = np.array(rssi)
            # print(rssi)
            # print("Mean:\t", np.mean(rssi))
            # print("Avg:\t", np.average(rssi))
            # print("Var:\t:", np.var(rssi))
            # print("Max:\t:", np.max(rssi))
            # print("Min:\t:", np.min(rssi))
    return out

if __name__ == "__main__":
    print(data())
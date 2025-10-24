import numpy as np

import storage.packets, storage.positions
import config

devices = ["ESP32_02", "ESP32_03"]
data = {}

base_position = np.array(storage.positions.get_device_position(
    config.VIZ_MEASUREMENT_ID,
    "dmitry-moosetop",
))

# data = {
#     "A": {"position": (0,0,0), "rssi": {"B":[-60,-61], "C":[-58]}},
#     "B": {"position": (1,0,0), "rssi": {"A":[-62], "C":[-59]}},
#     "C": {"position": (0.5,1,0), "rssi": {"A":[-57], "B":[-60]}}
# }

all_devices_that_found_a_network = [
    device
    for device in storage.packets.index_devices_by_ssid(
        config.VIZ_MEASUREMENT_ID,
        config.VIZ_SSID,
    )
    # if device["name"] in devices
]

for device in all_devices_that_found_a_network:
    data[device["name"]] = {}
    data[device["name"]]["position"] = storage.positions.get_device_position(
        config.MEASUREMENT_ID,
        device["name"]
    )
    data[device["name"]]["rssi"] = {}
    # print(a_device_that_found_a_network)
    other_devices = [
        other
        for other in storage.packets.index_other_devices_by_device(
            config.VIZ_MEASUREMENT_ID,
            device["name"],
        )
        if other["name"] in [d["name"] for d in all_devices_that_found_a_network]
    ]
    # print(other_devices_that_see_this_one)

    for other_device in other_devices:
        rssi = storage.packets.index_rssi_by_device_and_mac(
            config.VIZ_MEASUREMENT_ID,
            device['name'],
            other_device["mac"],
        )

        data[device["name"]]["rssi"][other_device["name"]] = rssi

        # print(f"{a_device_that_found_a_network['name']} -> {other_device["name"]}")
        # rssi = np.array(rssi)
        # print(rssi)
        # print("Mean:\t", np.mean(rssi))
        # print("Avg:\t", np.average(rssi))
        # print("Var:\t:", np.var(rssi))
        # print("Max:\t:", np.max(rssi))
        # print("Min:\t:", np.min(rssi))

if __name__ == "__main__":
    print(data)
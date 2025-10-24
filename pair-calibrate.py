import numpy as np

import storage.packets
import config

devices = ["ESP32_02", "ESP32_03"]

all_devices_that_found_a_network = [
    device
    for device in storage.packets.index_devices_by_ssid(
        config.VIZ_MEASUREMENT_ID,
        config.VIZ_SSID,
    )
    if device["name"] in devices
]

for a_device_that_found_a_network in all_devices_that_found_a_network:
    # print(a_device_that_found_a_network)
    other_devices_that_see_this_one = [
        other
        for other in storage.packets.index_other_devices_by_device(
            config.VIZ_MEASUREMENT_ID,
            a_device_that_found_a_network["name"],
        )
        if other["name"] in [d["name"] for d in all_devices_that_found_a_network]
    ]
    # print(other_devices_that_see_this_one)

    for other_device in other_devices_that_see_this_one:
        rssi = storage.packets.index_rssi_by_device_and_mac(
            config.VIZ_MEASUREMENT_ID,
            a_device_that_found_a_network['name'],
            other_device["mac"],
        )

        print(f"{a_device_that_found_a_network['name']} -> {other_device["name"]}")
        rssi = np.array(rssi)
        print(rssi)
        print("Mean:\t", np.mean(rssi))
        print("Avg:\t", np.average(rssi))
        print("Var:\t:", np.var(rssi))
        print("Max:\t:", np.max(rssi))
        print("Min:\t:", np.min(rssi))
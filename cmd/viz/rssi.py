import numpy as np

import storage.packets

test = 3


for device in storage.packets.index_devices_by_ssid(test, "dmitry-moosetop"):
    a = storage.packets.index_rssi(test, device[0], "dmitry-moosetop")
    rssi = np.array(a) + device[1]
    # print(rssi)
    print(device[0])
    print("Mean:\t", np.mean(rssi))
    print("Avg:\t", np.average(rssi))
    print("Var:\t:", np.var(rssi))
    print("Max:\t:", np.max(rssi))
    print("Min:\t:", np.min(rssi))
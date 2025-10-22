import numpy as np

import storage.packets

a = storage.packets.index_rssi_by_device_and_ssid("ESP32_01", "Beeline_2G_F29921")
rssi = np.array(a)
print(rssi)
print(np.mean(rssi))
print(np.average(rssi))
print(np.var(rssi))
print(np.max(rssi))
print(np.min(rssi))
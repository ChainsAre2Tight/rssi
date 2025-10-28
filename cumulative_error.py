import numpy as np
from viz_skibidi import RSSILocalizer, Config
from pair_calibrate import data, base_position
from calc_gain import calibrate_devices
from storage.packets import index_rssi
import storage.positions
import config


def error_one(measurement_id: int, ssid: str):
    d = data(measurement_id, ssid)
    # print(d)
    model = calibrate_devices(
        d,
        config.PATH_LOSS_EXPONENT,
        config.ESP32_SIGNAL_STRENGTH
    )

    model["rssi_values"] = {}
    model["positions"] = {}

    for dev in model["devices"]:
        model["positions"][dev] = d[dev]["position"]
        model["rssi_values"][dev] = index_rssi(
            measurement_id,
            dev,
            ssid,
        )

    # print(model)

    # true source and Pt
    x_true = np.array([0.3, -0.2, 0.1])
    P0_true = -50.0  # dB (arbitrary)
    n_true = config.PATH_LOSS_EXPONENT
    d0 = 1.0

    # build config
    cfg = Config(n=n_true, d0=d0, h_G=1e-3, d_min=1e-2, p0_bounds=(-100, -30),
                tol=1e-8, max_iter=200, aggregate_rssi="median", compute_covariance=False)

    # create localizer and run
    localizer = RSSILocalizer(devices=model["devices"], GainModels=model["GainModels"],
                            rssi_values=model["rssi_values"], positions=model["positions"], config=cfg)

    # out = localizer.localize(verbose=True, return_full=False)
    true_pos = storage.positions.get_device_position(
        measurement_id,
        ssid,
    )
    out = localizer.localize(verbose=False, return_full=False)["estimated_position"]
    return np.linalg.norm(np.array(true_pos)-np.array(out))

if __name__ == "__main__":
    s = []
    for i in range(7, 11):
        for ssid in ["dmitry-moosetop", "Leather club", "Leather Club Mini"]:
            s.append(error_one(i, ssid))
    
    s1 = np.array(s)
    print(sum(s), np.mean(s1), np.median(s1), np.var(s1))
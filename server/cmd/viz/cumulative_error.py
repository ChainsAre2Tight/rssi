import numpy as np
from cmd.viz.viz_skibidi import RSSILocalizer, Config
from compute.pair_calibrate import data, base_position
from compute.calc_gain import calibrate_devices
from compute.bbox import compute_bounding_box_center, angular_error
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

    bbox = compute_bounding_box_center(d)

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
    deviation = np.linalg.norm(np.array(true_pos)-np.array(out))
    angle = np.degrees(angular_error(bbox, true_pos, out))
    print(f"{measurement_id},\t{ssid:.12},\t{true_pos[0]:.1f},\t{true_pos[1]:.1f},\t{true_pos[2]:.1f},\t{out[0]:.1f},\t{out[1]:.1f},\t{out[2]:.1f},\t{deviation:.1f},\t{angle:.1f}")
    return deviation, angle

if __name__ == "__main__":
    print("MeasID,\tSSID,\t\tTrueX,\tTrueY,\tTrueZ,\tLocX,\tLocY,\tLocZ,\tDiff(m),\tAngle,\t")
    s = []
    for i in range(5, 13):
        for ssid in ["dmitry-moosetop", "Leather club", "Leather Club Mini"]:
            s.append(error_one(i, ssid))
    
    s1 = np.array(s)
    print(f'Strength: {config.ESP32_SIGNAL_STRENGTH}, N: {config.PATH_LOSS_EXPONENT}')
    print(f'Name\tMean\tMedian\tVar\tMin\tMax')
    print(f'Dist\t{np.mean(s1[:, 0]):.2f}\t{np.median(s1[:, 0]):.2f}\t{np.var(s1[:, 0]):.2f}\t{np.min(s1[:, 0]):.2f}\t{np.max(s1[:, 0]):.2f}')
    print(f'Theta\t{np.mean(s1[:, 1]):.2f}\t{np.median(s1[:, 1]):.2f}\t{np.var(s1[:, 1]):.2f}\t{np.min(s1[:, 1]):.2f}\t{np.max(s1[:, 1]):.2f}')
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import least_squares

# ============================================================
# 1️⃣   Расчёт вспомогательных геометрических параметров
# ============================================================
def spherical_angles(vec):
    """Преобразование векторного направления в сферические координаты (θ, φ)"""
    x, y, z = vec
    r = np.linalg.norm(vec)
    theta = np.arccos(z / r) if r > 0 else 0.0     # полярный угол [0, π]
    phi = np.arctan2(y, x)                         # азимут [-π, π]
    return theta, phi

def path_loss(d, n=2.0, PL0=-40, d0=1.0):
    """Модель затухания (логарифмическая)"""
    return PL0 + 10 * n * np.log10(d / d0)

# ============================================================
# 2️⃣   RBF-модель диаграммы направленности
# ============================================================
class GainRBF:
    def __init__(self, sigma=np.deg2rad(40), G0=0.0):
        self.sigma = sigma
        self.G0 = G0
        self.centers = None
        self.weights = None

    def fit(self, dirs, gains, lambda_reg=0.1):
        """dirs — массив углов [N,2]: (theta,phi), gains — [N]"""
        self.centers = dirs
        D = cdist(dirs, dirs, metric='euclidean')
        K = np.exp(-(D**2) / (2 * self.sigma**2))
        K_reg = K + lambda_reg * np.eye(len(K))
        # g1 = np.median(gains)
        self.weights = np.linalg.solve(K_reg, gains - self.G0)

    def predict(self, dirs):
        """Оценка усиления в направлениях dirs [M,2]"""
        if self.centers is None:
            return np.full(len(dirs), self.G0)
        D = cdist(dirs, self.centers, metric='euclidean')
        K = np.exp(-(D**2) / (2 * self.sigma**2))
        return self.G0 + K @ self.weights

    def gain(self, direction_vec):
        """Возвращает усиление в направлении (x,y,z)"""
        theta, phi = spherical_angles(direction_vec)
        return float(self.predict(np.array([[theta, phi]])))

# ============================================================
# 3️⃣   Основная оптимизация
# ============================================================
def calibrate_devices(data_dict, n_pathloss=2.0, K=0.0):
    devices = list(data_dict.keys())
    N = len(devices)

    # Индексация устройств
    idx = {dev: i for i, dev in enumerate(devices)}

    # Сбор всех измерений
    meas = []
    for i, dev_i in enumerate(devices):
        pos_i = np.array(data_dict[dev_i]["position"])
        for dev_j, rssi_list in data_dict[dev_i]["rssi"].items():
            if dev_j == dev_i or len(rssi_list) == 0:
                continue
            pos_j = np.array(data_dict[dev_j]["position"])
            d = np.linalg.norm(pos_j - pos_i)
            theta_ij, phi_ij = spherical_angles(pos_j - pos_i)
            theta_ji, phi_ji = spherical_angles(pos_i - pos_j)
            rssi_mean = np.mean(rssi_list)
            meas.append({
                "i": i, "j": idx[dev_j], "rssi": rssi_mean,
                "d": d, "angles_ij": (theta_ij, phi_ij),
                "angles_ji": (theta_ji, phi_ji)
            })

    # Инициализация параметров
    Pt_init = np.zeros(N)      # относительные мощности
    gains = [GainRBF() for _ in range(N)]

    # Сначала предварительно оцениваем Pt без G
    def residuals_power(Pt):
        res = []
        for m in meas:
            pl = path_loss(m["d"], n=n_pathloss)
            res.append(m["rssi"] - (Pt[m["j"]] - pl))
        return np.array(res) - np.mean(res)

    res = least_squares(residuals_power, Pt_init + K)
    Pt = res.x + K

    # Оценка направленных усилений
    gain_data = {i: {"dirs": [], "vals": []} for i in range(N)}
    for m in meas:
        pl = path_loss(m["d"], n=n_pathloss)
        base = m["rssi"] + pl - Pt[m["j"]]
        # равномерно делим вклад между i и j
        gain_data[m["i"]]["dirs"].append(m["angles_ij"])
        gain_data[m["i"]]["vals"].append(base / 2)
        gain_data[m["j"]]["dirs"].append(m["angles_ji"])
        gain_data[m["j"]]["vals"].append(base / 2)
    
    for i in range(N):
            dirs = np.array(gain_data[i]["dirs"])
            vals = np.array(gain_data[i]["vals"])
            if len(dirs) > 0:
                gains[i].fit(dirs, vals, lambda_reg=0.5)

    # Собираем результат
    model = {
        "devices": devices,
        "Pt": {devices[i]: Pt[i] for i in range(N)},
        "GainModels": {devices[i]: gains[i] for i in range(N)},
    }

    return model

import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import least_squares
from scipy.special import sph_harm

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
class GainZero:
    def gain(self, direction_vec):
        return 0.0

class GainRBF:
    def __init__(self, sigma=np.deg2rad(40), G0=0.0):
        self.sigma = sigma
        self.G0 = G0
        self.centers = None
        self.weights = None

    def fit(self, dirs, gains, lambda_reg=0.1):
        """dirs — массив углов [N,2]: (theta,phi), gains — [N]"""
        self.centers = dirs
        if self.G0 == 0.0:
            weights = np.sin(dirs[:, 0])
            self.G0 = np.average(gains, weights=weights)
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

class GainSH:
    def __init__(self, l_max=10, G0=0.0):
        """
        l_max — максимальный порядок сферических гармоник.
        G0 — базовое усиление (смещение).
        """
        self.l_max = l_max
        self.G0 = G0
        self.coeffs = None  # коэффициенты [complex]
        self.lm_list = None

    def _design_matrix(self, dirs):
        """Строит матрицу базисных функций Y_lm для всех направлений dirs."""
        thetas = dirs[:, 0]
        phis = dirs[:, 1]
        Y = []
        lm_list = []
        for l in range(self.l_max + 1):
            for m in range(-l, l + 1):
                Ylm = sph_harm(m, l, phis, thetas)  # Y_lm(phi, theta)
                Y.append(Ylm)
                lm_list.append((l, m))
        Y = np.vstack(Y).T  # форма [N, n_basis]
        return Y, lm_list

    def fit(self, dirs, gains, lambda_reg=0.1):
        """
        dirs — массив углов [N,2]: (theta, phi)
        gains — вектор значений усиления [N]
        lambda_reg — регуляризация (ridge)
        """
        if self.G0 == 0.0:
            weights = np.sin(dirs[:, 0])
            self.G0 = np.average(gains, weights=weights)
        Y, self.lm_list = self._design_matrix(dirs)
        N_basis = Y.shape[1]

        # Решаем (Y^H Y + λI)a = Y^H (g - G0)
        A = Y.conj().T @ Y + lambda_reg * np.eye(N_basis)
        b = Y.conj().T @ (gains - self.G0)
        self.coeffs = np.linalg.solve(A, b)

    def predict(self, dirs):
        """Оценка усиления в направлениях dirs [M,2]"""
        if self.coeffs is None:
            return np.full(len(dirs), self.G0)

        Y, _ = self._design_matrix(dirs)
        g_pred = self.G0 + np.real(Y @ self.coeffs)
        return g_pred

    def gain(self, direction_vec):
        """Возвращает усиление в направлении (x,y,z)"""
        theta, phi = spherical_angles(direction_vec)
        return float(self.predict(np.array([[theta, phi]])))

class GainIDW:
    def __init__(self, power=2, G0=0.0, eps=1e-6):
        """
        power — показатель для весов 1/d^power,
        G0 — базовое усиление (смещение),
        eps — минимальное расстояние для избежания деления на ноль.
        """
        self.power = power
        self.G0 = G0
        self.eps = eps
        self.centers = None
        self.gains = None

    def fit(self, dirs, gains, lambda_reg=None):
        """
        dirs — массив углов [N,2]: (theta, phi)
        gains — значения усиления [N]
        lambda_reg — не используется, для совместимости с интерфейсом
        """
        self.centers = dirs
        self.gains = gains
        if self.G0 == 0.0:
            weights = np.sin(dirs[:, 0])
            self.G0 = np.average(gains, weights=weights)

    def predict(self, dirs):
        """Оценка усиления в направлениях dirs [M,2]"""
        
        if self.centers is None:
            return np.full(len(dirs), self.G0)

        # Переводим (theta, phi) -> единичный вектор
        def sph2cart(th, ph):
            return np.stack([
                np.sin(th) * np.cos(ph),
                np.sin(th) * np.sin(ph),
                np.cos(th)
            ], axis=-1)

        Xq = sph2cart(dirs[:, 0], dirs[:, 1])
        Xc = sph2cart(self.centers[:, 0], self.centers[:, 1])

        # Угловое расстояние (по великой окружности)
        cos_dist = np.clip(np.dot(Xq, Xc.T), -1.0, 1.0)
        D = np.arccos(cos_dist)

        # Вес = 1 / (D^p), с обработкой нулевых расстояний
        W = 1.0 / np.maximum(D, self.eps) ** self.power
        W /= np.sum(W, axis=1, keepdims=True)  # нормализация

        return self.G0 + W @ (self.gains - self.G0)

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

    res = least_squares(residuals_power, Pt_init)
    Pt = res.x + K

    # Оценка направленных усилений
    gain_data = {i: {"dirs": [], "vals": []} for i in range(N)}
    for m in meas:
        pl = path_loss(m["d"], n=n_pathloss)
        base = m["rssi"] + pl - Pt[m["j"]]
        # равномерно делим вклад между i и j
        mid = (Pt[m["i"]] + Pt[m["j"]]) / 2
        gain_data[m["i"]]["dirs"].append(m["angles_ij"])
        # gain_data[m["i"]]["vals"].append(base + (mid - Pt[m["i"]]))
        gain_data[m["i"]]["vals"].append(base)
        # gain_data[m["j"]]["dirs"].append(m["angles_ji"])
        # gain_data[m["j"]]["vals"].append(base + (mid - Pt[m["j"]]))
        # gain_data[m["j"]]["vals"].append(base / 2)
    
    valid_count = 0

    for i in range(N):
        dirs = np.array(gain_data[i]["dirs"])
        vals = np.array(gain_data[i]["vals"])

        if len(dirs) > 0:
            gains[i].fit(dirs, vals, lambda_reg=0.5)
            valid_count += 1

    if valid_count != N:
        gains = [GainZero() for _ in range(N)]
        is_calibrated = False
    else:
        is_calibrated = True

    # Собираем результат
    model = {
        "devices": devices,
        "Pt": {devices[i]: Pt[i] for i in range(N)},
        "GainModels": {devices[i]: gains[i] for i in range(N)},
        "is_calibrated": is_calibrated,
    }

    return model

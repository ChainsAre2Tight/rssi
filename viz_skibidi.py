"""
rssi_localization.py

Локализация источника по RSSI (3D, log-distance PL, аналитический GainModel.gain(vec_local) -> dB)
- P0 (в dB) оптимизируем
- n фиксирован и задаётся в config
- GainModel возвращает только скаляр (dB); градиенты вычисляются центральными конечными разностями
- Инициализация: геометрический центр, P0 старт = медиана rssi
- Нет оценки шума; веса не используются (L2 loss)
"""

from typing import Dict, Callable, Tuple, Any, Optional
import numpy as np

# scipy may be required; if not installed, user must pip install scipy
from scipy.optimize import least_squares
from numpy.linalg import inv, LinAlgError

# ----------------------------
# Типы и конфиг
# ----------------------------
Vec3 = Tuple[float, float, float]

class GainModelInterface:
    """
    Интерфейс для GainModel.
    Метод .gain(vec_local: np.ndarray) -> float возвращает усиление в dB для радиус-вектора,
    заданного в локальной системе антенны (в метрах).
    """
    def gain(self, vec_local: np.ndarray) -> float:
        raise NotImplementedError("Implement gain(vec_local) -> float")


class Config:
    def __init__(
        self,
        n: float,
        d0: float = 1.0,
        h_G: float = 1e-3,
        d_min: float = 1e-2,
        p0_bounds: Tuple[float, float] = (-80.0, -40.0),
        tol: float = 1e-6,
        max_iter: int = 100,
        aggregate_rssi: str = "median",  # or "mean"
        compute_covariance: bool = True,
        sigma_for_covariance: Optional[float] = None  # if None -> use residual-based estimate up to scale
    ):
        self.n = n
        self.d0 = d0
        self.h_G = h_G
        self.d_min = d_min
        self.p0_bounds = p0_bounds
        self.tol = tol
        self.max_iter = max_iter
        self.aggregate_rssi = aggregate_rssi
        self.compute_covariance = compute_covariance
        self.sigma_for_covariance = sigma_for_covariance


# ----------------------------
# Вспомогательные функции
# ----------------------------
def aggregate_rssi_list(values: list, method: str = "median") -> float:
    arr = np.asarray(values, dtype=float)
    if method == "median":
        return float(np.median(arr))
    elif method == "mean":
        return float(np.mean(arr))
    else:
        raise ValueError("Unknown aggregation method: %s" % method)


# ----------------------------
# Основная реализация
# ----------------------------
class RSSILocalizer:
    def __init__(
        self,
        devices: list,
        GainModels: Dict[Any, GainModelInterface],
        rssi_values: Dict[Any, list],
        positions: Dict[Any, Vec3],
        config: Config
    ):
        """
        devices: список id устройств (ключи словарей ниже)
        GainModels: {id: GainModelInterface}
        rssi_values: {id: list_of_measurements (dB)}
        positions: {id: (x,y,z)} в метрах
        config: объект Config
        """
        self.devices = devices
        self.GainModels = GainModels
        self.rssi_values = rssi_values
        self.positions = {dev: np.asarray(positions[dev], dtype=float) for dev in devices}
        self.config = config

        # агрегируем RSSI (медиана/среднее)
        self.rssi_meas = {}
        for d in devices:
            self.rssi_meas[d] = aggregate_rssi_list(self.rssi_values[d], method=self.config.aggregate_rssi)

    def _model_rssi(self, x: np.ndarray, P0: float, device_id) -> float:
        """
        Вычисляет модельный RSSI в dB для одного датчика
        x: (3,) глобальная позиция источника
        P0: опорная мощность (dB)
        device_id: id датчика
        """
        s = self.positions[device_id]
        vec = -(x - s)  # радиус-вектор от датчика к источнику, глобальная система; GainModel принимает локальный vec
        d = np.linalg.norm(vec)
        d = max(d, self.config.d_min)
        Gi = self.GainModels[device_id].gain(vec)  # dB
        # Gi = 0
        # log-distance path loss (в dB): 10 n log10(d/d0)
        PL = 10.0 * self.config.n * np.log10(d / self.config.d0)
        r_model = P0 + Gi - PL
        return float(r_model)

    def residuals_vector(self, params: np.ndarray) -> np.ndarray:
        """
        params: [x, y, z, P0]
        возвращает вектор остатков e_i = r_i - r_model_i
        """
        x = params[0:3]
        P0 = float(params[3])
        res = []
        for dev in self.devices:
            r_meas = self.rssi_meas[dev]
            r_mod = self._model_rssi(x, P0, dev)
            res.append(r_meas - r_mod)
        return np.asarray(res, dtype=float)

    def analytic_jacobian(self, params: np.ndarray) -> np.ndarray:
        """
        Возвращает J (N x 4) матрицу частных производных остатков по параметрам [x,y,z,P0].
        Формула:
          e_i = r_i - (P0 + G_i(vec) - 10 n log10(d/d0))
        => ∂e/∂P0 = -1
           ∂e/∂x = -∇_v G_i(vec) + (10 n / ln 10) * vec / d^2
        ∇_v G_i вычисляем центральной разностью по компонентам с шагом h_G
        """
        x = params[0:3]
        P0 = float(params[3])
        N = len(self.devices)
        J = np.zeros((N, 4), dtype=float)
        h = self.config.h_G

        coef = 10.0 * self.config.n / np.log(10.0)  # 10 n / ln 10

        for idx, dev in enumerate(self.devices):
            s = self.positions[dev]
            vec = x - s
            d = np.linalg.norm(vec)
            d = max(d, self.config.d_min)

            # numeric gradient of G wrt vec components (central difference)
            Gi = self.GainModels[dev].gain(vec)
            grad_G = np.zeros(3, dtype=float)
            for k in range(3):
                e_k = np.zeros(3)
                e_k[k] = 1.0
                gp = self.GainModels[dev].gain(vec + h * e_k)
                gm = self.GainModels[dev].gain(vec - h * e_k)
                grad_G[k] = (gp - gm) / (2.0 * h)

            # analytical part from log-distance
            # derivative of 10n log10 d  wrt x is coef * (vec / d^2)
            part_log = coef * (vec / (d * d))

            # ∂e/∂x = -∇G + part_log
            J[idx, 0:3] = -grad_G + part_log
            J[idx, 3] = -1.0

        return J

    def localize(self, verbose: bool = True, return_full: bool = False) -> Dict[str, Any]:
        """
        Запустить оптимизацию и вернуть результат.
        return_full: если True, возвращает полный объект результата и якобиан/ковариацию
        """
        # стартовая инициализация
        s_positions = np.array([self.positions[d] for d in self.devices])
        x0 = np.mean(s_positions, axis=0)  # геометрический центр
        P0_0 = float(np.median(list(self.rssi_meas.values())))
        # P0_0 = -30
        p0_bounds = self.config.p0_bounds

        params0 = np.hstack([x0, P0_0])
        lower_bounds = np.array([-np.inf, -np.inf, -np.inf, p0_bounds[0]])
        upper_bounds = np.array([ np.inf,  np.inf,  np.inf, p0_bounds[1]])

        # wrapper residuals for least_squares
        def fun(p):
            return self.residuals_vector(p)

        def jac(p):
            return self.analytic_jacobian(p)

        res = least_squares(
            fun,
            x0=params0,
            jac=jac,
            bounds=(lower_bounds, upper_bounds),
            ftol=self.config.tol,
            xtol=self.config.tol,
            gtol=self.config.tol,
            max_nfev=self.config.max_iter,
            verbose=2 if verbose else 0
        )

        estimated = {
            "estimated_position": tuple(res.x[0:3].tolist()),
            "estimated_P0": float(res.x[3]),
            "converged": bool(res.success),
            "cost": float(res.cost),  # 1/2 sum(residuals^2)
            "optimality": float(res.optimality),
            "nfev": int(res.nfev),
        }

        # residuals per device
        res_vec = self.residuals_vector(res.x)
        residuals_dict = {dev: float(res_vec[idx]) for idx, dev in enumerate(self.devices)}
        estimated["residuals"] = residuals_dict

        # Jacobian at solution
        J = self.analytic_jacobian(res.x)
        estimated["jacobian_at_solution"] = J

        # Covariance approximation (if requested)
        if self.config.compute_covariance:
            # For L2 residuals, cov ~ sigma^2 * inv(J^T J)
            # If user provided sigma_for_covariance, use it; else estimate from residuals per degree of freedom
            m = len(self.devices)  # number of measurements
            p = 4  # number of parameters
            rss = np.sum(res_vec ** 2)  # sum squared residuals

            if self.config.sigma_for_covariance is not None:
                sigma2 = float(self.config.sigma_for_covariance ** 2)
            else:
                # unbiased estimator sigma^2 = rss / (m - p) if m>p else rss/m
                if m > p:
                    sigma2 = float(rss / float(m - p))
                else:
                    sigma2 = float(rss / float(max(1, m)))

            try:
                JTJ_inv = inv(J.T @ J)
                cov = sigma2 * JTJ_inv
                estimated["covariance"] = cov
                estimated["sigma2_used"] = sigma2
            except LinAlgError:
                estimated["covariance"] = None
                estimated["sigma2_used"] = sigma2
        else:
            estimated["covariance"] = None

        if return_full:
            return {"estimated": estimated, "lsq_result": res, "jacobian": J}
        else:
            return estimated

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # нужно для 3D
import numpy as np
import itertools

def plot_rssi_localization(positions: dict, result: dict, true_pos: tuple[float, float, float] = (0, 0, 0), title: str = "RSSI Localization Visualization"):
    """
    Визуализирует расположение датчиков и оценённую позицию источника.
    
    positions : dict {device_id: (x,y,z)} — координаты датчиков (в метрах)
    result : dict, полученный от RSSILocalizer.localize() (см. out["estimated_position"])
    title : str — заголовок графика
    """
    # Извлечь координаты
    device_ids = list(positions.keys())
    pos_array = np.array([positions[d] for d in device_ids])
    est_pos = np.array(result["estimated_position"])

    # Создать фигуру и 3D-ось
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(title, fontsize=12)

    # --- Датчики (красные)
    ax.scatter(pos_array[:, 0], pos_array[:, 1], pos_array[:, 2],
               color='red', s=50, label='Devices')

    # Подписи устройств
    for dev, (x, y, z) in zip(device_ids, pos_array):
        ax.text(x, y, z, dev, color='red', fontsize=9, weight='bold')

    # --- Синие рёбра между всеми датчиками (или только по ближайшим, если хотите)
    for (i, j) in itertools.combinations(range(len(device_ids)), 2):
        x_vals = [pos_array[i, 0], pos_array[j, 0]]
        y_vals = [pos_array[i, 1], pos_array[j, 1]]
        z_vals = [pos_array[i, 2], pos_array[j, 2]]
        ax.plot(x_vals, y_vals, z_vals, color='blue', linewidth=1, alpha=0.7)

    # Вектор расхождения
    vec = est_pos - true_pos
    ax.quiver(
        *true_pos,
        *vec,
        length=np.linalg.norm(vec),
        normalize=True,
        color='orange'
    )
    mid = true_pos + 0.5 * vec
    ax.text(mid[0], mid[1], mid[2], f"{np.linalg.norm(vec):.1f} m", color='black')


    # --- Предсказанная позиция источника (зелёная)
    ax.scatter(est_pos[0], est_pos[1], est_pos[2],
               color='green', s=80, label='Estimated Source', edgecolor='black')

    # Реальная позиция
    ax.scatter(*true_pos, color="yellow", s=50, label="True pos")

    
    # Настройки осей
    all_points = np.vstack([pos_array, est_pos.reshape(1, 3)])
    mins = np.min(all_points, axis=0)
    maxs = np.max(all_points, axis=0)
    pad = 0.2 * np.max(maxs - mins)
    ax.set_xlim(mins[0] - pad, maxs[0] + pad)
    ax.set_ylim(mins[1] - pad, maxs[1] + pad)
    ax.set_zlim(mins[2] - pad, maxs[2] + pad)

    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")

    ax.legend(loc='best')
    ax.view_init(elev=20, azim=35)
    ax.grid(True)

    plt.tight_layout()
    plt.show()


# ----------------------------
# Демонстрация / тест синтетических данных
# ----------------------------
if __name__ == "__main__":
    
    from compute.pair_calibrate import data, base_position
    from compute.calc_gain import calibrate_devices
    from storage.packets import index_rssi
    import storage.positions
    import config
    d = data()
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
            config.VIZ_MEASUREMENT_ID,
            dev,
            config.VIZ_SSID,
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
        config.VIZ_MEASUREMENT_ID,
        config.VIZ_SSID,
    )
    out = localizer.localize(verbose=False, return_full=False)
    plot_rssi_localization(model["positions"], out, true_pos)

    # # print("\nTrue position:", tuple(x_true.tolist()), "True P0:", P0_true)
    # print("Estimated:", out["estimated_position"], "Estimated P0:", out["estimated_P0"])
    # print("Converged:", out["converged"], "Cost:", out["cost"])
    # if out.get("covariance") is not None:
    #     print("Covariance (4x4) approx:\n", out["covariance"])

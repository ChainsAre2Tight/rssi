import numpy as np
from scipy.optimize import least_squares
import matplotlib
import matplotlib.pyplot as plt

import storage.packets, storage.positions
import config

matplotlib.use('QtAgg')

def get_data() -> list[dict[str, str]]:
    devices = storage.packets.index_devices_by_ssid(
        config.VIZ_MEASUREMENT_ID,
        config.VIZ_SSID,
    )
    data = []
    for device in devices:
        x, y, z = storage.positions.get_device_position(
            config.VIZ_MEASUREMENT_ID,
            device['name'],
        )
        base_rssi = storage.packets.index_rssi(
            config.VIZ_MEASUREMENT_ID,
            device["name"],
            "dmitry-moosetop",
        )
        rssi = storage.packets.index_rssi(
            config.VIZ_MEASUREMENT_ID,
            device["name"],
            config.VIZ_SSID,
        )
        data.append({
            "name": f"{device["name"]} {device["description"]}",
            "coords": np.array([x, y, z]),
            "rssi_base": np.array(base_rssi) + device['gain'],
            "rssi": np.array(rssi) + device['gain'],
        })
    return data

data = get_data()

# Преобразуем в удобные массивы
points = np.array([d["coords"] for d in data])
rssi_values = [d["rssi"] for d in data]
base_rssi_values = [d["rssi_base"] for d in data]
names = [d["name"] for d in data]

base_position = np.array(storage.positions.get_device_position(
    config.VIZ_MEASUREMENT_ID,
    "dmitry-moosetop",
))


# ---------- 2. Параметры ----------
n = 3
P0_values = np.linspace(-80, -50, 30)
# bounds = ((0, 6), (0, 3), (0, 3))  # кубический объём
# bounds = ((-1, 1), (-1, 1), (-1, 1))
bounds = ((1.5, 3.5), (0, 2), (0, 2))  # кубический объём


def compute_radius_2(power, gain, rssi):
    return np.mean(10**((power-(gain+rssi))/(10*n)))

def optimize_gain(P0, distance, rssi):
    def residuals(gain):
        return (compute_radius_2(P0, gain, rssi) - distance)
    res = least_squares(residuals, x0=0)
    return res.x[0]

for index in range(len(points)):
    rssi = base_rssi_values[index]
    point = points[index]
    distance = np.linalg.norm(base_position - point)
    gain = int(optimize_gain(-55, distance, rssi))
    print(index+1, gain)
    rssi_values[index] += gain
    

# ---------- 3. Функции ----------
def compute_radii(P0):
    """Рассчитывает радиусы по формуле из RSSI"""
    return np.array([np.mean(10 ** ((P0 - arr) / (10 * n))) for arr in rssi_values])

def compute_radius(pt):
    """Рассчитывает радиусы по формуле из RSSI"""
    return np.array([10 ** ((pt - np.mean(arr)) / (10 * n)) for arr in rssi_values])

# def trilaterate(P0):
#     """Находит точку, минимизирующую невязку сфер"""
    
#     # def residuals(p):
#     #     return (np.linalg.norm(points - np.array(p[:-1]), axis=1) - compute_radius(p[-1]))
#     def residuals(p):
#         return (np.linalg.norm(points - np.array(p), axis=1) - radii)
#     radii = compute_radii(P0)
#     res = least_squares(residuals, x0=np.mean(points, axis=0))
#     return res.x

def compute_radii_and_weights(P0, rssi_values, n):
    """Вычисляет радиусы и веса для взвешенной трилатерации"""
    radii = []
    weights = []

    for arr in rssi_values:
        mean_rssi = np.mean(arr)
        std_rssi = np.std(arr, ddof=1) + 1e-6  # добавим малое число чтобы избежать деления на 0
        d = 10 ** ((P0 - mean_rssi) / (10 * n))
        sigma_d = d * (np.log(10) / (10 * n)) * std_rssi
        w = 1.0 / (sigma_d ** 2)
        radii.append(d)
        weights.append(w)

    return np.array(radii), np.array(weights)

def trilaterate(P0):
    """Взвешенная трилатерация по RSSI"""
    radii, weights = compute_radii_and_weights(P0, rssi_values, n)

    def residuals(p):
        # взвешенные невязки
        return np.sqrt(weights) * (np.linalg.norm(points - np.array(p), axis=1) - radii)

    res = least_squares(residuals, x0=np.mean(points, axis=0))
    return res.x


def intersect_line_box(p0, v, bounds):
    """Находит пересечение линии p = p0 + t*v с прямоугольным объемом"""
    tmin, tmax = -np.inf, np.inf
    for i in range(3):
        if v[i] == 0:
            continue
        t1 = (bounds[i][0] - p0[i]) / v[i]
        t2 = (bounds[i][1] - p0[i]) / v[i]
        t1, t2 = min(t1, t2), max(t1, t2)
        tmin = max(tmin, t1)
        tmax = min(tmax, t2)
    if tmin > tmax:
        return None
    return p0 + tmin * v, p0 + tmax * v

# ---------- 4. Основные расчеты ----------
positions = np.array([trilaterate(P0) for P0 in P0_values])

# Аппроксимация линии (SVD)
C = positions.mean(axis=0)
_, _, vh = np.linalg.svd(positions - C)
direction = vh[0]

# Пересечение с кубом
intersection_points = intersect_line_box(C, direction, bounds)

# ---------- 5. Визуализация ----------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(base_position[0], base_position[1], base_position[2], color='y', s=50)

# Сферы (используем радиусы для среднего P0)
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
radii_mean = compute_radii(P0_values[len(P0_values)//2])
for (x, y, z), r, name in zip(points, radii_mean, names):
    ax.plot_surface(
        x + r*np.cos(u)*np.sin(v),
        y + r*np.sin(u)*np.sin(v),
        z + r*np.cos(v),
        color='b', alpha=0.15
    )
    ax.scatter(x, y, z, color='r', s=50)
    ax.text(x, y, z, name, color='k', fontsize=9, ha='center', va='bottom')

# Точки трилатерации
ax.scatter(positions[:,0], positions[:,1], positions[:,2], color='g', s=40, label='Трилатерация')

# Прямая
t = np.linspace(-20, 20, 100)
line = C + np.outer(t, direction)
ax.plot(line[:,0], line[:,1], line[:,2], 'k--', lw=2, label='Аппрокс. прямая')

# Пересечение с кубом
if intersection_points:
    p_in, p_out = intersection_points
    ax.scatter(*p_in, color='m', s=80, label='Пересечение (вход)')
    ax.scatter(*p_out, color='c', s=80, label='Пересечение (выход)')
    ax.text(*p_in, "IN", color='m', fontsize=9, ha='right')
    ax.text(*p_out, "OUT", color='c', fontsize=9, ha='left')

# Настройки осей и куба
ax.set_xlim(bounds[0])
ax.set_ylim(bounds[1])
ax.set_zlim(bounds[2])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
ax.set_box_aspect([1,1,1])
plt.tight_layout()
plt.show()

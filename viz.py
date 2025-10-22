import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt

# ---------- 1. Исходные данные ----------
points = np.array([
    [1, 2, 1],
    [4, 5, 3],
    [7, 8, 6],
    [9, 2, 5],
])
rssi_values = [
    np.array([-60, -61, -62]),
    np.array([-63, -64, -62]),
    np.array([-65, -66, -67]),
    np.array([-68, -69, -70]),
]
n = 2.0

# ---------- 2. Функции ----------
def compute_radii(P0):
    """Рассчитывает радиусы по формуле из RSSI"""
    return np.array([np.mean(10 ** ((P0 - arr) / (10 * n))) for arr in rssi_values])

def trilaterate(P0):
    """Находит точку, минимизирующую невязку сфер"""
    radii = compute_radii(P0)
    def residuals(p):
        return np.linalg.norm(points - p, axis=1) - radii
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

# ---------- 3. Основные расчеты ----------
P0_values = np.linspace(-45, -70, 10)
positions = np.array([trilaterate(P0) for P0 in P0_values])

# Аппроксимация линии (SVD)
C = positions.mean(axis=0)
_, _, vh = np.linalg.svd(positions - C)
direction = vh[0]

# Границы куба
bounds = ((0, 10), (0, 10), (0, 10))
intersection_points = intersect_line_box(C, direction, bounds)

# ---------- 4. Визуализация ----------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Сферы
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
radii_mean = compute_radii(P0_values[len(P0_values)//2])
for (x, y, z), r in zip(points, radii_mean):
    ax.plot_surface(
        x + r*np.cos(u)*np.sin(v),
        y + r*np.sin(u)*np.sin(v),
        z + r*np.cos(v),
        color='b', alpha=0.15
    )
    ax.scatter(x, y, z, color='r', s=50, label='Центры сфер')

# Точки трилатерации
ax.scatter(positions[:,0], positions[:,1], positions[:,2], color='g', s=40, label='Трилатерация')

# Прямая
t = np.linspace(-20, 20, 100)
line = C + np.outer(t, direction)
ax.plot(line[:,0], line[:,1], line[:,2], 'k--', lw=2, label='Аппрокс. прямая')

# Точки пересечения
if intersection_points:
    p_in, p_out = intersection_points
    ax.scatter(*p_in, color='m', s=80, label='Пересечение (вход)')
    ax.scatter(*p_out, color='c', s=80, label='Пересечение (выход)')

# Параметры осей и куба
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

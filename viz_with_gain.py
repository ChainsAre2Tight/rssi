import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection


# ------------------------------
# Генератор направлений (icosphere)
# ------------------------------
def icosphere(subdivisions=2):
    """Возвращает нормализованные направления (N, 3) равномерно распределённые по сфере."""
    t = (1.0 + np.sqrt(5.0)) / 2.0
    verts = np.array([
        [-1,  t,  0],
        [ 1,  t,  0],
        [-1, -t,  0],
        [ 1, -t,  0],
        [ 0, -1,  t],
        [ 0,  1,  t],
        [ 0, -1, -t],
        [ 0,  1, -t],
        [ t,  0, -1],
        [ t,  0,  1],
        [-t,  0, -1],
        [-t,  0,  1],
    ])
    faces = np.array([
        [0,11,5], [0,5,1], [0,1,7], [0,7,10], [0,10,11],
        [1,5,9], [5,11,4], [11,10,2], [10,7,6], [7,1,8],
        [3,9,4], [3,4,2], [3,2,6], [3,6,8], [3,8,9],
        [4,9,5], [2,4,11], [6,2,10], [8,6,7], [9,8,1]
    ])

    def midpoint(a, b):
        return (a + b) / np.linalg.norm(a + b)

    for _ in range(subdivisions):
        new_faces = []
        mid_cache = {}

        def mid_idx(i1, i2):
            key = tuple(sorted((i1, i2)))
            if key not in mid_cache:
                mid_cache[key] = len(verts_list)
                verts_list.append(midpoint(verts[i1], verts[i2]))
            return mid_cache[key]

        verts_list = list(verts)
        for tri in faces:
            a = mid_idx(tri[0], tri[1])
            b = mid_idx(tri[1], tri[2])
            c = mid_idx(tri[2], tri[0])
            new_faces += [
                [tri[0], a, c],
                [tri[1], b, a],
                [tri[2], c, b],
                [a, b, c]
            ]
        verts = np.array(verts_list)
        faces = np.array(new_faces)

    verts = verts / np.linalg.norm(verts, axis=1)[:, None]
    return verts, faces


# ------------------------------
# Построение сфер для модели
# ------------------------------
def plot_signal_surfaces(model, n=2.5, K_db=0.0):
    """
    model: {
        "devices": [...],
        "GainModels": {"A": Gobj, ...},
        "rssi_values": {"A": [-60, -61, ...]},
        "positions": {"A": (x,y,z), ...}
    }
    """
    devices = model["devices"]
    gain_models = model["GainModels"]
    rssi_values = model["rssi_values"]
    positions = model["positions"]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    dirs, faces = icosphere(subdivisions=2)

    for dev in devices:
        pos = np.array(positions[dev])
        rssi_mean = np.mean(rssi_values[dev])
        gain_model = gain_models[dev]

        G_db = np.array([gain_model.gain(vec) for vec in dirs])
        d = 10 ** ((K_db - (rssi_mean - G_db)) / (10 * n))  # Path-loss distance
        pts = pos + dirs * d[:, None]

        # полупрозрачная оранжевая поверхность
        mesh = Poly3DCollection(pts[faces], alpha=0.2, facecolor='orange', edgecolor='none')
        ax.add_collection3d(mesh)

        # рёбра сферы (wireframe)
        edges = []
        for tri in faces:
            for i in range(3):
                edges.append([pts[tri[i]], pts[tri[(i + 1) % 3]]])
        line_collection = Line3DCollection(edges, color='orange', alpha=0.7, linewidths=0.5)
        ax.add_collection3d(line_collection)

        # точка устройства
        ax.scatter(*pos, color='red', s=50)
        ax.text(pos[0], pos[1], pos[2], f" {dev}", color='red', fontsize=10, weight='bold')

    all_pts = np.array([positions[d] for d in devices])
    lims = np.ptp(all_pts, axis=0).max() * 1.5
    center = all_pts.mean(axis=0)
    ax.set_xlim(center[0] - lims / 2, center[0] + lims / 2)
    ax.set_ylim(center[1] - lims / 2, center[1] + lims / 2)
    ax.set_zlim(center[2] - lims / 2, center[2] + lims / 2)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Path-Loss surfaces per device (RSSI median)")
    plt.tight_layout()
    plt.show()


# ------------------------------
# Пример использования
# ------------------------------

from pair_calibrate import data, base_position
from calc_gain import calibrate_devices
from storage.packets import index_rssi
import config

model = calibrate_devices(
    data,
    config.PATH_LOSS_EXPONENT,
    config.ESP32_SIGNAL_STRENGTH
)

model["rssi_values"] = {}
model["positions"] = {}

for dev in model["devices"]:
    model["positions"][dev] = data[dev]["position"]
    model["rssi_values"][dev] = index_rssi(
        config.VIZ_MEASUREMENT_ID,
        dev,
        config.VIZ_SSID,
    )

plot_signal_surfaces(model, 2, -60)

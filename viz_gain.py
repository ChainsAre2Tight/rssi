
import matplotlib.pyplot as plt
import numpy as np

from calc_gain import calibrate_devices

def plot_devices_with_gain(model, scale_gain=0.1, base_position=(0, 0, 0)):
    """
    3D график устройств и направленных gain в сторону других устройств
    scale_gain: масштаб для визуализации векторов усиления
    """
    devices = model["devices"]
    Pt_dict = model["Pt"]
    GainModels = model["GainModels"]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_box_aspect([1,1,1])

    # собираем позиции устройств
    positions = {dev: np.array(model["GainModels"][dev].G0) for dev in devices}  # placeholder, подставим реальные позиции
    # Для визуализации используем реальные позиции из данных (если передали их)
    if hasattr(model["GainModels"][devices[0]], "positions"):
        positions = {dev: np.array(model["GainModels"][dev].positions) for dev in devices}

    # рисуем устройства
    for dev in devices:
        pos = np.array(model["GainModels"][dev].positions) if hasattr(model["GainModels"][dev], "positions") else np.zeros(3)
        ax.scatter(*pos, color='red', s=80)
        ax.text(pos[0], pos[1], pos[2],
                f"{dev}\nPt={Pt_dict[dev]:.1f} dB",
                color='black')
    
    # ноутбук
    ax.scatter(*base_position, color="yellow", s=80)

    # рисуем векторы усиления между устройствами
    for i, dev_i in enumerate(devices):
        pos_i = np.array(model["GainModels"][dev_i].positions) if hasattr(model["GainModels"][dev_i], "positions") else np.zeros(3)
        G_i = GainModels[dev_i]
        for j, dev_j in enumerate(devices):
            if dev_i == dev_j:
                continue
            pos_j = np.array(model["GainModels"][dev_j].positions) if hasattr(model["GainModels"][dev_j], "positions") else np.zeros(3)
            vec = pos_j - pos_i
            gain_val = G_i.gain(vec)
            G_lin = 10**(gain_val / 20)
            vec_scaled = vec / np.linalg.norm(vec) * G_lin * scale_gain
            ax.quiver(pos_i[0], pos_i[1], pos_i[2],
                      vec[0], vec[1], vec[2],
                      length=np.linalg.norm(vec_scaled), normalize=True, color='blue')
            # mid = pos_i + 0.5 * vec * scale_gain
            mid = pos_i + 0.5 * vec_scaled
            ax.text(mid[0], mid[1], mid[2], f"{gain_val:.1f} dB", color='blue')
        
        vec = base_position - pos_i
        gain_val = G_i.gain(vec)
        G_lin = 10**(gain_val / 20)
        vec_scaled = vec / np.linalg.norm(vec) * G_lin * scale_gain
        ax.quiver(pos_i[0], pos_i[1], pos_i[2],
                    vec[0], vec[1], vec[2],
                    length=np.linalg.norm(vec_scaled), normalize=True, color='green')
        # mid = pos_i + 0.5 * vec * scale_gain
        mid = pos_i + 0.5 * vec_scaled
        ax.text(mid[0], mid[1], mid[2], f"{gain_val:.1f} dB", color='green')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Devices and directional gain vectors")
    plt.show()

# model = calibrate_devices(data)

# G_A = model["GainModels"]["A"]
# direction = np.array([0, 1.0, 0.0])  # направление на произвольную точку
# print(G_A.gain(direction))

from pair_calibrate import data, base_position
import config
d = data()
model = calibrate_devices(
    d,
    config.PATH_LOSS_EXPONENT,
    config.ESP32_SIGNAL_STRENGTH
)

# Чтобы RBF знал позиции для визуализации:
for dev in model["devices"]:
    model["GainModels"][dev].positions = np.array(d[dev]["position"])

plot_devices_with_gain(model, scale_gain=1, base_position=base_position)
def compute_bounding_box_center(devices: dict):
    positions = [v["position"] for v in devices.values() if "position" in v]

    if not positions:
        raise ValueError("Нет данных о позициях устройств")

    # Транспонируем список [[x1,y1,z1], [x2,y2,z2], ...] → [(x1,x2,...), (y1,y2,...), (z1,z2,...)]
    xs, ys, zs = zip(*positions)

    bbox_min = [min(xs), min(ys), min(zs)]
    bbox_max = [max(xs), max(ys), max(zs)]
    center = [(bbox_min[i] + bbox_max[i]) / 2 for i in range(3)]

    return {
        "bbox_min": bbox_min,
        "bbox_max": bbox_max,
        "center": center
    }

import numpy as np

def angular_error(bbox: dict, true_pos, pred_pos) -> float:
    """
    Вычисляет угловую ошибку (в радианах) между векторами 
    'центр → истинная позиция' и 'центр → предсказанная позиция'.

    Parameters
    ----------
    bbox : dict
        {'bbox_min': [x_min, y_min, z_min], 'bbox_max': [x_max, y_max, z_max]}
    true_pos : array-like
        Истинная позиция [x, y, z]
    pred_pos : array-like
        Предсказанная позиция [x, y, z]

    Returns
    -------
    float
        Угловая ошибка в радианах (0 — идеальное совпадение направлений)
    """

    # Центр бокса
    bbox_min = np.array(bbox["bbox_min"])
    bbox_max = np.array(bbox["bbox_max"])
    center = (bbox_min + bbox_max) / 2

    # Вектора от центра
    v_true = np.array(true_pos) - center
    v_pred = np.array(pred_pos) - center

    # Проверка на нулевые вектора
    norm_true = np.linalg.norm(v_true)
    norm_pred = np.linalg.norm(v_pred)
    if norm_true == 0 or norm_pred == 0:
        raise ValueError("Один из векторов имеет нулевую длину — невозможно вычислить угол")

    # Косинус угла
    cos_theta = np.dot(v_true, v_pred) / (norm_true * norm_pred)

    # Защита от ошибок округления
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    # Угол в радианах
    theta = np.arccos(cos_theta)

    return theta

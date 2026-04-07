from decouple import config as env

DB_FILE: str = env("DB_PATH")
NAME: str = env("NAME")

ROOM_ID: int = int(env("ROOM_ID"))
MEASUREMENT_ID: int = int(env("MEASUREMENT_ID"))

VIZ_SSID: str = env("VIZ_SSID")
VIZ_ROOM_ID: int = int(env("VIZ_ROOM_ID"))
VIZ_MEASUREMENT_ID: int = int(env("VIZ_MEASUREMENT_ID"))

PATH_LOSS_EXPONENT: float = float(env("PATH_LOSS_EXPONENT"))
ESP32_SIGNAL_STRENGTH: float = float(env("ESP32_SIGNAL_STRENGTH"))

WINDOW_SIZE_US = 60_000_000
WINDOW_STEP_US = 30_000_000

WINDOW_MARGIN_US = 5_000_000

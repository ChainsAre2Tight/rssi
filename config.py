import logging

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

LOG_LEVEL: str = str(env("LOG_LEVEL", "info")).upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s"
)
logger = logging.getLogger("app")

WINDOW_SIZE_US = 60_000_000
WINDOW_STEP_US = 30_000_000
WINDOW_MARGIN_US = 30_000_000

MERGE_WINDOW_US = 100_000
REORDER_WINDOW_US = 20_000_000

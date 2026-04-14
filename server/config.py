import logging
import os

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

WHITELIST_PATH: str = env("WHITELIST_JSON_PATH", "whitelist.json")

LOG_LEVEL: str = str(env("LOG_LEVEL", "info")).upper()
worker = os.environ.get("WORKER_NAME", "main")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=f"%(asctime)s [%(levelname)s] [{worker}] %(name)s.%(funcName)s: %(message)s",
)
logger = logging.getLogger("app")

WINDOW_SIZE_US = 60_000_000
WINDOW_STEP_US = 30_000_000
WINDOW_MARGIN_US = 30_000_000

MERGE_WINDOW_US = 100_000
REORDER_WINDOW_US = 20_000_000

DATASET_DIR: str = str(env("DATASET_DIR"))
CSI_COMPLEX_COUNT: int = 156 # 312 in firmware // 2

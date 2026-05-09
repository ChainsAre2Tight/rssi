import logging
import os

from decouple import config as env

DB_FILE: str = env("DB_PATH", "/database/database.db") # type: ignore
NAME: str = env("NAME", __name__) # type: ignore

ROOM_ID: int = int(env("ROOM_ID", "1"))
MEASUREMENT_ID: int = int(env("MEASUREMENT_ID", "1"))

VIZ_SSID: str = env("VIZ_SSID", "123321") # type: ignore
VIZ_ROOM_ID: int = int(env("VIZ_ROOM_ID", "1"))
VIZ_MEASUREMENT_ID: int = int(env("VIZ_MEASUREMENT_ID", "1"))

PATH_LOSS_EXPONENT: float = float(env("PATH_LOSS_EXPONENT", "2.5"))
ESP32_SIGNAL_STRENGTH: float = float(env("ESP32_SIGNAL_STRENGTH", "-60.0"))

WHITELIST_PATH: str = env("WHITELIST_JSON_PATH", "whitelist.json") # type: ignore

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

TARGET_CSI_SUBCARRIERS = 64

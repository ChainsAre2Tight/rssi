import os

DB_FILE = os.environ.get("DB_PATH") or "database.db"
NAME = os.environ.get("NAME") or "esp32-sniffer-server"

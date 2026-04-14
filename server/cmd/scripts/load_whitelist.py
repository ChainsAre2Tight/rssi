import json
import re
from pathlib import Path

import storage
import config


MAC_RE = re.compile(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$")


def normalize_mac(mac: str) -> str:
    mac = mac.strip().upper()

    if not MAC_RE.match(mac):
        raise ValueError(f"Invalid MAC address: {mac}")

    return mac


def validate_whitelist(data: dict) -> dict:

    if not isinstance(data, dict):
        raise ValueError("Whitelist root must be JSON object")

    validated = {}

    for ssid, mac_list in data.items():

        if not isinstance(ssid, str):
            raise ValueError(f"SSID must be string: {ssid}")

        if not isinstance(mac_list, list):
            raise ValueError(f"SSID '{ssid}' must map to list of MACs")

        normalized_macs = []

        for mac in mac_list:

            if not isinstance(mac, str):
                raise ValueError(f"Invalid MAC entry for SSID '{ssid}'")

            normalized_macs.append(normalize_mac(mac))

        validated[ssid] = sorted(set(normalized_macs))

    return validated


def load_whitelist_file(path: Path) -> dict:

    if not path.exists():
        raise FileNotFoundError(f"Whitelist file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return validate_whitelist(data)


def ensure_measurement(conn, measurement_id: int) -> None:

    cur = conn.execute(
        """
        SELECT id
        FROM measurements
        WHERE id = ?
        """,
        (measurement_id,),
    )

    if cur.fetchone() is not None:
        return

    conn.execute(
        """
        INSERT INTO measurements (id, name, room_id, description)
        VALUES (?, ?, ?, ?)
        """,
        (
            measurement_id,
            "General",
            0, #TODO: maybe add to config idk
            "auto-created by whitelist loader",
        ),
    )


def store_whitelist(conn, measurement_id: int, whitelist: dict) -> None:

    whitelist_json = json.dumps(whitelist)

    conn.execute(
        """
        UPDATE measurements
        SET whitelist_json = ?
        WHERE id = ?
        """,
        (whitelist_json, measurement_id),
    )


def main() -> None:

    path = Path(config.WHITELIST_PATH)

    print(f"Loading whitelist from {path}")

    whitelist = load_whitelist_file(path)

    print(f"Validated {len(whitelist)} SSIDs")

    with storage.Session() as conn:

        with storage.Transaction(conn):

            ensure_measurement(conn, config.MEASUREMENT_ID)

            store_whitelist(conn, config.MEASUREMENT_ID, whitelist)

    print(f"Whitelist stored for measurement {config.MEASUREMENT_ID}")


if __name__ == "__main__":
    main()
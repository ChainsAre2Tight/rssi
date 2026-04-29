import re

import sqlite3
from storage.measurements import (
    load_measurement_whitelist,
    store_measurement_whitelist,
)

def add_whitelist_entry(
    conn: sqlite3.Connection,
    measurement_id: int,
    ssid: str,
    bssid: str
) -> bool:
    ssid, bssid = validate_inputs(ssid, bssid)

    whitelist = load_measurement_whitelist(conn, measurement_id) or {}
    changed = add_pair(whitelist, ssid, bssid)

    if changed:
        store_measurement_whitelist(conn, measurement_id, whitelist)

    return changed

def remove_whitelist_entry(
    conn: sqlite3.Connection,
    measurement_id: int,
    ssid: str,
    bssid: str
) -> bool:
    ssid, bssid = validate_inputs(ssid, bssid)

    whitelist = load_measurement_whitelist(conn, measurement_id) or {}
    changed = remove_pair(whitelist, ssid, bssid)

    if changed:
        store_measurement_whitelist(conn, measurement_id, whitelist)

    return changed


SSID_MAX_LEN = 32
BSSID_REGEX = re.compile(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")

def validate_ssid(ssid: str) -> str:
    if not isinstance(ssid, str):
        raise ValueError("SSID must be a string")
    ssid = ssid.strip()
    if not ssid or len(ssid) > SSID_MAX_LEN:
        raise ValueError("Invalid SSID length")
    return ssid


def validate_bssid(bssid: str) -> str:
    if not isinstance(bssid, str):
        raise ValueError("BSSID must be a string")
    bssid = bssid.strip().lower()
    if not BSSID_REGEX.match(bssid):
        raise ValueError("Invalid BSSID format")
    return bssid.upper()


def validate_inputs(ssid: str, bssid: str) -> tuple[str, str]:
    return validate_ssid(ssid), validate_bssid(bssid)

def add_pair(whitelist: dict, ssid: str, bssid: str) -> bool:
    changed = False

    if ssid not in whitelist:
        whitelist[ssid] = [bssid]
        return True

    bssid_set = set(whitelist[ssid])

    if bssid in bssid_set:
        return False

    bssid_set.add(bssid)
    whitelist[ssid] = list(bssid_set)
    return True

def remove_pair(whitelist: dict, ssid: str, bssid: str) -> bool:
    if ssid not in whitelist:
        return False

    bssid_set = set(whitelist[ssid])

    if bssid not in bssid_set:
        return False

    bssid_set.remove(bssid)

    if not bssid_set:
        del whitelist[ssid]
    else:
        whitelist[ssid] = list(bssid_set)

    return True
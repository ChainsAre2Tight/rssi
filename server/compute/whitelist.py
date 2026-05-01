import re

import sqlite3
from storage.measurements import (
    load_measurement_whitelist,
    store_measurement_whitelist,
)

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


def ensure_ssid(whitelist: dict, ssid: str) -> bool:
    if ssid in whitelist:
        return False
    whitelist[ssid] = []
    return True


def add_bssid(whitelist: dict, ssid: str, bssid: str) -> bool:
    if ssid not in whitelist:
        whitelist[ssid] = [bssid]
        return True

    if bssid in whitelist[ssid]:
        return False

    whitelist[ssid].append(bssid)
    return True


def remove_bssid(
    whitelist: dict,
    ssid: str,
    bssid: str,
    remove_empty_ssid: bool = True
) -> bool:
    if ssid not in whitelist:
        return False

    if bssid not in whitelist[ssid]:
        return False

    whitelist[ssid].remove(bssid)

    if not whitelist[ssid] and remove_empty_ssid:
        del whitelist[ssid]

    return True


def remove_ssid(whitelist: dict, ssid: str) -> bool:
    if ssid not in whitelist:
        return False

    del whitelist[ssid]
    return True


def rename_ssid(whitelist: dict, old: str, new: str) -> str:
    if old not in whitelist:
        return "not_found"

    if old == new:
        return "same_name"

    old_bssids = set(whitelist[old])

    if new in whitelist:
        # union
        merged = set(whitelist[new]) | old_bssids
        whitelist[new] = list(merged)
        del whitelist[old]
        return "merged"

    whitelist[new] = list(old_bssids)
    del whitelist[old]
    return "renamed"


def add_whitelist_entry(
    conn: sqlite3.Connection,
    measurement_id: int,
    ssid: str,
    bssid: str | None
) -> tuple[bool, str]:
    ssid = validate_ssid(ssid)

    whitelist = load_measurement_whitelist(conn, measurement_id) or {}

    if bssid:
        bssid = validate_bssid(bssid)
        changed = add_bssid(whitelist, ssid, bssid)
        action = "bssid_added" if changed else "already_exists"
    else:
        changed = ensure_ssid(whitelist, ssid)
        action = "ssid_created" if changed else "already_exists"

    if changed:
        store_measurement_whitelist(conn, measurement_id, whitelist)

    return changed, action


def remove_whitelist_entry(
    conn: sqlite3.Connection,
    measurement_id: int,
    ssid: str,
    bssid: str | None,
    remove_empty_ssid: bool = True
) -> tuple[bool, str]:
    ssid = validate_ssid(ssid)

    whitelist = load_measurement_whitelist(conn, measurement_id) or {}

    if bssid:
        bssid = validate_bssid(bssid)
        changed = remove_bssid(
            whitelist,
            ssid,
            bssid,
            remove_empty_ssid=remove_empty_ssid
        )
        action = "bssid_removed" if changed else "not_found"
    else:
        changed = remove_ssid(whitelist, ssid)
        action = "ssid_removed" if changed else "not_found"

    if changed:
        store_measurement_whitelist(conn, measurement_id, whitelist)

    return changed, action


def rename_whitelist_ssid(
    conn: sqlite3.Connection,
    measurement_id: int,
    ssid: str,
    new_ssid: str
) -> tuple[bool, str]:
    ssid = validate_ssid(ssid)
    new_ssid = validate_ssid(new_ssid)

    whitelist = load_measurement_whitelist(conn, measurement_id) or {}

    result = rename_ssid(whitelist, ssid, new_ssid)

    if result in ("renamed", "merged"):
        store_measurement_whitelist(conn, measurement_id, whitelist)
        return True, result

    return False, result

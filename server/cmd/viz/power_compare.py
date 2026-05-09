#!/usr/bin/env python3
"""
CSI Fingerprint Comparator

Plots per‑sensor amplitude profiles from two fingerprints (different BSSIDs or windows).

Usage:
    python compare_csi_fingerprints.py --measurement_id 1 \
        --first_bssid "AA:BB:CC:DD:EE:FF" --first_window 42 \
        --second_bssid "11:22:33:44:55:66" --second_window 99
"""

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np

from storage.csi_fingerprints import loads
import storage


def parse_args():
    parser = argparse.ArgumentParser(description="Compare two CSI fingerprints")
    parser.add_argument("--measurement_id", type=int, required=True, help="Measurement ID")
    parser.add_argument("--first_bssid", type=str, required=True, help="BSSID of first fingerprint")
    parser.add_argument("--first_window", type=int, required=True, help="Window ID of first fingerprint")
    parser.add_argument("--second_bssid", type=str, required=True, help="BSSID of second fingerprint")
    parser.add_argument("--second_window", type=int, required=True, help="Window ID of second fingerprint")
    return parser.parse_args()


def get_fingerprint_by_window_id(conn, window_id: int, bssid: str):
    """Retrieve fingerprint for a given window_id and bssid."""
    row = conn.execute(
        """
        SELECT id, measurement_id, window_id, bssid, is_reference,
               vector, sensor_names_json, metadata_json
        FROM csi_fingerprints
        WHERE window_id = ? AND bssid = ?
        LIMIT 1
        """,
        (window_id, bssid),
    ).fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "measurement_id": row[1],
        "window_id": row[2],
        "bssid": row[3],
        "is_reference": bool(row[4]),
        "vector": row[5],
        "sensor_names": loads(row[6]),
        "metadata": loads(row[7]) if row[7] else {},
    }


def main():
    args = parse_args()
    with storage.Session() as conn:
        fp1 = get_fingerprint_by_window_id(conn, args.first_window, args.first_bssid)
        if fp1 is None:
            print(f"Error: No fingerprint found for window {args.first_window}, BSSID {args.first_bssid}")
            sys.exit(1)

        fp2 = get_fingerprint_by_window_id(conn, args.second_window, args.second_bssid)
        if fp2 is None:
            print(f"Error: No fingerprint found for window {args.second_window}, BSSID {args.second_bssid}")
            sys.exit(1)

    # Extract metadata and vectors
    meta1 = fp1["metadata"]
    meta2 = fp2["metadata"]

    # Sensor order – may differ; we'll create a union of sensor names
    sensor_order1 = meta1.get("sensor_order", fp1["sensor_names"])
    sensor_order2 = meta2.get("sensor_order", fp2["sensor_names"])
    # Keep the order of the first fingerprint, but include any extra from second
    all_sensors = list(dict.fromkeys(sensor_order1 + sensor_order2))  # preserve order, remove duplicates

    # Number of subcarriers – must be identical
    n_subcarriers = meta1.get("n_subcarriers")
    if not n_subcarriers:
        vec_len = len(np.frombuffer(fp1["vector"], dtype=np.complex64))
        n_subcarriers = vec_len // len(sensor_order1)
    n_subcarriers2 = meta2.get("n_subcarriers")
    if n_subcarriers2 and n_subcarriers2 != n_subcarriers:
        print(f"Warning: Subcarrier count mismatch: {n_subcarriers} vs {n_subcarriers2}. Using {n_subcarriers}.")
    # Fallback infer for second if needed
    if not n_subcarriers2:
        vec_len2 = len(np.frombuffer(fp2["vector"], dtype=np.complex64))
        n_subcarriers2 = vec_len2 // len(sensor_order2)
        if n_subcarriers2 != n_subcarriers:
            print(f"Warning: Inferred subcarrier count mismatch: {n_subcarriers} vs {n_subcarriers2}. Using {n_subcarriers}.")

    # Convert vectors to real arrays
    vec1 = np.frombuffer(fp1["vector"], dtype=np.complex64).real
    vec2 = np.frombuffer(fp2["vector"], dtype=np.complex64).real

    # Build mapping from sensor to its profile (vector slice)
    def get_profile_map(vec, sensor_order, n_sc):
        profile_map = {}
        for idx, sensor in enumerate(sensor_order):
            start = idx * n_sc
            end = start + n_sc
            profile_map[sensor] = vec[start:end]
        return profile_map

    profiles1 = get_profile_map(vec1, sensor_order1, n_subcarriers)
    profiles2 = get_profile_map(vec2, sensor_order2, n_subcarriers)

    # Create subplots
    n_sensors = len(all_sensors)
    if n_sensors == 0:
        print("No sensors to plot.")
        sys.exit(1)

    fig, axes = plt.subplots(n_sensors, 1, figsize=(12, 3 * n_sensors), sharex=True)
    if n_sensors == 1:
        axes = [axes]

    subcarrier_indices = np.arange(n_subcarriers)
    width = 0.35

    for idx, sensor in enumerate(all_sensors):
        ax = axes[idx]
        prof1 = profiles1.get(sensor, np.zeros(n_subcarriers))
        prof2 = profiles2.get(sensor, np.zeros(n_subcarriers))

        # Bar pairs: first in green, second in blue
        x = subcarrier_indices
        ax.bar(x - width/2, prof1, width,
               label=f"First: {fp1['bssid']} (win {fp1['window_id']})",
               color='green', alpha=0.7)
        ax.bar(x + width/2, prof2, width,
               label=f"Second: {fp2['bssid']} (win {fp2['window_id']})",
               color='blue', alpha=0.7)

        ax.set_title(f"Sensor: {sensor}")
        ax.set_ylabel("Amplitude")
        ax.legend()
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Subcarrier index")
    fig.suptitle(f"CSI Amplitude Profile Comparison\nMeasurement ID: {args.measurement_id}", fontsize=14)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
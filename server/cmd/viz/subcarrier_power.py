#!/usr/bin/env python3
"""
CSI Fingerprint Viewer

Plots per‑sensor amplitude profiles (reference vs selected window) as vertical bar pairs,
skipping sensors with zero amplitude in both fingerprints.

Usage:
    python view_csi_fingerprint.py --measurement_id 1 --bssid "AA:BB:CC:DD:EE:FF" --window_id 42
"""

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np

from storage.csi_fingerprints import get_reference_fingerprint, loads
import storage


def parse_args():
    parser = argparse.ArgumentParser(description="Plot CSI fingerprint amplitude profiles")
    parser.add_argument("--measurement_id", type=int, required=True, help="Measurement ID")
    parser.add_argument("--bssid", type=str, required=True, help="BSSID of the AP")
    parser.add_argument("--window_id", type=int, required=True, help="Window ID to compare with reference")
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


def has_data(profile: np.ndarray, threshold: float = 1e-6) -> bool:
    """Return True if profile contains any value above threshold."""
    return np.any(profile > threshold)


def main():
    args = parse_args()
    with storage.Session() as conn:
        ref_fp = get_reference_fingerprint(conn, args.measurement_id, args.bssid)
        if ref_fp is None:
            print(f"Error: No reference fingerprint found for measurement {args.measurement_id}, BSSID {args.bssid}")
            sys.exit(1)

        test_fp = get_fingerprint_by_window_id(conn, args.window_id, args.bssid)
        if test_fp is None:
            print(f"Error: No fingerprint found for window {args.window_id}, BSSID {args.bssid}")
            sys.exit(1)

        if test_fp["measurement_id"] != args.measurement_id:
            print(f"Warning: Selected fingerprint belongs to measurement {test_fp['measurement_id']}, "
                  f"not {args.measurement_id}. Continuing anyway.")

    # Extract metadata and vectors
    ref_meta = ref_fp.metadata
    test_meta = test_fp["metadata"]

    # Sensor order – must be identical for both fingerprints
    sensor_order = ref_meta.get("sensor_order")
    if not sensor_order:
        sensor_order = ref_fp.sensor_names
    test_sensor_order = test_meta.get("sensor_order", test_fp["sensor_names"])
    if sensor_order != test_sensor_order:
        print("Error: Sensor order mismatch between reference and test fingerprints.")
        print(f"Ref: {sensor_order}")
        print(f"Test: {test_sensor_order}")
        sys.exit(1)

    # Number of subcarriers
    n_subcarriers = ref_meta.get("n_subcarriers")
    if not n_subcarriers:
        vec_len = len(np.frombuffer(ref_fp.vector, dtype=np.complex64))
        n_subcarriers = vec_len // len(sensor_order)
        if vec_len % len(sensor_order) != 0:
            print(f"Warning: Vector length {vec_len} not divisible by number of sensors {len(sensor_order)}")

    # Convert vectors to real arrays
    ref_vec = np.frombuffer(ref_fp.vector, dtype=np.complex64).real
    test_vec = np.frombuffer(test_fp["vector"], dtype=np.complex64).real

    if len(ref_vec) != len(test_vec):
        print(f"Error: Vector length mismatch: ref {len(ref_vec)} vs test {len(test_vec)}")
        sys.exit(1)

    # Split into per‑sensor profiles and keep only those with data
    sensors_with_data = []
    ref_profiles = []
    test_profiles = []
    for idx, sensor in enumerate(sensor_order):
        start = idx * n_subcarriers
        end = start + n_subcarriers
        ref_profile = ref_vec[start:end]
        test_profile = test_vec[start:end]
        if has_data(ref_profile) or has_data(test_profile):
            sensors_with_data.append(sensor)
            ref_profiles.append(ref_profile)
            test_profiles.append(test_profile)

    if not sensors_with_data:
        print("No sensors with data to plot.")
        sys.exit(1)

    # Create figure with one subplot per sensor (only those with data)
    n_sensors = len(sensors_with_data)
    fig, axes = plt.subplots(n_sensors, 1, figsize=(12, 3 * n_sensors), sharex=True)
    if n_sensors == 1:
        axes = [axes]

    subcarrier_indices = np.arange(n_subcarriers)
    width = 0.35

    for idx, sensor in enumerate(sensors_with_data):
        ax = axes[idx]
        ref_profile = ref_profiles[idx]
        test_profile = test_profiles[idx]

        ax.bar(subcarrier_indices - width/2, ref_profile, width,
               label=f"Reference (window {ref_fp.window_id})", color='green', alpha=0.7)
        ax.bar(subcarrier_indices + width/2, test_profile, width,
               label=f"Selected (window {args.window_id})", color='blue', alpha=0.7)

        ax.set_title(f"Sensor: {sensor}")
        ax.set_ylabel("Amplitude")
        ax.legend()
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Subcarrier index")
    fig.suptitle(f"CSI Amplitude Profile Comparison\nBSSID: {args.bssid} | Measurement ID: {args.measurement_id}", fontsize=14)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()